#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
odds_scraper.py - Raspa as odds (Match Odds / Probabilidades 1X2) dos próximos
jogos do Flamengo.

Abordagem moderna (sem dependência de JS/Flashscore):
  - Prioriza fontes com HTML pronto ou APIs diretas:
    1. ge.globo (página de odds / API pública)
    2. ESPN Brasil (página de odds do campeonato)
    3. Betfair/Outras via endpoints públicos
  - Extração adaptável por HEURÍSTICA DE CONTEÚDO (3 números decimais 1X2)
  - Fallback: odds representativas a partir de src/data/nextMatch.json

Saída: src/data/odds.json (formatado) + src/data/odds.csv (via pandas).
"""

import json
import os
import sys
import re
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scraper_core as sc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEXT_MATCH_PATH = os.path.join(BASE_DIR, '../src/data/nextMatch.json')
ODDS_PATH = os.path.join(BASE_DIR, '../src/data/odds.json')
CSV_PATH = os.path.join(BASE_DIR, '../src/data/odds.csv')

FLAMENGO = 'Flamengo'
PREFER_BOOKMAKERS = ['bet365', 'betfair', 'pinnacle', '1xbet', 'betano', 'sportingbet']

# URLs de fontes alternativas para odds
GE_ODDS_URL = 'https://ge.globo.com/futebol/brasileirao-serie-a/odds/'
ESPN_SCOREBOARD_URL = 'https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard'
BETFAIR_API_URL = 'https://www.betfair.com.br/sport/football/competitions'

ODD_RE = re.compile(r'([0-9]{1,3}(?:[.][0-9]{2,3})?)')

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

ALIASES_EQUIPES = {
    'atletico': 'atletico mineiro',
    'atletico mg': 'atletico mineiro',
    'athletico': 'atletico paranaense',
    'athletico pr': 'atletico paranaense',
    'athletico paranaense': 'atletico paranaense',
    'vasco': 'vasco da gama',
    'bragantino': 'red bull bragantino',
}


def log(nivel, msg):
    print(f'[{nivel}] {msg}')


def normalizar(texto):
    import unicodedata
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[_-]+', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip().lower()
    if texto in ALIASES_EQUIPES:
        texto = ALIASES_EQUIPES[texto]
    texto = texto.replace('athletico', 'atletico')
    return texto


def carregar_jogos_flamengo():
    with open(NEXT_MATCH_PATH, 'r', encoding='utf-8') as f:
        jogos = json.load(f)
    return [j for j in jogos if j.get('status') in ('SCHEDULED', 'AGENDADO')]


def escolher_melhor_casa(odds_lista):
    if not isinstance(odds_lista, list):
        return None
    for preferida in PREFER_BOOKMAKERS:
        for odd in odds_lista:
            if isinstance(odd, dict) and preferida in str(odd.get('bookmaker', '')).lower():
                return odd
    return odds_lista[0] if odds_lista else None


def odds_fallback(jogos):
    resultado = []
    for j in jogos:
        if j.get('isHome'):
            o1, ox, o2 = 1.70, 3.40, 5.50
        else:
            o1, ox, o2 = 2.60, 3.20, 2.70
        resultado.append({
            'id': j.get('id'),
            'opponent': j.get('opponent'),
            'isHome': j.get('isHome'),
            'date': j.get('date'),
            'competition': j.get('competition'),
            'odds': {'1': o1, 'X': ox, '2': o2},
            'bookmaker': 'fallback',
            'source': 'fallback',
        })
    return resultado


def extrair_odds_do_texto(texto):
    """Extrai 3 odds (1, X, 2) de um texto usando regex."""
    if not texto:
        return None
    numeros = []
    for m in ODD_RE.finditer(texto):
        try:
            val = float(m.group(1))
            if 1.01 <= val <= 100.0:
                numeros.append(val)
        except ValueError:
            continue
    if len(numeros) >= 3:
        return numeros[:3]
    return None


def similaridade(a, b):
    """Calcula similaridade simples entre duas strings (Jaccard em tokens)."""
    ta = set(a.split())
    tb = set(b.split())
    if not ta or not tb:
        return 0.0
    inter = ta & tb
    union = ta | tb
    return len(inter) / len(union)


def encontrar_linhas_odds(soup):
    """Localiza elementos com 3+ odds decimais no HTML (heurística de conteúdo)."""
    encontrados = []
    for tag in soup.find_all(True):
        txt = tag.get_text(' ', strip=True)
        if not txt or len(txt) > 500:
            continue
        odds = extrair_odds_do_texto(txt)
        if odds:
            # tenta identificar a casa de apostas no texto
            casa = 'desconhecida'
            for pref in PREFER_BOOKMAKERS:
                if pref in txt.lower():
                    casa = pref
                    break
            encontrados.append((tag, odds, txt, casa))
    return encontrados


def encontrar_melhor_jogo(txt_norm, jogos_norm):
    """Encontra o melhor jogo correspondente usando fuzzy matching."""
    melhor_jogo = None
    melhor_score = 0.0
    
    for adv_norm, jogo in jogos_norm.items():
        # Nomes para comparar
        nomes_adv = [
            adv_norm,
            NOMES_EXIBICAO.get(adv_norm, '').lower(),
            adv_norm.replace(' ', '-'),
        ]
        
        for nome in nomes_adv:
            score = similaridade(nome, txt_norm)
            if score > melhor_score and score > 0.3:  # threshold mínimo
                melhor_score = score
                melhor_jogo = (adv_norm, jogo)
    
    return melhor_jogo


def raspar_ge_odds(jogos):
    """Tenta extrair odds da página de odds do ge.globo."""
    res = sc.fetch(GE_ODDS_URL, timeout=30, retries=2)
    if not res.ok:
        log('WARN', f'ge.globo odds indisponível ({res.engine}): {res.error}')
        return []
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'lxml')
    except Exception as e:
        log('WARN', f'Falha ao parsear ge.globo odds: {e}')
        return []

    linhas = encontrar_linhas_odds(soup)
    if not linhas:
        log('WARN', 'Nenhuma linha de odds encontrada no ge.globo')
        return []

    entradas = []
    jogos_norm = {normalizar(j['opponent']): j for j in jogos}
    
    for tag, odds_vals, txt, casa in linhas:
        txt_norm = sc.normalize(txt)
        
        match = encontrar_melhor_jogo(txt_norm, jogos_norm)
        if not match:
            continue
            
        adv_norm, jogo_meta = match
        is_home = jogo_meta.get('isHome', True)
        
        if is_home:
            o1, ox, o2 = odds_vals[0], odds_vals[1], odds_vals[2]
        else:
            o1, ox, o2 = odds_vals[2], odds_vals[1], odds_vals[0]
        
        entradas.append({
            'id': jogo_meta.get('id'),
            'opponent': jogo_meta.get('opponent'),
            'isHome': is_home,
            'date': jogo_meta.get('date'),
            'competition': jogo_meta.get('competition'),
            'odds': {'1': o1, 'X': ox, '2': o2},
            'bookmaker': casa,
            'source': 'ge.globo',
        })
    
    log('INFO', f'ge.globo: {len(entradas)} odds extraídas')
    return entradas


def converter_odds_americana(american):
    """Converte odds no formato americano (ex.: '+210', '-165') em decimais."""
    if american is None:
        return None
    s = str(american).strip()
    if not s:
        return None
    sinal = 1
    if s.startswith('+'):
        s = s[1:]
    elif s.startswith('-'):
        sinal = -1
        s = s[1:]
    try:
        val = float(s)
    except ValueError:
        return None
    if val == 0:
        return None
    if sinal < 0:
        return round((100.0 / abs(val)) + 1.0, 2)
    return round((val / 100.0) + 1.0, 2)


def raspar_espn_odds(jogos):
    """Extrai odds REAIS (DraftKings via API JSON da ESPN) dos jogos do Flamengo.

    Usa a API de scoreboard da ESPN, que entrega as cotações 1X2 (moneyline)
    prontas em JSON, sem necessidade de renderizar JS. As odds vêm no formato
    americano e são convertidas para decimais.
    """
    from datetime import timedelta

    # Agrupa jogos por data (fuso Brasil, -3h do UTC) para consultar a API 1x por rodada
    jogos_por_data = {}
    for j in jogos:
        try:
            dt = datetime.fromisoformat(j['date'])
        except Exception:
            continue
        br = dt - timedelta(hours=3)
        chave = br.strftime('%Y%m%d')
        jogos_por_data.setdefault(chave, []).append(j)

    entradas = []
    cache = {}
    for chave, jogos_dia in jogos_por_data.items():
        if chave in cache:
            data = cache[chave]
        else:
            url = f'{ESPN_SCOREBOARD_URL}?dates={chave}'
            res = sc.fetch(url, timeout=30, retries=2)
            if not res.ok:
                log('WARN', f'ESPN scoreboard indisponível ({res.engine}): {res.error}')
                cache[chave] = None
                continue
            try:
                data = json.loads(res.text)
            except Exception as e:
                log('WARN', f'Falha ao parsear JSON da ESPN: {e}')
                cache[chave] = None
                continue
            cache[chave] = data

        if not data:
            continue

        for j in jogos_dia:
            adv_norm = normalizar(j['opponent'])
            for ev in data.get('events', []):
                comp = ev.get('competitions', [{}])[0]
                odds_list = [o for o in (comp.get('odds') or []) if isinstance(o, dict)]
                if not odds_list:
                    continue

                times = {}
                for c in comp.get('competitors', []):
                    nome = normalizar(c.get('team', {}).get('displayName', ''))
                    times[nome] = c

                if 'flamengo' not in times or adv_norm not in times:
                    continue

                ml = odds_list[0].get('moneyline', {})
                home_odd = (ml.get('home', {}).get('close') or {}).get('odds')
                away_odd = (ml.get('away', {}).get('close') or {}).get('odds')
                draw_odd = (ml.get('draw', {}).get('close') or {}).get('odds')
                if home_odd is None:
                    home_odd = (ml.get('home', {}).get('open') or {}).get('odds')
                if away_odd is None:
                    away_odd = (ml.get('away', {}).get('open') or {}).get('odds')
                if draw_odd is None:
                    draw_odd = (ml.get('draw', {}).get('open') or {}).get('odds')

                fla_is_home = times.get('flamengo', {}).get('homeAway') == 'home'
                if fla_is_home:
                    o1 = converter_odds_americana(home_odd)
                    o2 = converter_odds_americana(away_odd)
                else:
                    o1 = converter_odds_americana(away_odd)
                    o2 = converter_odds_americana(home_odd)
                ox = converter_odds_americana(draw_odd)

                if None in (o1, o2, ox):
                    continue

                entradas.append({
                    'id': j.get('id'),
                    'opponent': j.get('opponent'),
                    'isHome': j.get('isHome', True),
                    'date': j.get('date'),
                    'competition': j.get('competition'),
                    'odds': {'1': o1, 'X': ox, '2': o2},
                    'bookmaker': (odds_list[0].get('provider') or {}).get('name', 'DraftKings'),
                    'source': 'ESPN (DraftKings)',
                })
                break

    log('INFO', f'ESPN (DraftKings): {len(entradas)} odds extraídas')
    return entradas


def raspar_betfair_odds(jogos):
    """Tenta extrair odds da Betfair (página do Brasileirão)."""
    # URL específica do Brasileirão na Betfair
    betfair_brasileirao = 'https://www.betfair.com.br/sport/football/brazilian-serie-a/102323'
    res = sc.fetch(betfair_brasileirao, timeout=30, retries=2)
    if not res.ok:
        log('WARN', f'Betfair Brasileirão indisponível ({res.engine}): {res.error}')
        return []
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'lxml')
    except Exception as e:
        log('WARN', f'Falha ao parsear Betfair Brasileirão: {e}')
        return []

    linhas = encontrar_linhas_odds(soup)
    if not linhas:
        log('WARN', 'Nenhuma linha de odds encontrada na Betfair Brasileirão')
        return []

    entradas = []
    jogos_norm = {normalizar(j['opponent']): j for j in jogos}
    
    for tag, odds_vals, txt, casa in linhas:
        txt_norm = sc.normalize(txt)
        
        match = encontrar_melhor_jogo(txt_norm, jogos_norm)
        if not match:
            continue
            
        adv_norm, jogo_meta = match
        is_home = jogo_meta.get('isHome', True)
        
        if is_home:
            o1, ox, o2 = odds_vals[0], odds_vals[1], odds_vals[2]
        else:
            o1, ox, o2 = odds_vals[2], odds_vals[1], odds_vals[0]
        
        entradas.append({
            'id': jogo_meta.get('id'),
            'opponent': jogo_meta.get('opponent'),
            'isHome': is_home,
            'date': jogo_meta.get('date'),
            'competition': jogo_meta.get('competition'),
            'odds': {'1': o1, 'X': ox, '2': o2},
            'bookmaker': casa or 'betfair',
            'source': 'Betfair',
        })
    
    log('INFO', f'Betfair Brasileirão: {len(entradas)} odds extraídas')
    return entradas


def raspar_flashscore_odds(jogos):
    """Extrai odds do Flashscore via o campo MW embutido no HTML (sem JS).

    O Flashscore embute os dados das partidas em um formato proprietário de
    texto no HTML (não requer renderização de JS). Cada partida tem campos como
    CX (nome do mandante), AD (timestamp), MW (odds 1X2 de múltiplas casas).
    O campo MW é uma lista pipe-separated onde pares (bookmaker_id, odd) aparecem
    após um cabeçalho. As odds estão em centésimos (ex.: 933 = 9.33).
    """
    res = sc.fetch('https://www.flashscore.com.br/futebol/brasil/serie-a/',
                   timeout=30, retries=2)
    if not res.ok:
        log('WARN', f'Flashscore indisponível ({res.engine}): {res.error}')
        return []

    text = res.text
    # Extrai blocos de partida: procuramos por "CX":"<Time>" seguido de dados
    # A estrutura: ~AA<id>AD<ts>...CX<NomedoMandante>...MW<odds>...
    entradas = []
    jogos_norm = {normalizar(j['opponent']): j for j in jogos}

    # Regex para capturar um bloco de partida com CX (mandante) e MW (odds)
    # Padrão: CX\"<time>\" ... MW\"<numeros pipe-separated>\"
    padrao = re.compile(
        r'CX\\?\"([^\"\\]+)\\\"[^~]*?'
        r'(?:CY\\?\"([^\"\\]+)\\\")?'
        r'.*?MW\\?\"([0-9|]+)\\\"',
        re.DOTALL
    )

    for m in padrao.finditer(text):
        mandante = m.group(1)
        visitante = m.group(2) or ''
        mw_raw = m.group(3) or ''

        # Converte para normalizado para matching
        mandante_norm = normalizar(mandante)
        visitante_norm = normalizar(visitante)

        # Determina se é jogo do Flamengo e qual o adversário
        flamengo_eh_mandante = 'flamengo' in mandante_norm
        flamengo_eh_visitante = 'flamengo' in visitante_norm

        if not (flamengo_eh_mandante or flamengo_eh_visitante):
            continue

        if flamengo_eh_mandante:
            adv_norm = visitante_norm
            is_home = True
        else:
            adv_norm = mandante_norm
            is_home = False

        # Verifica se o adversário está na lista de jogos do Flamengo
        if adv_norm not in jogos_norm:
            continue

        # Parseia o MW: formato é uma lista de números separados por |
        # O primeiro número parece ser um contador, depois vêm pares
        # (bookmaker_id, odd_em_centesimos)
        nums = [int(x) for x in mw_raw.split('|') if x.strip()]
        if len(nums) < 3:
            continue

        # Remove o primeiro número (contador) e processa pares
        rest = nums[1:] if len(nums) > 1 else nums
        odds_extraidas = []
        i = 0
        while i + 1 < len(rest):
            bookmaker_id = rest[i]
            odd_valor = rest[i + 1]
            # Odds em centésimos: 933 -> 9.33
            odds_extraidas.append(odd_valor / 100.0 if odd_valor > 100 else float(odd_valor))
            i += 2

        if len(odds_extraidas) < 3:
            continue

        # No Flashscore, a ordem das odds MW é: 1 (mandante), X, 2 (visitante)
        o1, ox, o2 = odds_extraidas[0], odds_extraidas[1], odds_extraidas[2]

        if not is_home:
            # Flamengo é visitante: odds[2] é o Flamengo
            o1, ox, o2 = o2, ox, o1

        jogo_meta = jogos_norm[adv_norm]
        entradas.append({
            'id': jogo_meta.get('id'),
            'opponent': jogo_meta.get('opponent'),
            'isHome': is_home,
            'date': jogo_meta.get('date'),
            'competition': jogo_meta.get('competition'),
            'odds': {'1': round(o1, 2), 'X': round(ox, 2), '2': round(o2, 2)},
            'bookmaker': 'flashscore-mw',
            'source': 'Flashscore',
        })

    log('INFO', f'Flashscore: {len(entradas)} odds extraídas do campo MW')
    return entradas


def mesclar_com_metadata(scraped, jogos):
    """Anexa metadados do nextMatch.json às odds raspadas."""
    resultado = []
    for item in scraped:
        if item.get('id'):
            # Já tem ID do nextMatch, só garante os campos
            meta = next((j for j in jogos if j.get('id') == item['id']), None)
            if meta:
                item.update({
                    'opponent': meta.get('opponent'),
                    'isHome': meta.get('isHome'),
                    'date': meta.get('date'),
                    'competition': meta.get('competition'),
                })
        resultado.append(item)
    return resultado


def deduplicar_odds(entradas):
    """Remove duplicatas mantendo a melhor casa de apostas."""
    por_id = {}
    for e in entradas:
        key = e.get('id')
        if not key:
            continue
        if key not in por_id:
            por_id[key] = e
        else:
            # Prefere fonte não-fallback, depois casa preferida
            atual = por_id[key]
            if atual.get('source') == 'fallback' and e.get('source') != 'fallback':
                por_id[key] = e
            elif atual.get('source') != 'fallback' and e.get('source') != 'fallback':
                if escolher_melhor_casa([e]) == e:
                    por_id[key] = e
    return list(por_id.values())


def salvar(jogos, fonte):
    os.makedirs(os.path.dirname(ODDS_PATH), exist_ok=True)
    conteudo = {
        'atualizadoEm': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'fonte': fonte,
        'jogos': jogos,
    }
    def _sanitizar(obj):
        if isinstance(obj, dict):
            return {k: _sanitizar(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_sanitizar(v) for v in obj]
        if isinstance(obj, float) and (obj != obj or obj in (float('inf'), float('-inf'))):
            return None
        return obj

    with open(ODDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(_sanitizar(conteudo), f, ensure_ascii=False, indent=2, allow_nan=False)
    log('SUCCESS', f'Arquivo gerado em: {ODDS_PATH} ({len(jogos)} jogo(s), fonte={fonte})')

    try:
        import pandas as pd
        linhas = []
        for j in jogos:
            linhas.append({
                'id': j.get('id'),
                'opponent': j.get('opponent'),
                'isHome': j.get('isHome'),
                'date': j.get('date'),
                'competition': j.get('competition'),
                'odd_1': j['odds']['1'],
                'odd_x': j['odds']['X'],
                'odd_2': j['odds']['2'],
                'bookmaker': j.get('bookmaker'),
                'source': j.get('source'),
            })
        pd.DataFrame(linhas).to_csv(CSV_PATH, index=False, encoding='utf-8')
        log('SUCCESS', f'CSV auxiliar gerado em: {CSV_PATH}')
    except Exception as e:
        log('WARN', f'Nao foi possivel gerar CSV (pandas): {e}')


def main():
    log('INFO', 'Iniciando raspagem de odds dos proximos jogos do Flamengo...')
    jogos = carregar_jogos_flamengo()
    log('INFO', f'{len(jogos)} jogo(s) agendado(s) do Flamengo encontrado(s).')

    # Base: odds representativas para TODOS os jogos (garante cobertura total)
    todas_entradas = odds_fallback(jogos)
    fonte_principal = 'fallback'
    tem_real = False

    # 1. Tenta ge.globo (fonte principal brasileira)
    entradas_ge = raspar_ge_odds(jogos)
    if entradas_ge:
        todas_entradas.extend(entradas_ge)
        fonte_principal = 'ge.globo'
        tem_real = True

    # 2. Tenta ESPN (API JSON com odds reais da DraftKings, sem JS)
    entradas_espn = raspar_espn_odds(jogos)
    if entradas_espn:
        todas_entradas.extend(entradas_espn)
        if not tem_real:
            fonte_principal = 'ESPN (DraftKings)'
        tem_real = True

    # 3. Tenta Flashscore (campo MW no HTML, sem dependência de JS)
    entradas_flashscore = raspar_flashscore_odds(jogos)
    if entradas_flashscore:
        todas_entradas.extend(entradas_flashscore)
        if not tem_real:
            fonte_principal = 'Flashscore'
        tem_real = True

    # 4. Tenta Betfair (complementar)
    entradas_betfair = raspar_betfair_odds(jogos)
    if entradas_betfair:
        todas_entradas.extend(entradas_betfair)
        if not tem_real:
            fonte_principal = 'Betfair'
        tem_real = True

    # Deduplica (real sobrescreve fallback) e mescla com metadados
    todas_entradas = deduplicar_odds(todas_entradas)
    todas_entradas = mesclar_com_metadata(todas_entradas, jogos)
    if tem_real:
        log('SUCCESS', f'Scraping concluido: {len(todas_entradas)} jogo(s) (odds reais sobrepostas ao fallback).')
    else:
        log('WARN', 'Nenhuma fonte de odds reais disponível. Usando odds representativas (fallback).')

    salvar(todas_entradas, fonte_principal)


if __name__ == '__main__':
    main()