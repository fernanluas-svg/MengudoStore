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
CARIOCA_PATH = os.path.join(BASE_DIR, '../src/data/carioca.json')
COPA_BRASIL_PATH = os.path.join(BASE_DIR, '../src/data/copaDoBrasil.json')
ODDS_PATH = os.path.join(BASE_DIR, '../src/data/odds.json')
GE_API_URL = 'https://api.globoesporte.globo.com/tabela/d1a37fa4-e948-43a6-ba53-ab24ab3a45b1/fase/fase-unica-campeonato-brasileiro-2026/rodada/{rodada}/jogos/'
GE_RODADAS = 38
GE_LIBERTADORES_URL = 'https://ge.globo.com/futebol/libertadores/'
GE_CARIOCA_URL = 'https://ge.globo.com/rj/futebol/campeonato-carioca/'
GE_COPA_BRASIL_URL = 'https://ge.globo.com/futebol/copa-do-brasil/'
FLASHSCORE_TEAM_URL = 'https://www.flashscore.com/team/flamengo/fixtures/'
TEMPORADA = 2026

# ---------------------------------------------------------------------------
# NOVAS FONTES DE RASPAGEM (com fallback para o ge.globo)
# ---------------------------------------------------------------------------
ESPN_COPA_BRASIL_URL = 'https://www.espn.com.br/futebol/liga/_/nome/bra.copa_do_brasil'
ESPN_CARIOCA_URL = 'https://www.espn.com.br/futebol/liga/_/nome/bra.camp.carioca'
FERJ_CARIOCA_URL = 'https://www.fferj.com.br/campeonato-carioca/'
LANCE_TABELAS_URL = 'https://www.lance.com.br/tabelas/'
LANCE_COPA_BRASIL_URL = 'https://www.lance.com.br/tabelas/'

# Ordem de prioridade das fontes (a primeira que retornar dados válidos vence;
# ge.globo é mantido como fallback principal confiável).
ORDEM_FONTES_CARIOCA = [
    ('ESPN Brasil', ESPN_CARIOCA_URL),
    ('FERJ', FERJ_CARIOCA_URL),
    ('Lance!', LANCE_TABELAS_URL),
    ('ge.globo', GE_CARIOCA_URL),
]
ORDEM_FONTES_COPA = [
    ('ESPN Brasil', ESPN_COPA_BRASIL_URL),
    ('Lance!', LANCE_COPA_BRASIL_URL),
    ('ge.globo', GE_COPA_BRASIL_URL),
]

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


def _secao_ge(url):
    """Retorna a lista 'secao' (chaves/jogos) embutida na página do GE.
    Reutilizado para a Libertadores e para a Copa do Brasil."""
    res = sc.fetch(url, timeout=30, retries=3)
    if not res.ok:
        raise RuntimeError(f'Falha ao baixar página do GE ({res.engine}): {res.error}')
    t = res.text
    i = t.find('"secao":[')
    if i == -1:
        raise RuntimeError('Bloco "secao" não encontrado no GE.')
    arr = _extrair_array_json(t, i + len('"secao":'))
    if not arr:
        raise RuntimeError('Não foi possível extrair o bloco "secao" do GE.')
    return json.loads(arr)


def _secao_libertadores_ge():
    """Retorna a lista 'secao' (chaves/jogos) embutida na página do GE."""
    return _secao_ge(GE_LIBERTADORES_URL)


def _extrair_objeto_json(texto, idx):
    """Dado um índice que aponta para '{' em texto, retorna a substring do
    objeto balanceado (respeitando strings/escapes)."""
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
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return texto[idx:j + 1]
        j += 1
    return None


def _achar_classificacao(dados):
    """Procura recursivamente, em um objeto do GE, uma lista de standings de
    pontos corridos (cada item com 'pontos' e 'time'/'nome')."""
    def busca(d):
        if isinstance(d, dict):
            if 'pontos' in d and ('time' in d or 'nome' in d or 'nome_popular' in d):
                return [d]
            for v in d.values():
                r = busca(v)
                if r:
                    return r
        elif isinstance(d, list):
            # lista homogênea de standings?
            if d and all(isinstance(x, dict) and 'pontos' in x for x in d[:5]):
                return list(d)
            for x in d:
                r = busca(x)
                if r:
                    return r
        return None
    return busca(dados) or []


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


