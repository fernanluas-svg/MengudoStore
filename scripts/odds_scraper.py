#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
odds_scraper.py - Raspa as odds (Match Odds / Probabilidades 1X2) dos próximos
jogos do Flamengo.

Abordagem moderna (anti-bot + adaptável):
  - Fetch com mimetização de Chrome real (curl_cffi / TLS spoofing) em vez de
    Selenium/Requests convencionais, driblando Cloudflare/Flashscore sem
    depender de um navegador headless (sem timeout de boot do Chrome).
  - Extração de odds por HEURÍSTICA DE CONTEÚDO (3 números decimais 1X2 em um
    mesmo bloco) em vez de classes CSS fixas (ex.: div.ui-table.oddsCell__odds),
    mantendo a leitura mesmo que o layout do Flashscore mude.
  - Fallback: se não houver rede/Cloudflare bloquear, gera odds
    representativas a partir de src/data/nextMatch.json, marcando fonte="fallback".

Saída: src/data/odds.json (formatado) + src/data/odds.csv (via pandas).
"""

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scraper_core as sc

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
    """Tenta extração adaptável de odds no FlashScore via fetch mimetizado.
    Retorna lista de dicts ou [] se não houver conteúdo (Cloudflare/sem JS)."""
    res = sc.fetch('https://www.flashscore.com/team/flamengo/fixtures/',
                   timeout=30, retries=3)
    if not res.ok:
        log('WARN', f'Flashscore indisponível ({res.engine}): {res.error}')
        return []
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'lxml')
    except Exception as e:
        log('WARN', f'Falha ao parsear Flashscore: {e}')
        return []

    entradas = []
    # Seletor adaptável: blocos com 3 números decimais (1X2) no mesmo texto,
    # independente da classe da tabela (ui-table, wcl-*, etc.).
    for tag, numbers, txt in sc.find_odds_rows(soup):
        if len(numbers) < 3:
            continue
        o1, ox, o2 = numbers[0], numbers[1], numbers[2]
        resto = sc.normalize(txt)
        for n in numbers:
            resto = resto.replace(str(n), ' ')
        casa = ' '.join([w for w in resto.split() if len(w) > 2])[:50] or 'desconhecida'
        entradas.append({
            'matchIdFlashscore': None,
            'home': None,
            'away': None,
            'odds': {'1': o1, 'X': ox, '2': o2},
            'bookmaker': casa,
            'source': 'flashscore',
        })
    return entradas


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
        log('SUCCESS', f'Scraping concluido: {len(entradas)} jogo(s).')
    else:
        log('WARN', 'Usando odds representativas (fallback) a partir do nextMatch.json.')
        entradas = odds_fallback(jogos)
        fonte = 'fallback'

    salvar(entradas, fonte)


if __name__ == '__main__':
    main()
