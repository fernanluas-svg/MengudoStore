import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scraper_core as sc


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, '../src/data/nextMatch.json')
MATCHES_PATH = os.path.join(BASE_DIR, '../src/data/matches.json')
LIBERTADORES_PATH = os.path.join(BASE_DIR, '../src/data/libertadores.json')
CLASSIFICACAO_LIB_PATH = os.path.join(BASE_DIR, '../src/data/classificacaoLibertadores.json')
GE_API_URL = 'https://api.globoesporte.globo.com/tabela/d1a37fa4-e948-43a6-ba53-ab24ab3a45b1/fase/fase-unica-campeonato-brasileiro-2026/rodada/{rodada}/jogos/'
GE_RODADAS = 38
GE_LIBERTADORES_URL = 'https://ge.globo.com/futebol/libertadores/'
FLASHSCORE_TEAM_URL = 'https://www.flashscore.com/team/flamengo/fixtures/'
TEMPORADA = 2026

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
      {"id": "2026-08-22-cruzeiro", "opponent": "Cruzeiro", "opponentLogo": "https://s.sde.globo.com/media/organizations/2021/02/13/cruzeiro_2021.svg", "isHome": False, "date": "2026-08-22T20:30:00-03:00", "stadium": "Mineirão - Belo Horizonte, MG", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-08-30-botafogo", "opponent": "Botafogo", "opponentLogo": "https://s.sde.globo.com/media/organizations/2019/02/04/botafogo-svg.svg", "isHome": True, "date": "2026-08-30T16:00:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-09-06-remo", "opponent": "Remo", "opponentLogo": "https://s.sde.globo.com/media/organizations/2021/02/25/Remo-PA.svg", "isHome": False, "date": "2026-09-06T16:00:00-03:00", "stadium": "Baenão - Belém, PA", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-09-12-corinthians", "opponent": "Corinthians", "opponentLogo": "https://s.sde.globo.com/media/organizations/2024/10/09/Corinthians_2024_Q4ahot4.svg", "isHome": True, "date": "2026-09-12T16:00:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-09-19-red-bull-bragantino", "opponent": "Red Bull Bragantino", "opponentLogo": "https://s.sde.globo.com/media/organizations/2021/06/28/bragantino.svg", "isHome": True, "date": "2026-09-19T16:00:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-10-07-santos", "opponent": "Santos", "opponentLogo": "https://s.sde.globo.com/media/organizations/2018/03/12/santos.svg", "isHome": False, "date": "2026-10-07T21:30:00-03:00", "stadium": "Vila Belmiro - Santos, SP", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-10-10-fluminense", "opponent": "Fluminense", "opponentLogo": "https://s.sde.globo.com/media/organizations/2018/03/11/fluminense.svg", "isHome": True, "date": "2026-10-10T16:00:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-10-17-bahia", "opponent": "Bahia", "opponentLogo": "https://s.sde.globo.com/media/organizations/2018/03/11/bahia.svg", "isHome": False, "date": "2026-10-17T16:00:00-03:00", "stadium": "Arena Fonte Nova - Salvador, BA", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-10-24-atletico-mineiro", "opponent": "Atlético Mineiro", "opponentLogo": "https://s.sde.globo.com/media/organizations/2018/03/10/atletico-mg.svg", "isHome": True, "date": "2026-10-24T16:00:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-10-28-vasco-da-gama", "opponent": "Vasco da Gama", "opponentLogo": "https://s.sde.globo.com/media/organizations/2021/09/04/vasco_SVG.svg", "isHome": False, "date": "2026-10-28T21:30:00-03:00", "stadium": "São Januário - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-11-04-gremio", "opponent": "Grêmio", "opponentLogo": "https://s.sde.globo.com/media/organizations/2018/03/12/gremio.svg", "isHome": True, "date": "2026-11-04T21:30:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-11-18-athletico-paranaense", "opponent": "Athletico Paranaense", "opponentLogo": "https://s.sde.globo.com/media/organizations/2026/01/07/Athletico-PR.svg", "isHome": True, "date": "2026-11-18T21:30:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-11-21-palmeiras", "opponent": "Palmeiras", "opponentLogo": "https://s.sde.globo.com/media/organizations/2019/07/06/Palmeiras.svg", "isHome": False, "date": "2026-11-21T16:00:00-03:00", "stadium": "Allianz Parque - São Paulo, SP", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-11-28-coritiba", "opponent": "Coritiba", "opponentLogo": "https://s.sde.globo.com/media/organizations/2018/03/11/coritiba.svg", "isHome": False, "date": "2026-11-28T16:00:00-03:00", "stadium": "Couto Pereira - Curitiba, PR", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None},
      {"id": "2026-12-02-chapecoense", "opponent": "Chapecoense", "opponentLogo": "https://s.sde.globo.com/media/organizations/2021/06/21/CHAPECOENSE-2018.svg", "isHome": True, "date": "2026-12-02T21:30:00-03:00", "stadium": "Maracanã - Rio de Janeiro, RJ", "competition": "Brasileirão", "status": "SCHEDULED", "homeScore": None, "awayScore": None}
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


def _extrair_array_json(texto, idx):
    """Dado um índice que aponta para '[' em texto, retorna a substring do
    array balanceado (respeitando strings/escapes)."""
    depth = 0
    in_str = False
    esc = False
    j = idx
    while j < len(texto):
        c = texto[j]
        if in_str:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    return texto[idx:j + 1]
        j += 1
    return None


# ---------------------------------------------------------------------------
# FONTE PRIMÁRIA: Flashscore / Casas de Apostas (fetch mimetizado + adaptável)
# ---------------------------------------------------------------------------

KNOWN_TEAMS = set(LOGOS_SERIE_A.keys()) | set(NOMES_EXIBICAO.keys()) | {'flamengo'}


def _parse_flashscore_html(html, team_norm):
    """Extrai partidas de um HTML do Flashscore usando seletores adaptáveis
    (conteúdo: nome do time + data/placar), sem depender de classes CSS fixas.
    Retorna lista de dicts no formato interno. Se o adversário não for um time
    conhecido (ex.: Libertadores), a linha é ignorada com segurança."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')
    except Exception as e:
        log('WARN', f'Falha ao parsear HTML do Flashscore: {e}')
        return []

    partidas = []
    for row in sc.find_match_rows(soup, team_norm):
        txt = row.get_text(' ', strip=True)
        opp = sc.extract_opponent(txt, team_norm, KNOWN_TEAMS)
        # só considera adversários conhecidos para evitar lixo de layout novo
        if not opp or opp not in KNOWN_TEAMS:
            continue
        txt_norm = sc.normalize(txt)
        try:
            fla_pos = txt_norm.index('flamengo')
            opp_pos = txt_norm.index(opp)
        except ValueError:
            continue
        if fla_pos < opp_pos:
            mandante, visitante = team_norm, opp
        else:
            mandante, visitante = opp, team_norm
        gols_m, gols_v = sc.extract_scores(txt)
        iso = sc.extract_datetime(txt)
        if not iso:
            continue
        partidas.append({
            'data': iso,
            'mandante': mandante,
            'visitante': visitante,
            'gols_mandante': gols_m,
            'gols_visitante': gols_v,
            'estadio': 'A definir',
            'escudo_mandante': None,
            'escudo_visitante': None,
        })
    return partidas


def obter_partidas_flashscore():
    """Fonte primária: raspa as partidas (passadas e futuras) do Flamengo no
    Flashscore via fetch com mimetização de Chrome (curl_cffi / TLS spoofing).
    Seletores adaptáveis mantêm a extração mesmo se o layout mudar. Sem rede
    ou com Cloudflare bloqueando, retorna [] para acionar o fallback do GE."""
    res = sc.fetch(FLASHSCORE_TEAM_URL, timeout=30, retries=3)
    if not res.ok:
        log('WARN', f'Flashscore indisponível ({res.engine}): {res.error}')
        return []
    partidas = _parse_flashscore_html(res.text, 'flamengo')
    if not partidas:
        return []
    return partidas


def obter_libertadores_flashscore():
    """Fonte primária para o mata-mata da Libertadores via Flashscore.
    Best-effort: usa fetch mimetizado + parsing adaptável; retorna [] se não
    houver rede ou se os adversários não forem times conhecidos."""
    res = sc.fetch('https://www.flashscore.com/football/copa-libertadores/',
                   timeout=30, retries=3)
    if not res.ok:
        log('WARN', f'Flashscore/Libertadores indisponível ({res.engine}): {res.error}')
        return []
    return _parse_flashscore_html(res.text, 'flamengo')


# ---------------------------------------------------------------------------
# FALLBACK OFICIAL: ge.globo (API de tabela + página da Libertadores)
# ---------------------------------------------------------------------------

def obter_partidas_ge():
    """Fallback oficial: consulta a API pública de tabela do GE (Globo Esporte),
    percorrendo as 38 rodadas do Brasileirão e capturando as partidas do Flamengo.
    Retorna o formato interno, incluindo os escudos."""
    partidas = []
    for rodada in range(1, GE_RODADAS + 1):
        url = GE_API_URL.format(rodada=rodada)
        try:
            jogos = sc.fetch_json(url, timeout=30, retries=2)
            if not isinstance(jogos, list):
                raise RuntimeError('resposta vazia/inválida do GE')
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
            data = str(data).split('T')[0]
            hora = str(jogo.get('hora_realizacao') or '19:00').split('T')[0]
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


def _mapear_fase(nome):
    nome = (nome or '').lower()
    if 'oitavas' in nome:
        return 'Oitavas de Final'
    if 'quartas' in nome:
        return 'Quartas de Final'
    if 'semifinal' in nome:
        return 'Semifinal'
    if 'final' in nome:
        return 'Final'
    return 'Oitavas de Final'


def _leg_libertadores(raw):
    if not raw:
        return None
    equipes = raw.get('equipes') or {}
    mandante = normalizar((equipes.get('mandante') or {}).get('nome_popular', ''))
    visitante = normalizar((equipes.get('visitante') or {}).get('nome_popular', ''))
    data = raw.get('data_realizacao')
    hora = raw.get('hora_realizacao') or '00:00'
    iso = f'{data}T{hora}:00-03:00' if data else None
    return {
        'casa': mandante,
        'fora': visitante,
        'placarCasa': raw.get('placar_oficial_mandante'),
        'placarFora': raw.get('placar_oficial_visitante'),
        'data': iso,
    }


def _secao_libertadores_ge():
    """Retorna a lista 'secao' (chaves/jogos) embutida na página do GE."""
    res = sc.fetch(GE_LIBERTADORES_URL, timeout=30, retries=3)
    if not res.ok:
        raise RuntimeError(f'Falha ao baixar página do GE ({res.engine}): {res.error}')
    t = res.text
    i = t.find('"secao":[')
    if i == -1:
        raise RuntimeError('Bloco "secao" da Libertadores não encontrado no GE.')
    arr = _extrair_array_json(t, i + len('"secao":'))
    if not arr:
        raise RuntimeError('Não foi possível extrair o bloco "secao" do GE.')
    return json.loads(arr)


def obter_jogos_libertadores_flashscore():
    """Fonte primária para as partidas da Libertadores via Flashscore.
    Best-effort: usa fetch mimetizado + parsing adaptável; retorna [] se não
    houver rede ou se os adversários não forem times conhecidos."""
    res = sc.fetch('https://www.flashscore.com/football/copa-libertadores/',
                   timeout=30, retries=3)
    if not res.ok:
        log('WARN', f'Flashscore/Libertadores indisponível ({res.engine}): {res.error}')
        return []
    partidas = _parse_flashscore_html(res.text, 'flamengo')
    for p in partidas:
        p['competition'] = 'Libertadores'
    return partidas


def obter_jogos_libertadores_ge():
    """Fallback oficial: extrai as partidas (mandante, visitante, placar, data)
    do Flamengo em todas as fases da Libertadores a partir do JSON embutido na
    página do ge.globo. Retorna partidas no formato interno do consolidador de
    agenda, com competition='Libertadores'."""
    secao = _secao_libertadores_ge()
    jogos = []
    for item in secao:
        for chave in item.get('chave', []):
            for raw in chave.get('jogos', []):
                equipes = raw.get('equipes') or {}
                mandante = normalizar((equipes.get('mandante') or {}).get('nome_popular', ''))
                visitante = normalizar((equipes.get('visitante') or {}).get('nome_popular', ''))
                if 'flamengo' not in (mandante, visitante):
                    continue
                data = raw.get('data_realizacao')
                hora = raw.get('hora_realizacao') or '00:00'
                sede = raw.get('sede') or {}
                jogos.append({
                    'data': f'{data}T{hora}:00-03:00' if data else None,
                    'mandante': mandante,
                    'visitante': visitante,
                    'gols_mandante': raw.get('placar_oficial_mandante'),
                    'gols_visitante': raw.get('placar_oficial_visitante'),
                    'estadio': sede.get('nome_popular') or 'A definir',
                    'escudo_mandante': (equipes.get('mandante') or {}).get('escudo'),
                    'escudo_visitante': (equipes.get('visitante') or {}).get('escudo'),
                    'competition': 'Libertadores',
                })
    if not jogos:
        raise RuntimeError('Nenhuma partida do Flamengo encontrada no GE.')
    return jogos


def obter_libertadores_ge():
    """Fallback oficial para o chaveamento da Libertadores: raspa o JSON
    embutido na página do ge.globo (estrutura 'secao' -> 'chave' -> 'jogos')."""
    secao = _secao_libertadores_ge()

    confrontos = []
    for item in secao:
        for chave in item.get('chave', []):
            jogos = chave.get('jogos', [])
            if len(jogos) < 2:
                continue
            ida = _leg_libertadores(jogos[0])
            volta = _leg_libertadores(jogos[1])
            if not ida or not volta:
                continue
            times = {ida['casa'], ida['fora'], volta['casa'], volta['fora']}
            if not times & {'flamengo'}:
                continue

            def fla(g):
                return g['placarCasa'] if g['casa'] == 'flamengo' else g['placarFora']

            def adv(g):
                return g['placarFora'] if g['casa'] == 'flamengo' else g['placarCasa']

            gA = None if (ida['placarCasa'] is None or volta['placarCasa'] is None) else fla(ida) + fla(volta)
            gB = None if (ida['placarFora'] is None or volta['placarFora'] is None) else adv(ida) + adv(volta)

            if 'flamengo' == ida['casa']:
                adv_norm = ida['fora']
            elif 'flamengo' == ida['fora']:
                adv_norm = ida['casa']
            elif 'flamengo' == volta['casa']:
                adv_norm = volta['fora']
            else:
                adv_norm = volta['casa']

            adv_nome = NOMES_EXIBICAO.get(
                adv_norm, adv_norm.replace('-', ' ').title() if adv_norm != 'a definir' else 'A definir'
            )

            if gA is None or gB is None:
                status = 'A_DEFINIR'
                classificado = None
            else:
                status = 'DEFINIDO'
                classificado = 'Flamengo' if gA > gB else (adv_nome if gB > gA else None)

            data = None
            for lg in (ida, volta):
                if lg['placarCasa'] is None:
                    data = lg['data']
                    break
            if data is None:
                data = volta['data'] or ida['data']

            fase = _mapear_fase(chave.get('nome'))
            confrontos.append({
                'id': f"{fase.lower().replace(' ', '-')}-flamengo-{adv_norm.replace(' ', '-')}",
                'timeA': 'Flamengo',
                'timeB': adv_nome,
                'fase': fase,
                'data': data,
                'ida': ida,
                'volta': volta,
                'agregado': {'timeA': gA, 'timeB': gB},
                'classificado': classificado,
                'status': status,
            })

    if not confrontos:
        raise RuntimeError('Nenhum confronto do Flamengo encontrado no GE.')
    return confrontos


# ---------------------------------------------------------------------------
# MONTAGEM / PERSISTÊNCIA
# ---------------------------------------------------------------------------

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
        'competition': partida.get('competition', 'Brasileirão'),
        'status': 'FINISHED',
        'homeScore': homeScore,
        'awayScore': awayScore,
    }


def atualizar_agenda():
    """
    Sincroniza os jogos por data:
    - Jogos encerrados (data < agora) -> matches.json (FINISHED)
    - Próximos confrontos (data >= agora) -> nextMatch.json (SCHEDULED, ativo)
    Fonte primária: Flashscore / Casas de Apostas. Fallback oficial: ge.globo.
    Se nenhuma fonte responder, reaproveita os arquivos existentes.
    """
    base = fetch_and_format_matches()
    partidas_br = None
    origem = None

    try:
        partidas_br = obter_partidas_flashscore()
    except Exception as e:
        log('WARN', f'Fonte primária (Flashscore) indisponível: {e}')

    if not partidas_br:
        try:
            partidas_br = obter_partidas_ge()
            origem = 'GE (fallback)'
        except Exception as e2:
            log('ERROR', f'Fallback (GE) indisponível: {e2}')
            partidas_br = None

    # Libertadores (todas as fases com o Flamengo) — primário Flashscore, fallback GE
    partidas_lib = None
    try:
        partidas_lib = obter_jogos_libertadores_flashscore()
    except Exception as e:
        log('WARN', f'Fonte primária (Flashscore) indisponível: {e}')

    if not partidas_lib:
        try:
            partidas_lib = obter_jogos_libertadores_ge()
            if origem is None:
                origem = 'GE (fallback)'
        except Exception as e2:
            log('WARN', f'Fallback (GE/Libertadores) indisponível: {e2}')
            partidas_lib = None

    # Unifica todas as competições (Brasileirão + Libertadores + futuras fontes)
    partidas = list(partidas_br or []) + list(partidas_lib or [])

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


def atualizar_libertadores():
    """Atualiza o chaveamento da Libertadores.
    Fonte primária: Flashscore / Casas de Apostas. Fallback oficial: ge.globo.
    Rodadas futuras ainda não disponíveis na fonte são preservadas a partir do
    arquivo existente (ex.: Quartas de Final ainda não sorteadas)."""
    confrontos = None
    try:
        confrontos = obter_libertadores_flashscore()
    except Exception as e:
        log('WARN', f'Fonte primária (Flashscore/Libertadores) indisponível: {e}')

    if not confrontos:
        try:
            confrontos = obter_libertadores_ge()
            origem = 'GE (fallback)'
        except Exception as e2:
            log('WARN', f'Fallback (GE/Libertadores) indisponível: {e2}')
            confrontos = None

    if not confrontos:
        existentes = carregar_existentes(LIBERTADORES_PATH)
        if existentes:
            save_json(existentes, LIBERTADORES_PATH)
            log('WARN', 'Chaveamento da Libertadores mantido a partir dos dados existentes.')
        return None

    # Preserva rodadas futuras ausentes na fonte (merge por id, fonte tem prioridade)
    existentes = carregar_existentes(LIBERTADORES_PATH)
    por_id = {}
    if isinstance(existentes, dict) and existentes.get('confrontos'):
        for c in existentes['confrontos']:
            por_id[c['id']] = c
    for c in confrontos:
        por_id[c['id']] = c
    mesclados = list(por_id.values())

    dados = {
        'fase': 'Copa Libertadores 2026',
        'atualizadoEm': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'confrontos': mesclados,
    }
    save_json(dados, LIBERTADORES_PATH)
    log('SUCCESS', f'{len(mesclados)} confronto(s) de mata-mata registrados via {origem}.')
    return mesclados


if __name__ == "__main__":
    log('INFO', 'Iniciando atualização da agenda de jogos...')
    atualizar_agenda()
    atualizar_libertadores()