def _montar_confrontos_mata_mata(secao):
    """Constrói a lista de confrontos de ida/volta (estilo mata-mata) a partir de
    uma estrutura 'secao' do GE (Libertadores ou Copa do Brasil). Inclui apenas
    os confrontos que envolvem o Flamengo."""
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


def obter_libertadores_ge():
    """Fallback oficial para o chaveamento da Libertadores: raspa o JSON
    embutido na página do ge.globo (estrutura 'secao' -> 'chave' -> 'jogos')."""
    return _montar_confrontos_mata_mata(_secao_libertadores_ge())


def obter_copa_do_brasil_flashscore():
    """Fonte primária para a Copa do Brasil via Flashscore (best-effort).
    Retorna [] se indisponível ou sem adversários conhecidos."""
    res = sc.fetch('https://www.flashscore.com/football/copa-do-brasil/',
                   timeout=30, retries=3)
    if not res.ok:
        log('WARN', f'Flashscore/Copa do Brasil indisponível ({res.engine}): {res.error}')
        return []
    return _parse_flashscore_html(res.text, 'flamengo')


def obter_copa_do_brasil_ge():
    """Fallback oficial para o chaveamento da Copa do Brasil: reutiliza a
    estrutura 'secao' do ge.globo (mata-mata ida/volta)."""
    return _montar_confrontos_mata_mata(_secao_ge(GE_COPA_BRASIL_URL))


def obter_tabela_carioca_ge():
    """Tenta extrair a classificação da Taça Guanabara (pontos corridos) a partir
    do objeto 'classificacao' embutido na página do GE. Levanta RuntimeError se
    o GE ainda não expor a tabela (ex.: temporada ainda não iniciada)."""
    res = sc.fetch(GE_CARIOCA_URL, timeout=30, retries=3)
    if not res.ok:
        raise RuntimeError(f'Falha ao baixar página do GE ({res.engine}): {res.error}')
    t = res.text
    i = t.find('const classificacao = ')
    if i == -1:
        raise RuntimeError('Bloco "classificacao" do Carioca não encontrado no GE.')
    start = t.find('{', i)
    if start == -1:
        raise RuntimeError('Objeto "classificacao" do Carioca inválido.')
    obj = _extrair_objeto_json(t, start)
    if not obj:
        raise RuntimeError('Não foi possível extrair o objeto "classificacao" do GE.')
    dados = json.loads(obj)

    linhas_brutas = _achar_classificacao(dados)
    if not linhas_brutas:
        raise RuntimeError('Classificação da Taça Guanabara não disponível no GE.')

    linhas = []
    for idx, e in enumerate(linhas_brutas, start=1):
        nome = e.get('nome') or e.get('time') or e.get('nome_popular') or 'A definir'
        nome_norm = normalizar(nome)
        gols_pro = e.get('gols_pro') or e.get('gp') or 0
        gols_contra = e.get('gols_contra') or e.get('gc') or 0
        saldo = e.get('saldo_gols') or e.get('sg')
        if saldo is None:
            try:
                saldo = int(gols_pro) - int(gols_contra)
            except Exception:
                saldo = 0
        linhas.append({
            'posicao': int(e.get('posicao') or idx),
            'time': NOMES_EXIBICAO.get(nome_norm, nome),
            'pontos': int(e.get('pontos') or 0),
            'jogos': int(e.get('jogos') or 0),
            'vitorias': int(e.get('vitorias') or 0),
            'empates': int(e.get('empates') or 0),
            'derrotas': int(e.get('derrotas') or 0),
            'saldoGols': int(saldo),
        })

    if not linhas:
        raise RuntimeError('Classificação da Taça Guanabara vazia no GE.')
    return linhas


# ---------------------------------------------------------------------------
# NOVAS FONTES: ESPN Brasil, FERJ, Lance! (fallback ge.globo)
# ---------------------------------------------------------------------------

