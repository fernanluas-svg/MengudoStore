import json
import os
import re
import unicodedata
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '../src/data')
PUBLIC_DIR = os.path.join(BASE_DIR, '../public')
ESCUDOS_DIR = os.path.join(PUBLIC_DIR, 'escudos')
MAPA_PATH = os.path.join(DATA_DIR, 'mapa_escudos.json')

GE_LIBERTADORES_URL = 'https://ge.globo.com/futebol/libertadores/'
HEADERS = {
    'User-Agent': 'MengudoStoreBot/1.0 (busca automatizada de escudos; contato@mengudostore.com)'
}

# Ordem de prioridade das fontes (conforme definido para o projeto).
PRIORIDADE_FONTES = ['ge', 'flashscore', 'bolavip', 'betfair', 'sportingbet']

CAMINHOS_CHROME = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
    os.path.join(os.environ.get('PROGRAMFILES', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
]


def localizar_chrome():
    """Tenta localizar o executável do Chrome em caminhos alternativos do
    Windows. Retorna o caminho encontrado ou None (Selenium usará o padrão)."""
    for caminho in CAMINHOS_CHROME:
        if caminho and os.path.isfile(caminho):
            return caminho
    return None


def log(nivel, mensagem):
    print(f'[{nivel}] {mensagem}')


def normalizar(texto):
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[_-]+', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip().lower()
    return texto


def slugificar(texto):
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.lower()
    texto = re.sub(r'[^a-z0-9]+', '-', texto)
    return texto.strip('-')


# ---------------------------------------------------------------------------
# Coleta de times a partir dos JSONs de dados
# ---------------------------------------------------------------------------

def _carregar(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def coletar_times():
    """Retorna um conjunto com os nomes de exibição dos clubes encontrados
    nos três JSONs de dados."""
    times = set()

    for arquivo in ('nextMatch.json', 'matches.json'):
        dados = _carregar(os.path.join(DATA_DIR, arquivo))
        if isinstance(dados, list):
            for m in dados:
                op = m.get('opponent')
                if op:
                    times.add(op)

    lib = _carregar(os.path.join(DATA_DIR, 'libertadores.json'))
    if isinstance(lib, dict):
        for c in lib.get('confrontos', []):
            for chave in ('timeA', 'timeB'):
                if c.get(chave):
                    times.add(c[chave])
            for leg in ('ida', 'volta'):
                leg_dados = c.get(leg) or {}
                for lado in ('casa', 'fora'):
                    if leg_dados.get(lado):
                        times.add(leg_dados[lado])

    cl = _carregar(os.path.join(DATA_DIR, 'classificacaoLibertadores.json'))
    if isinstance(cl, list):
        for g in cl:
            for t in g.get('classificacao', []):
                if t.get('time'):
                    times.add(t['time'])

    times.discard('A definir')
    times.add('Flamengo')
    return times


def coletar_logos_existentes():
    """Mapeia time -> URL de escudo remoto já presente em nextMatch/matches."""
    logos = {}
    for arquivo in ('nextMatch.json', 'matches.json'):
        dados = _carregar(os.path.join(DATA_DIR, arquivo))
        if isinstance(dados, list):
            for m in dados:
                op = m.get('opponent')
                logo = m.get('opponentLogo')
                if op and isinstance(logo, str) and logo.startswith('http'):
                    logos[op] = logo
    return logos


# ---------------------------------------------------------------------------
# Busca de escudos (Selenium como primário, HTTP como fallback leve)
# ---------------------------------------------------------------------------

_GE_HTML_CACHE = None
_SELENIUM_INDISPONIVEL = False


def _html_ge_libertadores():
    global _GE_HTML_CACHE
    if _GE_HTML_CACHE is None:
        try:
            r = requests.get(GE_LIBERTADORES_URL, headers=HEADERS, timeout=30)
            r.raise_for_status()
            _GE_HTML_CACHE = r.text
        except Exception as e:
            log('WARN', f'Falha ao baixar página do GE: {e}')
            _GE_HTML_CACHE = ''
    return _GE_HTML_CACHE


def _buscar_ge_html(nome):
    """Extrai o escudo de um time a partir dos <img alt="Time" src="...">
    embutidos na página da Libertadores do GE."""
    html = _html_ge_libertadores()
    if not html:
        return None
    soup = BeautifulSoup(html, 'html.parser')
    alvo = normalizar(nome)

    def _candidatos(pred):
        resultado = []
        for img in soup.find_all('img'):
            alt = normalizar(img.get('alt') or '')
            src = img.get('src') or ''
            if pred(alt) and 's.sde.globo.com/media/' in src:
                resultado.append(src)
        return resultado

    # 1) correspondência exata no alt (preferindo SVG)
    for cand in _candidatos(lambda a: a == alvo):
        if cand.lower().endswith('.svg'):
            return cand
    for cand in _candidatos(lambda a: a == alvo):
        return cand
    # 2) correspondência parcial (ex.: "Cusco" em "Cusco FC")
    for cand in _candidatos(lambda a: alvo and alvo in a):
        if cand.lower().endswith('.svg'):
            return cand
    for cand in _candidatos(lambda a: alvo and alvo in a):
        return cand
    return None


def _buscar_site_generico(nome, url_template):
    """Best-effort: busca o escudo em um site de apostas/notícias via HTTP.
    Retorna a URL da imagem ou None."""
    try:
        url = url_template.format(query=requests.utils.quote(nome))
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        alvo = normalizar(nome)
        # 1) img cujo alt bate com o time e parece um escudo
        for img in soup.find_all('img'):
            alt = normalizar(img.get('alt') or '')
            src = img.get('src') or ''
            eh_imagem = bool(re.search(r'\.(svg|png|jpg|jpeg)$', src, re.I))
            eh_escudo = bool(re.search(r'(logo|shield|escudo|crest|badge)', src, re.I))
            if alt == alvo and eh_imagem and eh_escudo:
                return src
        # 2) qualquer img de escudo próxima do nome
        for img in soup.find_all('img'):
            src = img.get('src') or ''
            if re.search(r'(logo|shield|escudo|crest|badge)', src, re.I) and re.search(r'\.(svg|png|jpg|jpeg)$', src, re.I):
                return src
    except Exception:
        return None
    return None


def _buscar_escudo_selenium(nome):
    """Fonte primária: Selenium/Chrome. Retorna URL ou None quando o navegador
    não está disponível ou a busca falha."""
    global _SELENIUM_INDISPONIVEL
    if _SELENIUM_INDISPONIVEL:
        return None
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from bs4 import BeautifulSoup
    except Exception as e:
        log('WARN', f'Dependencias de Selenium indisponiveis: {type(e).__name__}')
        return None

    try:
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('useAutomationExtension', False)
        chrome = localizar_chrome()
        if chrome:
            options.binary_location = chrome
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        _SELENIUM_INDISPONIVEL = True
        log('WARN', f'Navegador indisponivel para Selenium: {type(e).__name__}')
        return None

    try:
        driver.get(f'https://www.flashscore.com/search/?q={requests.utils.quote(nome)}')
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.searchElem'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        alvo = normalizar(nome)
        for img in soup.find_all('img'):
            alt = normalizar(img.get('alt') or '')
            src = img.get('src') or ''
            if alt == alvo and 'media' in src:
                return src
    except Exception as e:
        log('WARN', f'Falha na busca via Selenium: {type(e).__name__}')
        return None
    finally:
        try:
            driver.quit()
        except Exception:
            pass
    return None


def obter_url_escudo(nome):
    """Tenta, na ordem de prioridade, obter a URL do escudo do time."""
    # Selenium (Flashscore) como fonte primária
    url = _buscar_escudo_selenium(nome)
    if url:
        return url, 'flashscore (selenium)'

    # Fallback leve HTTP, respeitando a prioridade das fontes
    buscas = {
        'ge': lambda: _buscar_ge_html(nome),
        'flashscore': lambda: _buscar_site_generico(nome, 'https://www.flashscore.com/search/?q={query}'),
        'bolavip': lambda: _buscar_site_generico(nome, 'https://www.bolavip.com/br/search?q={query}'),
        'betfair': lambda: _buscar_site_generico(nome, 'https://www.betfair.com/sport/football?q={query}'),
        'sportingbet': lambda: _buscar_site_generico(nome, 'https://www.sportingbet.com/br/sports/futebol?q={query}'),
    }
    for fonte in PRIORIDADE_FONTES:
        try:
            url = buscas[fonte]()
        except Exception:
            url = None
        if url:
            return url, fonte
    return None, None


# ---------------------------------------------------------------------------
# Download e persistência
# ---------------------------------------------------------------------------

def _extensao(url):
    m = re.search(r'\.(svg|png|jpg|jpeg)(?:[?#].*)?$', url, re.I)
    return (m.group(1).lower() if m else 'png')


def baixar_escudo(nome, url):
    """Baixa o escudo para public/escudos e retorna o caminho público."""
    os.makedirs(ESCUDOS_DIR, exist_ok=True)
    ext = _extensao(url)
    arquivo = f'{slugificar(nome)}.{ext}'
    destino = os.path.join(ESCUDOS_DIR, arquivo)
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        with open(destino, 'wb') as f:
            f.write(r.content)
        return f'/escudos/{arquivo}'
    except Exception as e:
        log('WARN', f'Falha ao baixar escudo de {nome}: {e}')
        return None


def carregar_mapa():
    return _carregar(MAPA_PATH) or {}


def salvar_mapa(mapa):
    os.makedirs(os.path.dirname(MAPA_PATH), exist_ok=True)
    with open(MAPA_PATH, 'w', encoding='utf-8') as f:
        json.dump(mapa, f, ensure_ascii=False, indent=2)
    log('SUCCESS', f'Mapa de escudos salvo em: {MAPA_PATH}')


def atualizar_jsons(mapa):
    """Atribui os escudos baixados aos respectivos clubes nos JSONs de dados."""
    # nextMatch.json e matches.json: opponentLogo
    for arquivo in ('nextMatch.json', 'matches.json'):
        caminho = os.path.join(DATA_DIR, arquivo)
        dados = _carregar(caminho)
        if not isinstance(dados, list):
            continue
        for m in dados:
            op = m.get('opponent')
            if op and mapa.get(op):
                m['opponentLogo'] = mapa[op]
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        log('SUCCESS', f'Escudos atribuídos em: {caminho}')

    # classificacaoLibertadores.json: campo "escudo" por time
    caminho = os.path.join(DATA_DIR, 'classificacaoLibertadores.json')
    cl = _carregar(caminho)
    if isinstance(cl, list):
        for g in cl:
            for t in g.get('classificacao', []):
                if t.get('time') and mapa.get(t['time']):
                    t['escudo'] = mapa[t['time']]
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(cl, f, ensure_ascii=False, indent=2)
        log('SUCCESS', f'Escudos atribuídos em: {caminho}')

    # libertadores.json: escudo do confronto e das pernas ida/volta
    caminho = os.path.join(DATA_DIR, 'libertadores.json')
    lib = _carregar(caminho)
    if isinstance(lib, dict):
        for c in lib.get('confrontos', []):
            if c.get('timeB') and mapa.get(c['timeB']):
                c['escudo'] = mapa[c['timeB']]
            for leg in ('ida', 'volta'):
                leg_dados = c.get(leg) or {}
                for lado in ('casa', 'fora'):
                    chave = leg_dados.get(lado)
                    if chave and mapa.get(chave):
                        leg_dados[f'{lado}Escudo'] = mapa[chave]
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(lib, f, ensure_ascii=False, indent=2)
        log('SUCCESS', f'Escudos atribuídos em: {caminho}')


def main():
    log('INFO', 'Iniciando busca automatizada de escudos...')
    mapa = carregar_mapa()
    times = coletar_times()
    log('INFO', f'{len(times)} time(s) coletado(s) dos JSONs de dados.')
    logos_existentes = coletar_logos_existentes()

    novos = 0
    for nome in sorted(times):
        # já possui escudo local?
        if mapa.get(nome) or mapa.get(normalizar(nome)):
            continue
        # caminho rápido: reutiliza escudo remoto já conhecido (ex.: globo)
        if logos_existentes.get(nome) and logos_existentes[nome].startswith('http'):
            url, fonte = logos_existentes[nome], 'logo existente (globo)'
        else:
            url, fonte = obter_url_escudo(nome)
        if not url:
            log('WARN', f'Nenhum escudo encontrado para: {nome}')
            continue
        caminho_local = baixar_escudo(nome, url)
        if not caminho_local:
            continue
        mapa[nome] = caminho_local
        mapa[normalizar(nome)] = caminho_local
        novos += 1
        log('SUCCESS', f'Escudo de {nome} obtido via {fonte}.')

    salvar_mapa(mapa)
    atualizar_jsons(mapa)
    log('INFO', f'Busca concluída. {novos} novo(s) escudo(s) adicionado(s).')


if __name__ == '__main__':
    main()
