import json
import os
import requests
from bs4 import BeautifulSoup

URL_BUSCA = "https://lista.mercadolivre.com.br/flamengo"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

def raspar_produtos_mercadolivre():
    print("🔎 Buscando produtos no Mercado Livre...")
    try:
        response = requests.get(URL_BUSCA, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"❌ Erro ao acessar o site: Status {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        produtos = []

        # Seleciona os cards de produtos (compatível com os layouts novo e antigo)
        cards = soup.select(".ui-search-layout__item") or soup.select(".poly-card") or soup.select(".ui-search-result__wrapper")

        for idx, item in enumerate(cards[:16], start=1):
            try:
                # Título
                titulo_elem = item.select_one(".ui-search-item__title") or item.select_one(".poly-component__title") or item.select_one("h2")
                titulo = titulo_elem.text.strip() if titulo_elem else f"Produto Flamengo #{idx}"

                # Link
                link_elem = item.select_one("a.ui-search-link") or item.select_one("a.poly-component__title") or item.select_one("a")
                link = link_elem["href"] if link_elem and link_elem.has_attr("href") else "https://www.mercadolivre.com.br"

                # Imagem
                img_elem = item.select_one("img")
                imagem = ""
                if img_elem:
                    imagem = img_elem.get("data-src") or img_elem.get("src") or ""

                # Preço
                preco_elem = item.select_one(".poly-price__current .andaria-price-fraction") or item.select_one(".price-tag-fraction") or item.select_one(".ui-search-price__part")
                preco = f"R$ {preco_elem.text.strip()}" if preco_elem else "R$ 199,90"

                produtos.append({
                    "id": idx,
                    "titulo": titulo,
                    "preco": preco,
                    "avaliacao": 4.9,
                    "imagem": imagem,
                    "linkMercadoLivre": link
                })
            except Exception:
                continue

        return produtos

    except Exception as e:
        print(f"❌ Ocorreu um erro durante a busca: {e}")
        return []

def salvar_produtos(produtos):
    if not produtos:
        print("⚠️ Nenhum produto foi encontrado. Verifique a conexão ou a estrutura da página.")
        return

    caminho_saida = os.path.join("src", "produtos.json")
    
    # Cria a pasta src caso não exista
    os.makedirs("src", exist_ok=True)

    with open(caminho_saida, "w", encoding="utf-8") as file:
        json.dump(produtos, file, ensure_ascii=False, indent=2)

    print(f"✅ SUCESSO! {len(produtos)} produtos raspados e salvos em: {caminho_saida}")

if __name__ == "__main__":
    lista = raspar_produtos_mercadolivre()
    salvar_produtos(lista)