def _fetch_html(url, retries=3):
    """Atalho de fetch HTML mimetizado. Retorna o texto ou None."""
    res = sc.fetch(url, timeout=30, retries=retries)
    if not res.ok:
        return None
    return res.text


def _parse_tabela_classificacao_html(html):
    """Parser genérico e resiliente de tabelas de classificação (ESPN/FERJ/Lance).

    Não depende de classes CSS fixas: localiza <tr> cujas células tenham ao
    menos 6 valores numéricos (P, J, V, E, D, SG...) e extrai o time a partir
    da primeira célula textual. Retorna [] se nada consistente for encontrado.
    Nunca lança exceção."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')
    except Exception:
        return []

    linhas = []
    for tr in soup.find_all('tr'):
        cells = [c.get_text(' ', strip=True) for c in tr.find_all(['td', 'th'])]
        cells = [c for c in cells if c != '']
        if len(cells) < 7:
            continue
        nums = []
        for c in cells:
            try:
                nums.append(int(c))
            except ValueError:
                nums.append(None)
        n_numeric = sum(1 for n in nums if n is not None)
        if n_numeric < 6:
            continue

        posicao = None
        time = None
        for i, c in enumerate(cells):
            if nums[i] is not None:
                if posicao is None:
                    posicao = nums[i]
                continue
            if time is None:
                time = c
        if not time:
            continue

        valores = [n for n in nums if n is not None]
        # descarta a posição do início, se for o primeiro valor numérico
        restante = valores[1:] if (posicao is not None and valores and posicao == valores[0]) else valores
        try:
            pontos = restante[0]
            jogos = restante[1] if len(restante) > 1 else 0
            vitorias = restante[2] if len(restante) > 2 else 0
            empates = restante[3] if len(restante) > 3 else 0
            derrotas = restante[4] if len(restante) > 4 else 0
            saldoGols = restante[5] if len(restante) > 5 else 0
        except IndexError:
            continue

        nome_norm = normalizar(time)
        gols_pro = (restante[6] if len(restante) > 6 else None)
        gols_contra = (restante[7] if len(restante) > 7 else None)
        if saldoGols == 0 and gols_pro is not None and gols_contra is not None:
            try:
                saldoGols = int(gols_pro) - int(gols_contra)
            except Exception:
                pass

        linhas.append({
            'posicao': int(posicao) if posicao else len(linhas) + 1,
            'time': NOMES_EXIBICAO.get(nome_norm, time),
            'pontos': int(pontos),
            'jogos': int(jogos),
            'vitorias': int(vitorias),
            'empates': int(empates),
            'derrotas': int(derrotas),
            'saldoGols': int(saldoGols),
        })
    return linhas


def obter_tabela_carioca_espn():
    """Fonte ESPN Brasil para a Taça Guanabara (best-effort)."""
    html = _fetch_html(ESPN_CARIOCA_URL)
    if not html:
        return []
    return _parse_tabela_classificacao_html(html)


def obter_tabela_carioca_ferj():
    """Fonte oficial FERJ para a Taça Guanabara (best-effort)."""
    html = _fetch_html(FERJ_CARIOCA_URL)
    if not html:
        return []
    return _parse_tabela_classificacao_html(html)


def obter_tabela_carioca_lance():
    """Fonte Lance! para a Taça Guanabara (best-effort)."""
    html = _fetch_html(LANCE_TABELAS_URL)
    if not html:
        return []
    return _parse_tabela_classificacao_html(html)


def _secao_para_jogos_flamengo(secao, competition):
    """Extrai as partidas do Flamengo de um bloco 'secao' (estrutura do GE)."""
    jogos = []
    for item in secao or []:
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
                is_home = mandante == 'flamengo'
                opponent = visitante if is_home else mandante
                opponent_logo = (equipes.get('visitante' if is_home else 'mandante') or {}).get('escudo')
                jogos.append({
                    'data': f'{data}T{hora}:00-03:00' if data else None,
                    'mandante': NOMES_EXIBICAO.get(mandante, mandante),
                    'visitante': NOMES_EXIBICAO.get(visitante, visitante),
                    'placarMandante': raw.get('placar_oficial_mandante'),
                    'placarVisitante': raw.get('placar_oficial_visitante'),
                    'estadio': sede.get('nome_popular') or 'A definir',
                    'adversario': NOMES_EXIBICAO.get(opponent, opponent),
                    'isHome': is_home,
                    'adversarioLogo': opponent_logo or LOGOS_SERIE_A.get(opponent),
                    'competition': competition,
                })
    return jogos


def obter_jogos_flamengo_carioca_ge():
    """Jogos do Flamengo no Carioca a partir do bloco 'secao' do ge.globo."""
    try:
        secao = _secao_ge(GE_CARIOCA_URL)
    except Exception:
        return []
    return _secao_para_jogos_flamengo(secao, 'Campeonato Carioca')


def _extrair_confrontos_de_html(html):
    """Parser genérico de mata-mata a partir de HTML (ESPN/Lance/Flashscore-like).

    Reaproveita a heurística de linhas de partida do scraper_core e agrupa as
    partidas do Flamengo por adversário em ida/volta. Retorna [] se não houver
    dados consistentes. Best-effort."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')
    except Exception:
        return []
    partidas = _parse_flashscore_html(html, 'flamengo')
    if not partidas:
        return []

    por_adversario = {}
    for p in partidas:
        adv = p['visitante'] if p['mandante'] == 'flamengo' else p['mandante']
        por_adversario.setdefault(adv, []).append(p)

    confrontos = []
    for adv, ps in por_adversario.items():
        ps.sort(key=lambda x: x['data'])
        ida = ps[0]
        volta = ps[-1] if len(ps) > 1 else None

        def _leg(p):
            casa = p['mandante']
            fora = p['visitante']
            esc_casa = p.get('escudo_mandante') or LOGOS_SERIE_A.get(casa) or LOGOS_SERIE_A['flamengo']
            esc_fora = p.get('escudo_visitante') or LOGOS_SERIE_A.get(fora) or LOGOS_SERIE_A['flamengo']
            return {
                'casa': casa,
                'fora': fora,
                'placarCasa': p['gols_mandante'],
                'placarFora': p['gols_visitante'],
                'data': p['data'],
                'casaEscudo': esc_casa,
                'foraEscudo': esc_fora,
            }

        leg_ida = _leg(ida)
        leg_volta = _leg(volta) if volta else None

        gA = None if (leg_ida['placarCasa'] is None) else (
            leg_ida['placarCasa'] if ida['mandante'] == 'flamengo' else leg_ida['placarFora']
        )
        gB = None if (leg_ida['placarFora'] is None) else (
            leg_ida['placarFora'] if ida['mandante'] == 'flamengo' else leg_ida['placarCasa']
        )
        if leg_volta:
            if leg_volta['placarCasa'] is not None:
                gA = (gA or 0) + (leg_volta['placarCasa'] if volta['mandante'] == 'flamengo' else leg_volta['placarFora'])
            if leg_volta['placarFora'] is not None:
                gB = (gB or 0) + (leg_volta['placarFora'] if volta['mandante'] == 'flamengo' else leg_volta['placarCasa'])

        adv_norm = ida['visitante'] if ida['mandante'] == 'flamengo' else ida['mandante']
        adv_nome = NOMES_EXIBICAO.get(adv_norm, adv_norm.replace('-', ' ').title())

        # Só considera confrontos válidos de mata-mata (ida e volta com placar definido),
        # evitando lixo de páginas genéricas (ex.: uma única menção a um adversário).
        if leg_ida['placarCasa'] is None or not leg_volta or leg_volta['placarCasa'] is None:
            continue

        status = 'ENCERRADO'
        classificado = 'Flamengo' if gA > gB else adv_nome

        confrontos.append({
            'id': f"mata-mata-flamengo-{adv_norm.replace(' ', '-')}",
            'timeA': 'Flamengo',
            'timeB': adv_nome,
            'fase': 'Copa do Brasil',
            'data': leg_volta['data'] if leg_volta else leg_ida['data'],
            'ida': leg_ida,
            'volta': leg_volta,
            'agregado': {'timeA': gA, 'timeB': gB},
            'classificado': classificado,
            'status': status,
            'escudo': LOGOS_SERIE_A.get(adv_norm),
        })
    return confrontos


