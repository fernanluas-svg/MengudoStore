import json
import os


# Caminho para salvar o JSON dentro da estrutura do Mengudo Store
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, '../src/data/nextMatch.json')


def fetch_and_format_matches():
    """
    Função para estruturar os dados das partidas (mando, data, estádio, status e placares).
    """
    matches_data = [
        {
            "id": "2026-08-22-cruzeiro",
            "opponent": "Cruzeiro",
            "opponentLogo": "/logos/cruzeiro.svg",
            "isHome": False,
            "date": "2026-08-22T20:30:00-03:00",
            "stadium": "Mineirão - Belo Horizonte, MG",
            "competition": "Brasileirão",
            "status": "SCHEDULED",
            "homeScore": None,
            "awayScore": None
        },
        {
            "id": "2026-08-30-botafogo",
            "opponent": "Botafogo",
            "opponentLogo": "/logos/botafogo.svg",
            "isHome": True,
            "date": "2026-08-30T16:00:00-03:00",
            "stadium": "Maracanã - Rio de Janeiro, RJ",
            "competition": "Brasileirão",
            "status": "SCHEDULED",
            "homeScore": None,
            "awayScore": None
        },
        {
            "id": "2026-09-06-remo",
            "opponent": "Remo",
            "opponentLogo": "/logos/remo.svg",
            "isHome": False,
            "date": "2026-09-06T16:00:00-03:00",
            "stadium": "Baenão - Belém, PA",
            "competition": "Brasileirão",
            "status": "SCHEDULED",
            "homeScore": None,
            "awayScore": None
        }
    ]
    return matches_data


def save_json(data):
    """Garante que a pasta exista e escreve o arquivo JSON atualizado."""
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Agenda atualizada com sucesso em: {JSON_PATH}")


if __name__ == "__main__":
    print("🚀 Iniciando atualização da agenda de jogos...")
    data = fetch_and_format_matches()
    save_json(data)