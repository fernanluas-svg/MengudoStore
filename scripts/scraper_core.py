'''scraper_core.py - Camada de raspagem moderna, adaptavel e com evasao anti-bot.

Centraliza a logica de extracao para os scrapers do MengudoStore:

1. FETCH MIMETIZADO (evasao de bot / Cloudflare)
   - Usa curl_cffi com impersonacao de Chrome real (TLS/JA3 + headers de
     navegador, cookie jar de sessao), driblando a maior parte dos bloqueios
     do Cloudflare/Flashscore sem depender de um navegador headless.
   - Fallback automatico para requests com headers mimetizados caso o
     curl_cffi nao esteja disponivel.
   - Retries com backoff + jitter para nao dar timeout sob instabilidade.

2. SELETORES RESILIENTES / ADAPTAVEIS
   - Em vez de confiar em classes CSS fixas (ex.: div.event__match),
     localizamos blocos de partida/odds/escudos por HEURISTICAS DE CONTEUDO:
     presenca do nome do time, de um padrao de placar, de data/hora e de
     imagens de escudo. Assim, se o layout do ge/Flashscore mudar, a extracao
     continua funcionando.
'''

from __future__ import annotations

import random
import re
import time
import unicodedata
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Mimetizacao de navegador real (User-Agents de Chrome estaveis)
# ---------------------------------------------------------------------------

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
]


def _chrome_headers():
    ua = random.choice(USER_AGENTS)
    return {
        'User-Agent': ua,
        'Accept': (
            'text/html,application/xhtml+xml,application/xml;q=0.9,'
            'image/avif,image/webp,image/apng,*/*;q=0.8,'
            'application/signed-exchange;v=b3;q=0.7'
        ),
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'sec-ch-ua': 'Chromium;v=124, Google Chrome;v=124, Not-A.Brand;v=99',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
    }


# ---------------------------------------------------------------------------
# Sessao unica (reaproveita cookies => parece um visitante recorrente)
# ---------------------------------------------------------------------------

_session = None


def _build_session():
    try:
        from curl_cffi import requests as cr
        return cr.Session(impersonate='chrome')
    except Exception:
        import requests as rq
        return rq.Session()


def get_session():
    global _session
    if _session is None:
        _session = _build_session()
    return _session


# ---------------------------------------------------------------------------
# Padroes heuristicos de conteudo (sem backslashes / sem classes CSS fixas)
# ---------------------------------------------------------------------------

# Placar "2 - 1" / "2-1" / "2–1" (hifen ou en-dash). Mascaramos datas antes.
SCORE_RE = re.compile(r'([0-9]{1,2})[ \t]*[–-][ \t]*([0-9]{1,2})')

# Data: dd/mm/yyyy, dd.mm.yyyy, dd-mm-yyyy, ISO yyyy-mm-dd ou "12 de agosto de 2026"
DATE_RE = re.compile(
    r'([0-9]{1,2})[./-]([0-9]{1,2})[./-]([0-9]{2,4})'
    r'|([0-9]{4})-([0-9]{2})-([0-9]{2})'
    r'|([0-9]{1,2})[ \t]+de[ \t]+([a-zçãõéáíúâêô]+)[ \t]+([0-9]{4})',
    re.I,
)

TIME_RE = re.compile(r'([0-9]{1,2}):([0-9]{2})')

# Odds: numeros flutuantes tipicos de casas de apostas (1.01 .. 999.99)
ODD_RE = re.compile(r'([0-9]{1,3}(?:[.][0-9]{2,3})?)')

MESES = {
    'janeiro': 1, 'fevereiro': 2, 'marco': 3, 'março': 3, 'abril': 4,
    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8, 'setembro': 9,
    'outubro': 10, 'novembro': 11, 'dezembro': 12,
}

_IMG_EXT_RE = re.compile(r'[.](svg|png|jpe?g)(?:[?#].*)?$', re.I)
_MEDIA_RE = re.compile(r'(media|img|static|cdn|logo|escudo|shield|crest)', re.I)


# ---------------------------------------------------------------------------
# Normalizacao de texto (acento-insensitive, canonica)
# ---------------------------------------------------------------------------

def normalize(text):
    if not text:
        return ''
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[_-]+', ' ', text)
    text = re.sub(r'[ \t\r\n]+', ' ', text).strip().lower()
    return text


# ---------------------------------------------------------------------------
# Resultado de fetch
# ---------------------------------------------------------------------------

