import json
import os
import re
import sys
import unicodedata
import urllib.parse as _up
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scraper_core as sc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '../src/data')
PUBLIC_DIR = os.path.join(BASE_DIR, '../public')
ESCUDOS_DIR = os.path.join(PUBLIC_DIR, 'escudos')
MAPA_PATH = os.path.join(DATA_DIR, 'mapa_escudos.json')

GE_LIBERTADORES_URL = 'https://ge.globo.com/futebol/libertadores/'

# Ordem de prioridade das fontes (conforme definido para o projeto).
PRIORIDADE_FONTES = ['ge', 'flashscore', 'bolavip', 'betfair', 'sportingbet']


def log(nivel, mensagem):
    print(f'[{nivel}] {mensagem}')


def normalizar(texto):
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[_-]+', ' ', texto)
    texto = re.sub(r'[ \t\r\n]+', ' ', texto).strip().lower()
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

    car = _carregar(os.path.join(DATA_DIR, 'carioca.json'))
    if isinstance(car, list):
        for t in car:
            if t.get('time'):
                times.add(t['time'])
    elif isinstance(car, dict):
        for t in car.get('classificacao', []):
            if t.get('time'):
                times.add(t['time'])

    cdb = _carregar(os.path.join(DATA_DIR, 'copaDoBrasil.json'))
    if isinstance(cdb, dict):
        for c in cdb.get('confrontos', []):
            for chave in ('timeA', 'timeB'):
                if c.get(chave):
                    times.add(c[chave])
            for leg in ('ida', 'volta'):
                leg_dados = c.get(leg) or {}
                for lado in ('casa', 'fora'):
                    if leg_dados.get(lado):
                        times.add(leg_dados[lado])

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

    cdb = _carregar(os.path.join(DATA_DIR, 'copaDoBrasil.json'))
    if isinstance(cdb, dict):
        for c in cdb.get('confrontos', []):
            for chave in ('timeA', 'timeB'):
                nome = c.get(chave)
                logo = c.get('escudo')
                if nome and isinstance(logo, str) and logo.startswith('http'):
                    logos[nome] = logo
            for leg in ('ida', 'volta'):
                leg_dados = c.get(leg) or {}
                for lado in ('casa', 'fora'):
                    chave = leg_dados.get(lado)
                    logo = leg_dados.get(f'{lado}Escudo')
                    if chave and isinstance(logo, str) and logo.startswith('http'):
                        logos[chave] = logo
    return logos


# ---------------------------------------------------------------------------
# Busca de escudos (fetch mimetizado + seletor adaptável de imagem)
# ---------------------------------------------------------------------------

_GE_HTML_CACHE = None


def _html_ge_libertadores():
    global _GE_HTML_CACHE
    if _GE_HTML_CACHE is None:
        res = sc.fetch(GE_LIBERTADORES_URL, timeout=30, retries=3)
        if res.ok:
            _GE_HTML_CACHE = res.text
        else:
            _GE_HTML_CACHE = ''
            log('WARN', f'Falha ao baixar página do GE: {res.error}')
    return _GE_HTML_CACHE


def _buscar_ge_html(nome):
    """Extrai o escudo de um time a partir da página da Libertadores do GE,
    usando seletor adaptável (alt/title + src de imagem)."""
    html = _html_ge_libertadores()
    if not html:
        return None
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')
    except Exception:
        return None
    return sc.find_shield(soup, nome)


def _buscar_site_generico(nome, url_template):
    """Best-effort: busca o escudo em um site de apostas/notícias via HTTP
    mimetizado, com seletor adaptável de imagem. Retorna URL ou None."""
    try:
        url = url_template.format(query=_up.quote(nome))
        res = sc.fetch(url, timeout=20, retries=2)
        if not res.ok:
            return None
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'lxml')
        return sc.find_shield(soup, nome)
    except Exception:
        return None


def _buscar_flashscore_shield(nome):
    """Fonte primária: Flashscore via fetch mimetizado + find_shield adaptável."""
    try:
        url = 'https://www.flashscore.com/search/?q=' + _up.quote(nome)
        res = sc.fetch(url, timeout=20, retries=2)
        if not res.ok:
            return None
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'lxml')
        return sc.find_shield(soup, nome)
    except Exception:
        return None


def obter_url_escudo(nome):
    """Tenta, na ordem de prioridade, obter a URL do escudo do time."""
    # Flashscore (fetch mimetizado) como fonte primária
    try:
        url = _buscar_flashscore_shield(nome)
    except Exception:
        url = None
    if url:
        return url, 'flashscore (curl_cffi)'

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
    m = re.search(r'[.](svg|png|jpe?g)(?:[?#].*)?$', url, re.I)
    return (m.group(1).lower() if m else 'png')


def baixar_escudo(nome, url):
    """Baixa o escudo para public/escudos e retorna o caminho público."""
    os.makedirs(ESCUDOS_DIR, exist_ok=True)
    ext = _extensao(url)
    arquivo = f'{slugificar(nome)}.{ext}'
    destino = os.path.join(ESCUDOS_DIR, arquivo)
    try:
        status, content, engine = sc.download(url, timeout=30, retries=2)
        if status and content:
            with open(destino, 'wb') as f:
                f.write(content)
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

    # carioca.json: campo "escudo" por time (aceita lista ou objeto com classificacao)
    caminho = os.path.join(DATA_DIR, 'carioca.json')
    car = _carregar(caminho)
    if isinstance(car, list):
        for t in car:
            if t.get('time') and mapa.get(t['time']):
                t['escudo'] = mapa[t['time']]
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(car, f, ensure_ascii=False, indent=2)
        log('SUCCESS', f'Escudos atribuídos em: {caminho}')
    elif isinstance(car, dict):
        for t in car.get('classificacao', []):
            if t.get('time') and mapa.get(t['time']):
                t['escudo'] = mapa[t['time']]
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(car, f, ensure_ascii=False, indent=2)
        log('SUCCESS', f'Escudos atribuídos em: {caminho}')

    # copaDoBrasil.json: escudo do confronto e das pernas ida/volta
    caminho = os.path.join(DATA_DIR, 'copaDoBrasil.json')
    cdb = _carregar(caminho)
    if isinstance(cdb, dict):
        for c in cdb.get('confrontos', []):
            if c.get('timeB') and mapa.get(c['timeB']):
                c['escudo'] = mapa[c['timeB']]
            for leg in ('ida', 'volta'):
                leg_dados = c.get(leg) or {}
                for lado in ('casa', 'fora'):
                    chave = leg_dados.get(lado)
                    if chave and mapa.get(chave):
                        leg_dados[f'{lado}Escudo'] = mapa[chave]
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(cdb, f, ensure_ascii=False, indent=2)
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