def obter_copa_do_brasil_espn():
    """Fonte ESPN Brasil para o chaveamento da Copa do Brasil (best-effort)."""
    html = _fetch_html(ESPN_COPA_BRASIL_URL)
    if not html:
        return []
    return _extrair_confrontos_de_html(html)


def obter_copa_do_brasil_lance():
    """Fonte Lance! para o chaveamento da Copa do Brasil (best-effort)."""
    html = _fetch_html(LANCE_COPA_BRASIL_URL)
    if not html:
        return []
    return _extrair_confrontos_de_html(html)


def normalizar_copa(cdb):
    """Garante que partidas passadas do Flamengo fiquem com status 'ENCERRADO',
    placares finais e o time classificado registrado. Recalcula agregado e
    classificado quando ausentes."""
    if not isinstance(cdb, dict):
        return cdb
    for c in cdb.get('confrontos', []):
        ida = c.get('ida') or {}
        volta = c.get('volta') or {}
        if ida.get('placarCasa') is None and volta.get('placarCasa') is None:
            c['status'] = 'A_DEFINIR'
            continue

        # placares por lado do Flamengo
        def _fla(g):
            return g['placarCasa'] if g.get('casa') == 'flamengo' else g['placarFora']

        def _adv(g):
            return g['placarFora'] if g.get('casa') == 'flamengo' else g['placarCasa']

        fla_ida = _fla(ida) if ida.get('placarCasa') is not None else None
        fla_volta = _fla(volta) if volta.get('placarCasa') is not None else None
        adv_ida = _adv(ida) if ida.get('placarCasa') is not None else None
        adv_volta = _adv(volta) if volta.get('placarCasa') is not None else None

        if fla_ida is None or adv_ida is None or fla_volta is None or adv_volta is None:
            # apenas uma das pernas foi jogada -> em andamento
            c['status'] = 'EM_ANDAMENTO'
            if c.get('agregado') is None:
                c['agregado'] = {'timeA': None, 'timeB': None}
            continue

        c['status'] = 'ENCERRADO'
        gA = fla_ida + fla_volta
        gB = adv_ida + adv_volta
        c['agregado'] = {'timeA': gA, 'timeB': gB}
        c['classificado'] = 'Flamengo' if gA > gB else (c.get('timeB') if gB > gA else None)
    return cdb