@dataclass
class FetchResult:
    status: int
    text: str
    url: str
    engine: str
    error: Optional[str] = None

    @property
    def ok(self):
        return 200 <= self.status < 300 and bool(self.text)

    def is_challenge(self):
        '''Heuristica: a resposta e uma pagina de desafio (Cloudflare/etc.)?'''
        t = self.text.lower()
        markers = (
            'just a moment', 'checking your browser', 'verify you are human',
            'attention required', 'cf-chl',
        )
        return any(m in t for m in markers) and len(self.text) < 8000


# ---------------------------------------------------------------------------
# FETCH (mimetizado + resiliente ao timeout)
# ---------------------------------------------------------------------------

def fetch(url, timeout=30, retries=3, extra_headers=None, verify=True):
    '''Requisicao com mimetizacao de Chrome real (TLS/JA3 spoofing).

    Tenta curl_cffi (impersonate=chrome). Em caso de erro, refaz com
    backoff exponencial + jitter. Nunca lanca excecao: retorna FetchResult
    com status 0 / erro preenchido.
    '''
    session = get_session()
    headers = _chrome_headers()
    if extra_headers:
        headers.update(extra_headers)

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(
                url, headers=headers, timeout=timeout, verify=verify,
                allow_redirects=True,
            )
            engine = 'curl_cffi' if 'curl_cffi' in type(session).__module__ else 'requests'
            result = FetchResult(resp.status_code, resp.text, resp.url, engine)
            if result.ok and not result.is_challenge():
                return result
            if result.is_challenge():
                last_err = 'Cloudflare/interactive challenge detectado'
                headers = _chrome_headers()
                time.sleep(random.uniform(1.0, 2.0) * attempt)
                continue
            return result
        except Exception as e:  # noqa: BLE001
            last_err = f'{type(e).__name__}: {e}'
            time.sleep(random.uniform(0.5, 1.5) * attempt)
    return FetchResult(0, '', url, 'error', last_err)


def fetch_json(url, timeout=30, retries=3):
    '''Atalho para endpoints JSON (ex.: API de tabela do GE).'''
    import json as _json
    res = fetch(url, timeout=timeout, retries=retries,
                extra_headers={'Accept': 'application/json, text/plain, */*'})
    if not res.ok:
        return None
    try:
        return _json.loads(res.text)
    except Exception:
        return None


def download(url, timeout=30, retries=2):
    '''Baixa conteudo binario (ex.: escudos) com a mesma mimetizacao.
    Retorna (status, content_bytes, engine). Nunca lanca excecao.'''
    session = get_session()
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, headers=_chrome_headers(), timeout=timeout)
            if 200 <= resp.status_code < 300:
                return resp.status_code, resp.content, 'curl_cffi' if 'curl_cffi' in type(session).__module__ else 'requests'
        except Exception as e:  # noqa: BLE001
            last_err = f'{type(e).__name__}: {e}'
            time.sleep(random.uniform(0.5, 1.0) * attempt)
    return 0, b'', f'error:{last_err}'


# ---------------------------------------------------------------------------
# Extracao adaptavel de placar / data / hora
# ---------------------------------------------------------------------------

def extract_scores(text):
    '''Extrai o placar (home, away) a partir de qualquer texto.'''
    cleaned = DATE_RE.sub(' ', text or '')
    cleaned = TIME_RE.sub(' ', cleaned)
    m = SCORE_RE.search(cleaned)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def extract_datetime(text):
    '''Retorna ISO (America/Sao_Paulo) ou None a partir de padroes de data/hora.'''
    if not text:
        return None
    m = DATE_RE.search(text)
    if not m:
        return None
    dia = mes = ano = None
    if m.group(1):
        dia, mes, ano = int(m.group(1)), int(m.group(2)), int(m.group(3))
    elif m.group(4):
        ano, mes, dia = int(m.group(4)), int(m.group(5)), int(m.group(6))
    else:
        mes = MESES.get(normalize(m.group(8)), 0)
        if mes:
            dia, ano = int(m.group(7)), int(m.group(9))
    if not (dia and mes and ano):
        return None
    if ano < 100:
        ano += 2000
    hora = '00:00'
    mt = TIME_RE.search(text)
    if mt:
        hora = f'{mt.group(1)}:{mt.group(2)}'
    return f'{ano}-{mes:02d}-{dia:02d}T{hora}:00-03:00'


# ---------------------------------------------------------------------------
# Extracao adaptavel de blocos de partida (sem classes CSS fixas)
# ---------------------------------------------------------------------------

