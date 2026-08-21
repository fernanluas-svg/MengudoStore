import json
import os
import re
import time
import unicodedata
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, '../src/data/nextMatch.json')
MATCHES_PATH = os.path.join(BASE_DIR, '../src/data/matches.json')
WIKIPEDIA_URL = 'https://pt.wikipedia.org/wiki/Temporada_do_Clube_de_Regatas_do_Flamengo_de_2026'
GE_API_URL = 'https://api.globoesporte.globo.com/tabela/d1a37fa4-e948-43a6-ba53-ab24ab3a45b1/fase/fase-unica-campeonato-brasileiro-2026/rodada/{rodada}/jogos/'
GE_RODADAS = 38
TEMPORADA = 2026
HEADERS = {
    'User-Agent': 'MengudoStoreBot/1.0 (automação da agenda de jogos; contato@mengudostore.com)'
}

LOGOS_SERIE_A = {
    'sao paulo': 'https://s.sde.globo.com/media/organizations/2018/03/11/sao-paulo.svg',
    'flamengo': 'https://s.sde.globo.com/media/organizations/2018/04/10/Flamengo-2018.svg',
    'internacional': 'https://s.sde.globo.com/media/organizations/2018/03/11/internacional.svg',
    'vitoria': 'https://s.sde.globo.com/media/organizations/2025/12/18/Vitoria_2025.svg',
    'mirassol': 'https://s.sde.globo.com/media/organizations/2026/07/17/MIrassol.svg',
    'cruzeiro': 'https://s.sde.globo.com/media/organizations/2021/02/13/cruzeiro_2021.svg',
    'botafogo': 'https://s.sde.globo.com/media/organizations/2019/02/04/botafogo-svg.svg',
    'remo': 'https://s.sde.globo.com/media/organizations/2021/02/25/Remo-PA.svg',
    'corinthians': 'https://s.sde.globo.com/media/organizations/2024/10/09/Corinthians_2024_Q4ahot4.svg',
    'red bull bragantino': 'https://s.sde.globo.com/media/organizations/2021/06/28/bragantino.svg',
    'santos': 'https://s.sde.globo.com/media/organizations/2018/03/12/santos.svg',
    'fluminense': 'https://s.sde.globo.com/media/organizations/2018/03/11/fluminense.svg',
    'bahia': 'https://s.sde.globo.com/media/organizations/2018/03/11/bahia.svg',
    'atletico mineiro': 'https://s.sde.globo.com/media/organizations/2018/03/10/atletico-mg.svg',
    'vasco da gama': 'https://s.sde.globo.com/media/organizations/2021/09/04/vasco_SVG.svg',
    'gremio': 'https://s.sde.globo.com/media/organizations/2018/03/12/gremio.svg',
    'atletico paranaense': 'https://s.sde.globo.com/media/organizations/2026/01/07/Athletico-PR.svg',
    'palmeiras': 'https://s.sde.globo.com/media/organizations/2019/07/06/Palmeiras.svg',
    'coritiba': 'https://s.sde.globo.com/media/organizations/2018/03/11/coritiba.svg',
    'chapecoense': 'https://s.sde.globo.com/media/organizations/2021/06/21/CHAPECOENSE-2018.svg',
}

NOMES_EXIBICAO = {
    'sao paulo': 'São Paulo',
    'flamengo': 'Flamengo',
    'internacional': 'Internacional',
    'vitoria': 'Vitória',
    'mirassol': 'Mirassol',
    'cruzeiro': 'Cruzeiro',
    'botafogo': 'Botafogo',
    'remo': 'Remo',
    'corinthians': 'Corinthians',
    'red bull bragantino': 'Red Bull Bragantino',
    'santos': 'Santos',
    'fluminense': 'Fluminense',
    'bahia': 'Bahia',
    'atletico mineiro': 'Atlético Mineiro',
    'vasco da gama': 'Vasco da Gama',
    'gremio': 'Grêmio',
    'atletico paranaense': 'Athletico Paranaense',
    'palmeiras': 'Palmeiras',
    'coritiba': 'Coritiba',
    'chapecoense': 'Chapecoense',
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
    'bragantino': 'red bull bragantino',
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


MESES = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
    'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
}