# ---------------------------------------------------------------------------
# MONTAGEM / PERSISTÊNCIA
# ---------------------------------------------------------------------------

def _converter_para_entrada(partida):
    """Converte uma partida interna (qualquer competição) para o schema do
    nextMatch.json. O status é definido pelo chamador conforme data/placar."""
    mandante = normalizar(partida.get('mandante') or '')
    visitante = normalizar(partida.get('visitante') or '')
    is_home = (mandante == 'flamengo')
    opponent = visitante if is_home else mandante
    home_score = partida.get('gols_mandante')
    away_score = partida.get('gols_visitante')
    escudo = (
        partida.get('escudo_visitante') if is_home else partida.get('escudo_mandante')
    ) or LOGOS_SERIE_A.get(opponent)
    if not escudo:
        escudo = LOGOS_SERIE_A['flamengo']
    slug = NOMES_EXIBICAO.get(opponent, opponent).lower().replace(' ', '-')
    return {
        'id': partida.get('id') or f"{(partida.get('data') or '')[:10]}-{slug}",
        'opponent': NOMES_EXIBICAO.get(opponent, opponent),
        'opponentLogo': escudo,
        'isHome': is_home,
        'date': partida['data'],
        'stadium': partida.get('estadio') or (
            'Maracanã - Rio de Janeiro, RJ' if is_home else 'A definir'
        ),
        'competition': partida.get('competition', 'Brasileirão'),
        'status': 'AGENDADO',
        'homeScore': home_score,
        'awayScore': away_score,
        'odds': None,
    }


