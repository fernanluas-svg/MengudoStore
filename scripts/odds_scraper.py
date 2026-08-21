#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
odds_scraper.py - Raspa as odds (Match Odds / Probabilidades 1X2) dos próximos
jogos do Flamengo, baseado nos módulos do Fut Python Trader (FlashScore Scraper).

Abordagem (espelhada do repositório futpythontrader/YouTube):
  - Selenium + webdriver-manager para dirigir o FlashScore (flashscore.com).
  - Extração das odds 1X2 (Vitória Mandante "1", Empate "X", Vitória Visitante "2")
    e seleção da casa de apostas preferencial (Bet365 > Betfair > primeira).
  - Fallback: se não houver navegador/rede (ex.: ambiente sem Chrome), gera odds
    representativas a partir de src/data/nextMatch.json, marcando fonte="fallback".

Saída: src/data/odds.json (formatado) + src/data/odds.csv (via pandas).
"""

import json
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEXT_MATCH_PATH = os.path.join(BASE_DIR, '../src/data/nextMatch.json')
ODDS_PATH = os.path.join(BASE_DIR, '../src/data/odds.json')
CSV_PATH = os.path.join(BASE_DIR, '../src/data/odds.csv')

FLAMENGO = 'Flamengo'
PREFER_BOOKMAKERS = ['bet365', 'betfair']


def log(nivel, msg):
    print(f'[{nivel}] {msg}')


def carregar_jogos_flamengo():
    with open(NEXT_MATCH_PATH, 'r', encoding='utf-8') as f:
        jogos = json.load(f)
    return [j for j in jogos if j.get('status') == 'SCHEDULED']


def escolher_melhor_casa(odds_lista):
    if not isinstance(odds_lista, list):
        return None
    for preferida in PREFER_BOOKMAKERS:
        for odd in odds_lista:
            if isinstance(odd, dict) and preferida in str(odd.get('Bookmaker', '')).lower():
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
            'matchIdFlashscore': None,
            'source': 'fallback',
        })
    return resultado


def raspar_flashscore(jogos):
    """Tenta scraping real no FlashScore. Retorna lista de dicts ou [] se falhar."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
    except Exception as e:
        log('WARN', f'Dependencias de scraping indisponiveis: {e}')
        return []

    try:
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('useAutomationExtension', False)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        log('WARN', f'Nao foi possivel iniciar o navegador: {e}')
        return []

    try:
        ids = obter_ids_proximos_flamengo(driver)
        if not ids:
            log('WARN', 'Nenhum id de partida do Flamengo descoberto no FlashScore.')
            return []

        entradas = []
        for mid in ids:
            odds = extrair_odds_1x2(driver, mid)
            if odds:
                entradas.append(odds)
        return entradas
    except Exception as e:
        log('ERROR', f'Falha no scraping do FlashScore: {e}')
        return []
    finally:
        driver.quit()


def obter_ids_proximos_flamengo(driver):
    """Best-effort: coleta ids das proximas partidas do Flamengo no FlashScore."""
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from bs4 import BeautifulSoup

        driver.get('https://www.flashscore.com/team/flamengo/fixtures/')
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.event__match'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return [
            elem.get('data-id')
            for elem in soup.select('div.event__match')
            if elem.get('data-id')
        ]
    except Exception:
        return []


def extrair_odds_1x2(driver, match_id):
    """Extrai odds 1X2 FT de uma partida (baseado no Fut Python Trader)."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup

    url = f'https://www.flashscore.com/match/{match_id}/#/match-summary/odds/1x2/full-time'
    driver.get(url)
    try:
        WebDriverWait(driver, 12).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.ui-table.oddsCell__odds'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.select_one('div.ui-table.oddsCell__odds')
        if not table:
            return None

        odds_lista = []
        for linha in table.select('div.ui-table__row'):
            logo = linha.select_one('div.wcl-bookmakerLogo_4IUU0 a img')
            if not logo:
                continue
            casa = (logo.get('title') or logo.get('alt', '')).strip()
            celulas = linha.select('a.oddsCell__odd')
            if len(celulas) < 3:
                continue
            try:
                o1 = o2 = ox = None
                for i, celula in enumerate(celulas[:3]):
                    if celula.select('span.oddsCell__lineThrough'):
                        continue
                    span = celula.select_one('span')
                    if not span:
                        continue
                    valor = float(span.text.strip().replace(',', '.'))
                    if i == 0:
                        o1 = valor
                    elif i == 1:
                        ox = valor
                    elif i == 2:
                        o2 = valor
                if o1 or ox or o2:
                    odds_lista.append({'Bookmaker': casa, 'Odd_1': o1, 'Odd_X': ox, 'Odd_2': o2})
            except Exception:
                continue

        melhor = escolher_melhor_casa(odds_lista)
        if not melhor:
            return None

        return {
            'matchIdFlashscore': match_id,
            'home': None,
            'away': None,
            'odds': {
                '1': melhor.get('Odd_1'),
                'X': melhor.get('Odd_X'),
                '2': melhor.get('Odd_2'),
            },
            'bookmaker': melhor.get('Bookmaker'),
            'source': 'flashscore',
        }
    except Exception:
        return None


def mesclar_com_metadata(scraped, jogos):
    """Anexa id/date/competition/opponent do nextMatch.json às odds raspadas."""
    resultado = []
    for item in scraped:
        meta = None
        for j in jogos:
            if {item.get('home'), item.get('away')} == {FLAMENGO, j.get('opponent')}:
                meta = j
                break
        if meta:
            item.update({
                'id': meta.get('id'),
                'opponent': meta.get('opponent'),
                'isHome': meta.get('isHome'),
                'date': meta.get('date'),
                'competition': meta.get('competition'),
            })
        else:
            item.setdefault('id', item.get('matchIdFlashscore'))
            item.setdefault('opponent', item.get('away') if item.get('home') == FLAMENGO else item.get('home'))
            item.setdefault('isHome', item.get('home') == FLAMENGO)
            item.setdefault('date', None)
            item.setdefault('competition', None)
        resultado.append(item)
    return resultado


def salvar(jogos, fonte):
    os.makedirs(os.path.dirname(ODDS_PATH), exist_ok=True)
    conteudo = {
        'atualizadoEm': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'fonte': fonte,
        'jogos': jogos,
    }
    with open(ODDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(conteudo, f, ensure_ascii=False, indent=2)
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

    entradas = raspar_flashscore(jogos)
    if entradas:
        fonte = 'flashscore'
        entradas = mesclar_com_metadata(entradas, jogos)
        log('SUCCESS', f'Scraping real concluido: {len(entradas)} jogo(s).')
    else:
        log('WARN', 'Usando odds representativas (fallback) a partir do nextMatch.json.')
        entradas = odds_fallback(jogos)
        fonte = 'fallback'

    salvar(entradas, fonte)


if __name__ == '__main__':
    main()