def _extrair_placar(texto):
    m = re.search(r'(\d+)\s*[–-]\s*(\d+)', texto)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def obter_partidas_wikipedia():
    """
    Fonte primária: raspa a página "Temporada do Flamengo 2026" na Wikipédia,
    percorrendo todas as rodadas do Brasileirão (anteriores e futuras).
    Retorna uma lista de partidas do Flamengo no formato:
    {data, mandante, visitante, gols_mandante, gols_visitante, estadio}.
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

    partidas = []
    for tabela in soup.find_all('table'):
        if tabela.find_previous('h3') is not cabecalho:
            continue
        linhas = tabela.find_all('tr')
        if len(linhas) < 2:
            continue
        cabecalho_linha = linhas[0].find_all(['td', 'th'])
        detalhe_linha = linhas[1].find_all(['td', 'th'])
        if len(cabecalho_linha) < 5:
            continue

        texto_data = cabecalho_linha[0].get_text(' ', strip=True)
        mdata = re.match(r'(\d{1,2})\s+de\s+([a-zç]+)', texto_data, re.I)
        if not mdata:
            continue
        dia = int(mdata.group(1))
        mes = MESES.get(mdata.group(2).lower())
        if mes is None:
            continue

        mandante = normalizar(cabecalho_linha[1].get_text(' ', strip=True))
        visitante = normalizar(cabecalho_linha[3].get_text(' ', strip=True))
        if mandante != 'flamengo' and visitante != 'flamengo':
            continue

        gols_m, gols_v = _extrair_placar(cabecalho_linha[2].get_text(' ', strip=True))

        estadio = None
        hora = '19:00'
        if len(detalhe_linha) >= 5:
            texto_hora = detalhe_linha[0].get_text(' ', strip=True)
            mh = re.search(r'(\d{1,2}):(\d{2})', texto_hora)
            if mh:
                hora = f'{mh.group(1)}:{mh.group(2)}'
            texto_estadio = detalhe_linha[4].get_text(' ', strip=True)
            me = re.search(r'Estádio:\s*([^P]+)', texto_estadio)
            if me:
                estadio = me.group(1).strip()

        if not estadio:
            cidade = cabecalho_linha[4].get_text(' ', strip=True)
            estadio = cidade if cidade and cidade != 'A definir' else 'A definir'

        partidas.append({
            'data': f'{TEMPORADA}-{mes:02d}-{dia:02d}T{hora}:00-03:00',
            'mandante': mandante,
            'visitante': visitante,
            'gols_mandante': gols_m,
            'gols_visitante': gols_v,
            'estadio': estadio,
        })

    if not partidas:
        raise RuntimeError('Nenhuma partida do Flamengo encontrada na página.')
    return partidas


def obter_partidas_ge():
    """
    Fonte secundária: consulta a API pública de tabela do GE (Globo Esporte),
    percorrendo as 38 rodadas do Brasileirão e capturando as partidas do Flamengo.
    Retorna o mesmo formato da fonte primária, incluindo os escudos.
    """
    partidas = []
    for rodada in range(1, GE_RODADAS + 1):
        url = GE_API_URL.format(rodada=rodada)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            jogos = resp.json()
        except Exception as e:
            log('WARN', f'GE rodada {rodada} indisponível: {e}')
            continue
        for jogo in jogos:
            mandante = normalizar(jogo['equipes']['mandante']['nome_popular'])
            visitante = normalizar(jogo['equipes']['visitante']['nome_popular'])
            if mandante != 'flamengo' and visitante != 'flamengo':
                continue
            data = jogo.get('data_realizacao')
            if not data:
                continue
            hora = jogo.get('hora_realizacao') or '19:00'
            sede = jogo.get('sede') or {}
            partidas.append({
                'data': f'{data}T{hora}:00-03:00',
                'mandante': mandante,
                'visitante': visitante,
                'gols_mandante': jogo.get('placar_oficial_mandante'),
                'gols_visitante': jogo.get('placar_oficial_visitante'),
                'estadio': sede.get('nome_popular') or 'A definir',
                'escudo_mandante': jogo['equipes']['mandante'].get('escudo'),
                'escudo_visitante': jogo['equipes']['visitante'].get('escudo'),
            })
        time.sleep(0.2)

    if not partidas:
        raise RuntimeError('Nenhuma partida do Flamengo encontrada na API do GE.')
    return partidas


def montar_entrada_historica(partida):
    """Converte uma partida encerrada em uma entrada FINISHED do nextMatch.json."""
    if partida['mandante'] == 'flamengo':
        isHome = True
        opponent = partida['visitante']
        homeScore = partida['gols_mandante']
        awayScore = partida['gols_visitante']
        escudo = partida.get('escudo_visitante') or LOGOS_SERIE_A.get(opponent)
    else:
        isHome = False
        opponent = partida['mandante']
        homeScore = partida['gols_mandante']
        awayScore = partida['gols_visitante']
        escudo = partida.get('escudo_mandante') or LOGOS_SERIE_A.get(opponent)

    if not escudo:
        escudo = LOGOS_SERIE_A['flamengo']

    slug = opponent.replace(' ', '-')
    return {
        'id': f"{partida['data'][:10]}-{slug}",
        'opponent': NOMES_EXIBICAO.get(opponent, opponent),
        'opponentLogo': escudo,
        'isHome': isHome,
        'date': partida['data'],
        'stadium': partida['estadio'],
        'competition': 'Brasileirão',
        'status': 'FINISHED',
        'homeScore': homeScore,
        'awayScore': awayScore,
    }


def atualizar_agenda():
    """
    Sincroniza os jogos por data:
    - Jogos encerrados (data < agora) -> matches.json (FINISHED)
    - Próximos confrontos (data >= agora) -> nextMatch.json (SCHEDULED, ativo)
    Usa a Wikipédia como fonte primária e a API do GE como fallback. Se nenhuma
    fonte responder, reaproveita o nextMatch.json existente para reclassificar.
    """
    base = fetch_and_format_matches()
    partidas = None
    origem = None

    try:
        partidas = obter_partidas_wikipedia()
        origem = 'Wikipedia'
    except Exception as e:
        log('WARN', f'Fonte primária indisponível: {e}')
        try:
            partidas = obter_partidas_ge()
            origem = 'API GE'
        except Exception as e2:
            log('ERROR', f'Fonte secundária indisponível: {e2}')
            partidas = None

    if partidas:
        historico = [
            montar_entrada_historica(p)
            for p in partidas
            if p['gols_mandante'] is not None and p['gols_visitante'] is not None
        ]
        combinadas = historico + base
        vistos = set()
        todas = []
        for m in combinadas:
            if m['id'] in vistos:
                continue
            vistos.add(m['id'])
            todas.append(m)
        # Preserva jogos adicionados manualmente (nextMatch.json e matches.json)
        for caminho in (JSON_PATH, MATCHES_PATH):
            extras = carregar_existentes(caminho)
            if extras:
                for m in extras:
                    if m['id'] not in vistos:
                        vistos.add(m['id'])
                        todas.append(m)
    else:
        existentes = carregar_existentes()
        if existentes is not None:
            log('WARN', 'Fontes indisponíveis: reutilizando nextMatch.json e sincronizando por data.')
            todas = existentes
            origem = 'dados existentes (fallback)'
        else:
            log('WARN', 'Usando dados estáticos de fallback (sem acesso às fontes).')
            todas = base
            origem = 'fallback estático'

    agora = datetime.now(timezone.utc)
    resultados = []
    agenda = []
    for m in todas:
        data = datetime.fromisoformat(m['date'])
        if data < agora:
            m['status'] = 'FINISHED'
            resultados.append(m)
        else:
            m['status'] = 'SCHEDULED'
            agenda.append(m)

    resultados.sort(key=lambda x: x['date'], reverse=True)
    agenda.sort(key=lambda x: x['date'])

    save_json(agenda, JSON_PATH)
    save_json(resultados, MATCHES_PATH)
    log('SUCCESS', f'{len(resultados)} resultado(s) e {len(agenda)} agendado(s) registrados via {origem}.')
    return agenda


def carregar_existentes(caminho=JSON_PATH):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def save_json(data, caminho=JSON_PATH):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log('SUCCESS', f'Arquivo atualizado em: {caminho}')


if __name__ == "__main__":
    log('INFO', 'Iniciando atualização da agenda de jogos...')
    atualizar_agenda()