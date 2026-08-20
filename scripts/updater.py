import json
import os
import re
import unicodedata

import requests
from bs4 import BeautifulSoup


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, '../src/data/nextMatch.json')
WIKIPEDIA_URL = 'https://pt.wikipedia.org/wiki/Temporada_do_Clube_de_Regatas_do_Flamengo_de_2026'
BOLAVIP_URL = 'https://br.bolavip.com/flamengo/confira-todos-os-jogos-do-flamengo-no-brasileirao-2026-rodada-a-rodada'
HEADERS = {
    'User-Agent': 'MengudoStoreBot/1.0 (automação da agenda de jogos; contato@mengudostore.com)'
}
BOLAVIP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8'
}


def log(nivel, mensagem):
    print(f'[{nivel}] {mensagem}')


def fetch_and_format_matches():
    matches_data = [
      {"id": "2026-08-22-cruzeiro", "opponent": "Cruzeiro", "opponentLogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Cruzeiro_Esporte_Clube_%28logo%29.svg/330px-Cruzeiro_Esporte_Clube_%28logo%29.svg.png", "isHome": False, "date": "2026-08-22T20:30:00-03:00", "stadium": "Mineirão - Belo Horizonte, MG", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-08-30-botafogo", "opponent": "Botafogo", "opponentLogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Botafogo_de_Futebol_e_Regatas_logo.svg/330px-Botafogo_de_Futebol_e_Regatas_logo.svg.png", "isHome": True, "date": "2026-08-30T16:00:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-09-06-remo", "opponent": "Remo", "opponentLogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Clube_do_Remo.svg/330px-Clube_do_Remo.svg.png", "isHome": False, "date": "2026-09-06T16:00:00-03:00", "stadium": "Baenão - Belém, PA", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-09-12-corinthians", "opponent": "Corinthians", "opponentLogo": "https://upload.wikimedia.org/wikipedia/pt/thumb/b/b4/Corinthians_simbolo.png/330px-Corinthians_simbolo.png", "isHome": True, "date": "2026-09-12T16:00:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-09-19-red-bull-bragantino", "opponent": "Red Bull Bragantino", "opponentLogo": "https://upload.wikimedia.org/wikipedia/pt/thumb/9/9e/RedBullBragantino.png/330px-RedBullBragantino.png", "isHome": True, "date": "2026-09-19T16:00:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-10-07-santos", "opponent": "Santos", "opponentLogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Santos_Futebol_Clube_logo_%28with_stars_and_crown%29.png/330px-Santos_Futebol_Clube_logo_%28with_stars_and_crown%29.png", "isHome": False, "date": "2026-10-07T21:30:00-03:00", "stadium": "Vila Belmiro - Santos, SP", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-10-10-fluminense", "opponent": "Fluminense", "opponentLogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Fluminense_Football_Club.svg/330px-Fluminense_Football_Club.svg.png", "isHome": True, "date": "2026-10-10T16:00:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-10-17-bahia", "opponent": "Bahia", "opponentLogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Esporte_Clube_Bahia_logo.svg/330px-Esporte_Clube_Bahia_logo.svg.png", "isHome": False, "date": "2026-10-17T16:00:00-03:00", "stadium": "Arena Fonte Nova - Salvador, BA", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-10-24-atletico-mineiro", "opponent": "Atlético Mineiro", "opponentLogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Logo_of_Clube_Atl%C3%A9tico_Mineiro.svg/330px-Logo_of_Clube_Atl%C3%A9tico_Mineiro.svg.png", "isHome": True, "date": "2026-10-24T16:00:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-10-28-vasco-da-gama", "opponent": "Vasco da Gama", "opponentLogo": "https://upload.wikimedia.org/wikipedia/pt/thumb/8/8b/EscudoDoVascoDaGama.svg/330px-EscudoDoVascoDaGama.svg.png", "isHome": False, "date": "2026-10-28T21:30:00-03:00", "stadium": "São Januário - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-11-04-gremio", "opponent": "Grêmio", "opponentLogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Gremio_logo.svg/330px-Gremio_logo.svg.png", "isHome": True, "date": "2026-11-04T21:30:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-11-18-athletico-paranaense", "opponent": "Athletico Paranaense", "opponentLogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Athletico_Paranaense_%28Logo_2019%29.svg/330px-Athletico_Paranaense_%28Logo_2019%29.svg.png", "isHome": True, "date": "2026-11-18T21:30:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-11-21-palmeiras", "opponent": "Palmeiras", "opponentLogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/SE_Palmeiras_2025_crest.png/330px-SE_Palmeiras_2025_crest.png", "isHome": False, "date": "2026-11-21T16:00:00-03:00", "stadium": "Allianz Parque - São Paulo, SP", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-11-28-coritiba", "opponent": "Coritiba", "opponentLogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Coritiba_Foot_Ball_Club_logo.svg/330px-Coritiba_Foot_Ball_Club_logo.svg.png", "isHome": False, "date": "2026-11-28T16:00:00-03:00", "stadium": "Couto Pereira - Curitiba, PR", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-12-02-chapecoense", "opponent": "Chapecoense", "opponentLogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Logo_Associa%C3%A7%C3%A3o_Chapecoense_de_Futebol.svg/330px-Logo_Associa%C3%A7%C3%A3o_Chapecoense_de_Futebol.svg.png", "isHome": True, "date": "2026-12-02T21:30:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None}
    ]
    return matches_data


ALIASES_EQUIPES = {
    'atletico': 'atletico mineiro',
    'atletico mg': 'atletico mineiro',
    'athletico': 'atletico paranaense',
    'athletico pr': 'atletico paranaense',
    'athletico paranaense': 'atletico paranaense',
    'vasco': 'vasco da gama',
}

EQUIPES_SERIE_A = {
    'sao paulo', 'flamengo', 'internacional', 'vitoria', 'mirassol',
    'cruzeiro', 'botafogo', 'remo', 'corinthians', 'red bull bragantino',
    'santos', 'fluminense', 'bahia', 'atletico mineiro', 'vasco da gama',
    'gremio', 'atletico paranaense', 'palmeiras', 'coritiba', 'chapecoense',
}


def normalizar(texto):
    """Remove acentos, padroniza e expande apelidos para nomes canônicos."""
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[_-]+', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip().lower()
    if texto in ALIASES_EQUIPES:
        texto = ALIASES_EQUIPES[texto]
    texto = texto.replace('athletico', 'atletico')
    return texto


def obter_resultados_brasileirao():
    """
    Fonte primária: raspa a página "Temporada do Flamengo 2026" na Wikipédia.
    Retorna um dicionário {(mandante_normalizado, visitante_normalizado): placar_texto}.
    """
    resp = requests.get(WIKIPEDIA_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    cabecalho = None
    for h in soup.find_all('h3'):
        if h.get_text(strip=True) == 'Campeonato Brasileiro':
            cabecalho = h
            break
    if cabecalho is None:
        raise RuntimeError('Seção "Campeonato Brasileiro" não encontrada na página.')

    resultados = {}
    for tabela in soup.find_all('table'):
        if tabela.find_previous('h3') is not cabecalho:
            continue
        linhas = tabela.find_all('tr')
        if not linhas:
            continue
        celulas = linhas[0].find_all(['td', 'th'])
        if len(celulas) < 4:
            continue
        mandante = normalizar(celulas[1].get_text(' ', strip=True))
        visitante = normalizar(celulas[3].get_text(' ', strip=True))
        placar = celulas[2].get_text(' ', strip=True)
        if mandante and visitante:
            resultados[(mandante, visitante)] = placar

    if not resultados:
        raise RuntimeError('Nenhuma rodada encontrada na página.')
    return resultados


def obter_resultados_fallback():
    """
    Fonte secundária: raspa o portal esportivo Bolavip, que lista as 38 rodadas
    do Flamengo no Brasileirão 2026 no formato "Rodada N (datas): Casa x Visitante".
    Retorna o mesmo formato da fonte primária, com placar quando disponível.
    """
    resp = requests.get(BOLAVIP_URL, headers=BOLAVIP_HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    texto = soup.get_text(' ', strip=True)

    resultados = {}
    for trecho in re.split(r'(?=Rodada\s+\d+)', texto):
        m = re.match(r'Rodada\s+\d+.*?:\s*(.*)$', trecho, re.S)
        if not m:
            continue
        corpo = m.group(1)
        for palavra in (' publicidade ', ' leia tambem ', ' veja tambem ', ' receba as ultimas '):
            idx = corpo.lower().find(palavra)
            if idx >= 0:
                corpo = corpo[:idx]
        if 'x' not in corpo.lower():
            continue

        placar = '–'
        sm = re.search(r'(\d{1,2})\s*[xX]\s*(\d{1,2})', corpo)
        if sm:
            placar = f'{sm.group(1)} – {sm.group(2)}'
            corpo = corpo.replace(sm.group(0), ' x ')

        partes = [normalizar(p) for p in re.split(r'\s*x\s*', corpo, flags=re.I) if p.strip()]
        if len(partes) >= 2 and partes[0] in EQUIPES_SERIE_A and partes[1] in EQUIPES_SERIE_A:
            resultados[(partes[0], partes[1])] = placar

    if not resultados:
        raise RuntimeError('Nenhuma rodada encontrada no Bolavip.')
    return resultados


def chave_partida(partida):
    """Retorna a chave (mandante, visitante) esperada para uma partida da agenda."""
    mandante = normalizar('Flamengo' if partida['isHome'] else partida['opponent'])
    visitante = normalizar(partida['opponent'] if partida['isHome'] else 'Flamengo')
    return (mandante, visitante)


def atualizar_placares(matches):
    """Atualiza status e placares usando a Wikipédia; em caso de falha, usa o Bolavip."""
    resultados = None
    origem = 'Wikipedia'
    try:
        resultados = obter_resultados_brasileirao()
        cobertura = sum(1 for p in matches if chave_partida(p) in resultados)
        if cobertura == 0:
            log('WARN', 'Fonte primária não encontrou nenhum jogo da agenda.')
            resultados = None
    except Exception as e:
        log('WARN', f'Fonte primária indisponível: {e}')
        resultados = None

    if resultados is None:
        origem = 'Bolavip'
        try:
            resultados = obter_resultados_fallback()
            log('INFO', f'Fallback (Bolavip) ativado: {len(resultados)} rodada(s) encontrada(s).')
        except Exception as e:
            log('ERROR', f'Fonte secundária indisponível: {e}')
            return matches

    atualizadas = 0
    for partida in matches:
        placar = resultados.get(chave_partida(partida))
        if not placar:
            continue
        m = re.search(r'(\d+)\s*[–-]\s*(\d+)', placar)
        if not m:
            continue
        partida['status'] = 'FINISHED'
        partida['homeScore'] = int(m.group(1))
        partida['awayScore'] = int(m.group(2))
        atualizadas += 1

    log('SUCCESS', f'Placar confirmado para {atualizadas} partida(s) via {origem}.')
    return matches


def save_json(data):
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log('SUCCESS', f'Agenda atualizada em: {JSON_PATH}')


if __name__ == "__main__":
    log('INFO', 'Iniciando atualização da agenda de jogos...')
    data = fetch_and_format_matches()
    data = atualizar_placares(data)
    save_json(data)