# Tags que costumam envolver um bloco de partida (evita casar html/body)
CONTAINER_TAGS = {
    'div', 'section', 'li', 'tr', 'article', 'a', 'ul', 'ol', 'table', 'tbody',
}


def find_match_rows(soup, team_norm, max_chars=300):
    '''Retorna elementos cujo texto conteem o time alvo E um placar ou data.

    Nao depende de classe CSS especifica: funciona mesmo que o Flashscore/ge
    mudem os nomes das divs, contanto que o conteudo (time + data/placar)
    permaneça no mesmo bloco de texto. Descarta tags ancestors para evitar
    duplicatas (fica com o bloco mais interno / especifico).
    '''
    cands = []
    for tag in soup.find_all(CONTAINER_TAGS):
        txt = tag.get_text(' ', strip=True)
        if not txt or len(txt) > max_chars:
            continue
        if team_norm not in normalize(txt):
            continue
        if not (SCORE_RE.search(txt) or DATE_RE.search(txt) or TIME_RE.search(txt)):
            continue
        cands.append(tag)

    rows = []
    seen = set()
    for c in cands:
        # pula se for ancestor de outro candidato (mantem o mais interno)
        if any(c is not other and c in other.parents for other in cands):
            continue
        key = c.get_text(' ', strip=True)
        if key in seen:
            continue
        seen.add(key)
        rows.append(c)
    return rows


def extract_opponent(row_text, team_norm, known_teams):
    '''Descobre o adversario a partir do texto de uma linha de partida.

    known_teams: conjunto de nomes canonicos (normalizados) dos times.
    '''
    txt_norm = normalize(row_text)
    # procura qualquer time conhecido que nao seja o proprio
    for t in known_teams:
        if t and t != team_norm and t in txt_norm:
            return t
    # fallback: remove o time alvo, datas, placares e pontuacao; sobra o adversario
    rest = txt_norm.replace(team_norm, ' ')
    rest = DATE_RE.sub(' ', rest)
    rest = TIME_RE.sub(' ', rest)
    rest = SCORE_RE.sub(' ', rest)
    rest = re.sub(r'[^a-z0-9 ]', ' ', rest)
    rest = re.sub(r'[ \t]+', ' ', rest).strip()
    tokens = [r for r in rest.split(' ') if len(r) > 2]
    return tokens[0] if tokens else None


# ---------------------------------------------------------------------------
# Extracao adaptavel de odds (1X2)
# ---------------------------------------------------------------------------

def find_odds_rows(soup):
    '''Localiza linhas de odds por conteudo: 3 numeros decimais + casa.

    Funciona independente da classe da tabela (ui-table, wcl-*, etc.).
    '''
    from bs4 import BeautifulSoup
    found = []
    for tag in soup.find_all(True):
        txt = tag.get_text(' ', strip=True)
        if not txt or len(txt) > 400:
            continue
        numbers = [float(n) for n in ODD_RE.findall(txt)
                   if 1.0 < float(n) < 1000.0]
        if len(numbers) >= 3:
            found.append((tag, numbers, txt))
    return found


# ---------------------------------------------------------------------------
# Extracao adaptavel de escudos (imagens)
# ---------------------------------------------------------------------------

def _is_image_src(src):
    if not src:
        return False
    if _IMG_EXT_RE.search(src):
        return True
    return bool(_MEDIA_RE.search(src)) and ('http' in src or src.startswith('/'))


def find_shield(soup, team_name):
    '''Encontra a URL do escudo de um time por heurística de conteudo.

    Procura <img> cujo alt/title bate (exato ou parcial) com o nome do time e
    cujo src parece um escudo. Tambem inspecta background-image em style e
    atributos data-src/data-lazy-src (comum em lazy loading).
    '''
    target = normalize(team_name)
    if not target:
        return None

    imgs = soup.find_all('img')
    # 1) alt exato + imagem
    for img in imgs:
        alt = normalize(img.get('alt') or '')
        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or ''
        if alt == target and _is_image_src(src):
            return src
    # 2) alt parcial + imagem
    for img in imgs:
        alt = normalize(img.get('alt') or '')
        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or ''
        if target and target in alt and _is_image_src(src):
            return src
    # 3) title/alt parcial em qualquer tag com background-image
    for tag in soup.find_all(True):
        style = tag.get('style') or ''
        sm = re.search(r'url\(([^)]+)\)', style)
        if not sm:
            continue
        src = sm.group(1).strip('\'"')
        alt = normalize(tag.get('alt') or tag.get('title') or '')
        if target and target in alt and _is_image_src(src):
            return src
    return None