def _partidas_de_copa():
    """Extrai as partidas do Flamengo (ida/volta) do chaveamento da Copa do Brasil."""
    dados = carregar_existentes(COPA_BRASIL_PATH)
    out = []
    if not isinstance(dados, dict):
        return out
    for c in dados.get('confrontos', []):
        for leg_nome in ('ida', 'volta'):
            leg = c.get(leg_nome)
            if not isinstance(leg, dict):
                continue
            casa = normalizar(leg.get('casa') or '')
            fora = normalizar(leg.get('fora') or '')
            if 'flamengo' not in (casa, fora):
                continue
            is_home = casa == 'flamengo'
            adv = fora if is_home else casa
            esc_adv = (
                leg.get('foraEscudo') if is_home else leg.get('casaEscudo')
            ) or LOGOS_SERIE_A.get(adv)
            out.append({
                'id': f"{c.get('id')}-{leg_nome}",
                'mandante': casa,
                'visitante': fora,
                'gols_mandante': leg.get('placarCasa'),
                'gols_visitante': leg.get('placarFora'),
                'data': leg.get('data'),
                'estadio': 'Maracanã - Rio de Janeiro, RJ' if is_home else 'A definir',
                'escudo_mandante': leg.get('casaEscudo'),
                'escudo_visitante': leg.get('foraEscudo'),
                'competition': 'Copa do Brasil',
            })
    return out


