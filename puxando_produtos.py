import json
import os
import requests
from datetime import datetime

# URL da API com parâmetros
URL_API = "https://api.mercadolibre.com/sites/MLB/search"
PARAMS = {
    "q": "flamengo",
    "limit": 20,
    "offset": 0
}

# Headers para parecer um navegador (o que pode evitar o 403)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "X-Client-Id": "12345"  # <--- Adicione esta linha
}

def buscar_produtos_api():
    print("🔎 Buscando produtos via API do Mercado Livre...")

    try:
        # Faz a requisição com os headers de navegador
        response = requests.get(URL_API, params=PARAMS, headers=HEADERS, timeout=15)

        if response.status_code != 200:
            print(f"❌ Erro na API: Status {response.status_code}")
            print(f"   Mensagem: {response.text}")  # Mostra o que o ML devolveu
            return []

        dados = response.json()
        resultados = dados.get("results", [])

        if not resultados:
            print("⚠️ Nenhum produto encontrado na API")
            return []

        produtos = []
        for idx, item in enumerate(resultados, start=1):
            # Formata o preço
            preco_float = item.get("price", 0)
            preco = f"R$ {preco_float:.2f}".replace(".", ",")

            # Pega a imagem (thumbnail)
            imagem = item.get("thumbnail", "")
            if imagem and "http" not in imagem:
                imagem = "https:" + imagem

            # Título
            titulo = item.get("title", f"Produto #{idx}")

            # Link
            link = item.get("permalink", "https://www.mercadolivre.com.br")

            produtos.append({
                "id": idx,
                "titulo": titulo,
                "preco": preco,
                "avaliacao": 4.5,
                "imagem": imagem,
                "linkMercadoLivre": link
            })

            print(f"  ✅ {idx}: {titulo[:40]}... - {preco}")

        return produtos

    except Exception as e:
        print(f"❌ Erro ao buscar da API: {e}")
        return []

def salvar_produtos(produtos):
    if not produtos:
        print("⚠️ Nenhum produto foi encontrado. Verifique a conexão ou a estrutura da página.")
        return

    pasta_frontend = os.path.join("frontend")
    os.makedirs(pasta_frontend, exist_ok=True)

    caminho_json = os.path.join(pasta_frontend, "produtos.json")
    caminho_js = os.path.join(pasta_frontend, "produtos.js")

    with open(caminho_json, "w", encoding="utf-8") as file:
        json.dump(produtos, file, ensure_ascii=False, indent=2)

    with open(caminho_js, "w", encoding="utf-8") as file:
        file.write(f"// Produtos atualizados em {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        file.write(f"const produtos = {json.dumps(produtos, ensure_ascii=False, indent=2)};\n")

    print(f"\n✅ SUCESSO! {len(produtos)} produtos salvos em:")
    print(f"   📄 {caminho_json}")
    print(f"   📄 {caminho_js}")

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 MENGUDOSTORE - Buscador de Produtos (API)")
    print("=" * 50)

    produtos = buscar_produtos_api()
    salvar_produtos(produtos)

    print("=" * 50)
    print("🏁 Processo finalizado!")