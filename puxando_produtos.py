import json
import os
import requests
from bs4 import BeautifulSoup

# URL de busca ou lista do Mercado Livre com os produtos do Flamengo
# Você pode colar aqui o link de uma busca do Mercado Livre (ex: ofertas do Flamengo)
URL_BUSCA = "https://lista.mercadolivre.com.br/flamengo"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def raspar_produtos_mercadolivre():
    print(f"🔎 Buscando produtos no Mercado Livre...")
    response = requests.get(URL_BUSCA, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"❌ Erro ao acessar o site: Status {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    produtos = []
    
    # Encontra os cards de produtos no Mercado Livre
    itens = soup.select(".ui-search-layout__item")
    
    for idx, item in enumerate(itens[:16], start=1):  # Pega os primeiros 16 produtos
        try:
            # Título
            titulo_elem = item.select_one(".ui-search-item__title")
            titulo = titulo_elem.text.strip() if titulo_elem else "Produto do Flamengo"
            
            # Link do produto
            link_elem = item.select_one("a.ui-search-link")
            link = link_elem["href"] if link_elem else "https://www.mercadolivre.com.br"
            
            # Imagem
            img_elem = item.select_one("img.ui-search-result-image__element")
            imagem = ""
            if img_elem:
                imagem = img_elem.get("data-src") or img_elem.get("src") or ""
            
            # Preço
            preco_fraction = item.select_one(".poly-price__current .andaria-price-fraction, .price-tag-fraction")
            if preco_fraction:
                preco = f"R$ {preco_fraction.text.strip()}"
            else:
                preco = "R$ 199,90"

            produtos.append({
                "id": idx,
                "titulo": titulo,
                "preco": preco,
                "avaliacao": 4.9,
                "imagem": imagem,
                "linkMercadoLivre": link
            })
        except Exception as e:
            continue

    return produtos

def salvar_produtos(produtos):
    if not produtos:
        print("⚠️ Nenhum produto foi encontrado.")
        return

    caminho_saida = os.path.join("src", "produtos.json")
    with open(caminho_saida, "w", encoding="utf-8") as file:
        json.dump(produtos, file, ensure_ascii=False, indent=2)
        
    print(f"✅ SUCESSO! {len(produtos)} produtos raspados e salvos em: {caminho_saida}")

if __name__ == "__main__":
    lista_produtos = raspar_produtos_mercadolivre()
    salvar_produtos(lista_produtos)