def _partidas_de_carioca():
    """Extrai os jogos do Flamengo no Carioca (estadual) a partir da classificação."""
    dados = carregar_existentes(CARIOCA_PATH)
    out = []
    jogos = []
    if isinstance(dados, dict):
        jogos = dados.get('flamengoJogos', [])
    for j in jogos:
        mandante = normalizar(j.get('mandante') or '')
        visitante = normalizar(j.get('visitante') or '')
        if 'flamengo' not in (mandante, visitante):
            continue
        is_home = mandante == 'flamengo'
        adv = visitante if is_home else mandante
        adv_nome = NOMES_EXIBICAO.get(adv, adv.replace('-', ' ').title())
        out.append({
            'id': j.get('id') or f"{(j.get('data') or '')[:10]}-{adv_nome.replace(' ', '-')}",
            'mandante': mandante,
            'visitante': visitante,
            'gols_mandante': j.get('placarMandante'),
            'gols_visitante': j.get('placarVisitante'),
            'data': j.get('data'),
            'estadio': j.get('estadio') or (
                'Maracanã - Rio de Janeiro, RJ' if is_home else 'A definir'
            ),
            'escudo_mandante': LOGOS_SERIE_A.get(mandante),
            'escudo_visitante': LOGOS_SERIE_A.get(visitante),
            'competition': 'Campeonato Carioca',
        })
    return out


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
    Gera e reescreve o nextMatch.json automaticamente a cada execução,
    considerando TODAS as competições (Brasileirão, Libertadores, Copa do Brasil
    e Campeonato Carioca):
    - Jogos encerrados -> matches.json (FINISHED)
    - Próximos confrontos -> nextMatch.json (AGENDADO, ordenados; o primeiro
      elemento é a próxima partida mais próxima da data atual)
    Fonte primária: Flashscore. Fallback oficial: ge.globo. Chaveamentos e
    estadual vêm dos respectivos arquivos JSON locais.
    """
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

    partidas_lib = None
    try:
        partidas_lib = obter_jogos_libertadores_flashscore()
    except Exception as e:
        log('WARN', f'Fonte primária (Flashscore/Libertadores) indisponível: {e}')

    if not partidas_lib:
        try:
            partidas_lib = obter_jogos_libertadores_ge()
            if origem is None:
                origem = 'GE (fallback)'
        except Exception as e2:
            log('WARN', f'Fallback (GE/Libertadores) indisponível: {e2}')
            partidas_lib = None

    copa = _partidas_de_copa()
    carioca = _partidas_de_carioca()

    partidas = list(partidas_br or []) + list(partidas_lib or []) + copa + carioca

    if not partidas:
        existentes = carregar_existentes()
        if existentes is not None:
            log('WARN', 'Fontes indisponíveis: reutilizando nextMatch.json existente.')
            save_json(existentes, JSON_PATH)
            return None
        log('WARN', 'Sem acesso às fontes e sem dados existentes: nada a atualizar.')
        return None

    agora = datetime.now(timezone.utc)
    resultados = []
    agenda = []
    for p in partidas:
        if not p.get('data'):
            continue
        ent = _converter_para_entrada(p)
        try:
            data = datetime.fromisoformat(p['data'])
        except Exception:
            continue
        jogado = (
            p.get('gols_mandante') is not None
            and p.get('gols_visitante') is not None
        )
        if data < agora or jogado:
            ent['status'] = 'FINISHED'
            resultados.append(ent)
        else:
            ent['status'] = 'AGENDADO'
            agenda.append(ent)

    resultados.sort(key=lambda x: x['date'], reverse=True)
    agenda.sort(key=lambda x: x['date'])

    def _dedup(lista):
        vistos = set()
        out = []
        for m in lista:
            if m['id'] in vistos:
                continue
            vistos.add(m['id'])
            out.append(m)
        return out

    resultados = _dedup(resultados)
    agenda = _dedup(agenda)

    save_json(agenda, JSON_PATH)
    save_json(resultados, MATCHES_PATH)
    log('SUCCESS', f'{len(resultados)} resultado(s) e {len(agenda)} agendado(s) registrados via {origem or "arquivos locais"}.')
    return agenda


def atualizar_odds():
    """Gera as odds (via odds_scraper) e anexa o campo 'odds' ao nextMatch.json."""
    try:
        import odds_scraper
        odds_scraper.main()
    except Exception as e:
        log('WARN', f'Falha ao gerar odds: {e}')
        return

    try:
        with open(ODDS_PATH, encoding='utf-8') as f:
            odds_data = json.load(f)
    except Exception:
        return

    por_id = {}
    for j in odds_data.get('jogos', []):
        if j.get('id'):
            por_id[j['id']] = j.get('odds')

    agenda = carregar_existentes(JSON_PATH)
    if not isinstance(agenda, list):
        return
    alterado = False
    for m in agenda:
        if m.get('id') in por_id:
            m['odds'] = por_id[m['id']]
            alterado = True
    if alterado:
        save_json(agenda, JSON_PATH)
        log('SUCCESS', f'Odds anexadas a {len(por_id)} jogo(s) no nextMatch.json.')


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


def atualizar_copa_do_brasil():
    """Atualiza o chaveamento da Copa do Brasil.

    Ordem de fontes (primeira que retornar dados válidos vence):
    ESPN Brasil -> Lance! -> ge.globo (fallback principal). O Flashscore permanece
    como tentativa adicional. Partidas passadas do Flamengo são normalizadas para
    status 'ENCERRADO' com placares finais e o time classificado. Se nenhuma fonte
    responder, reaproveita o arquivo existente (também normalizado)."""
    fontes = [
        ('ESPN Brasil', obter_copa_do_brasil_espn),
        ('Lance!', obter_copa_do_brasil_lance),
        ('Flashscore', obter_copa_do_brasil_flashscore),
        ('ge.globo', obter_copa_do_brasil_ge),
    ]
    confrontos = None
    origem = None
    for nome, fn in fontes:
        try:
            c = fn()
        except Exception as e:
            log('WARN', f'Fonte {nome} (Copa do Brasil) indisponível: {e}')
            continue
        if c and len(c) >= 2:
            confrontos = c
            origem = nome
            log('INFO', f'Copa do Brasil: dados obtidos via {nome}.')
            break
        log('WARN', f'Fonte {nome} (Copa do Brasil) não retornou dados.')

    # Fallback para o arquivo existente (mantém o cenário já consolidado)
    if not confrontos:
        existentes = carregar_existentes(COPA_BRASIL_PATH)
        if existentes:
            existentes = normalizar_copa(existentes)
            save_json(existentes, COPA_BRASIL_PATH)
            log('WARN', 'Chaveamento da Copa do Brasil mantido a partir dos dados existentes (normalizado).')
            return existentes.get('confrontos')
        return None

    # Preserva rodadas futuras ausentes na fonte (merge por id, fonte tem prioridade)
    existentes = carregar_existentes(COPA_BRASIL_PATH)
    por_id = {}
    if isinstance(existentes, dict) and existentes.get('confrontos'):
        for c in existentes['confrontos']:
            por_id[c['id']] = c
    for c in confrontos:
        por_id[c['id']] = c
    mesclados = list(por_id.values())
    mesclados = normalizar_copa({'fase': 'Copa do Brasil 2026', 'confrontos': mesclados})['confrontos']

    dados = {
        'fase': 'Copa do Brasil 2026',
        'atualizadoEm': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'confrontos': mesclados,
    }
    save_json(dados, COPA_BRASIL_PATH)
    log('SUCCESS', f'{len(mesclados)} confronto(s) de mata-mata da Copa do Brasil registrados via {origem}.')
    return mesclados


def _salvar_carioca(classificacao, flamengo_jogos, origem):
    dados = {
        'taca': 'Taça Guanabara 2026',
        'atualizadoEm': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'classificacao': classificacao or [],
        'flamengoJogos': flamengo_jogos or [],
    }
    save_json(dados, CARIOCA_PATH)
    log('SUCCESS', f'{len(dados["classificacao"])} time(s) na tabela do Carioca registrados via {origem}.')


def _mesclar_jogos(existentes, novos):
    """Combina listas de jogos do Flamengo, desduplicando por (data, mandante, visitante)."""
    mesclados = {}
    for j in list(existentes or []) + list(novos or []):
        chave = (j.get('data'), j.get('mandante'), j.get('visitante'))
        mesclados[chave] = j
    return list(mesclados.values())


def atualizar_carioca():
    """Atualiza a classificação da Taça Guanabara (Carioca) e os jogos do Flamengo.

    Ordem de fontes (primeira que retornar dados válidos vence):
    ESPN Brasil -> FERJ -> Lance! -> ge.globo (fallback principal). Os jogos do
    Flamengo no estadual são enriquecidos a partir do ge.globo (best-effort),
    independentemente da fonte da classificação. Se nenhuma fonte responder,
    reaproveita o arquivo existente."""
    fontes = [
        ('ESPN Brasil', obter_tabela_carioca_espn),
        ('FERJ', obter_tabela_carioca_ferj),
        ('Lance!', obter_tabela_carioca_lance),
        ('ge.globo', obter_tabela_carioca_ge),
    ]
    linhas = None
    origem = None
    for nome, fn in fontes:
        try:
            l = fn()
        except Exception as e:
            log('WARN', f'Fonte {nome} (Carioca) indisponível: {e}')
            continue
        if l and len(l) >= 6:
            linhas = l
            origem = nome
            log('INFO', f'Carioca: tabela obtida via {nome}.')
            break
        log('WARN', f'Fonte {nome} (Carioca) não retornou dados.')

    # Jogos do Flamengo no estadual (ge.globo, best-effort) — sempre tentado
    jogos = []
    try:
        jogos = obter_jogos_flamengo_carioca_ge()
    except Exception as e:
        log('WARN', f'Jogos do Flamengo no Carioca indisponíveis: {e}')

    if not linhas:
        existentes = carregar_existentes(CARIOCA_PATH)
        if existentes:
            classificacao = existentes['classificacao'] if isinstance(existentes, dict) else existentes
            jogos_existentes = existentes.get('flamengoJogos') if isinstance(existentes, dict) else []
            jogos = _mesclar_jogos(jogos_existentes, jogos)
            _salvar_carioca(classificacao, jogos, 'dados existentes (fallback)')
            return classificacao
        return None

    _salvar_carioca(linhas, jogos, origem)
    return linhas


if __name__ == "__main__":
    log('INFO', 'Iniciando atualização da agenda de jogos...')
    atualizar_agenda()
    atualizar_libertadores()
    atualizar_copa_do_brasil()
    atualizar_carioca()
    atualizar_odds()
