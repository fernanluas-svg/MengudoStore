import os
import json
import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL_CANVA = "https://canaldomengudo.my.canva.site/"
PASTA_IMAGENS = "public/produtos"
ARQUIVO_JSON = "src/produtos.json"

# Cria a pasta de imagens se não existir
os.makedirs(PASTA_IMAGENS, exist_ok=True)

def extrair_produtos():
    print("🚀 Iniciando a raspagem no Canva...")
    
    with sync_playwright() as p:
        # Abre o navegador
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL_CANVA, wait_until="networkidle")
        
        # FORÇA O SCROLL ATÉ O FINAL PARA CARREGAR OS 33 PRODUTOS
        print("📜 Rolando a página para carregar todos os 33 itens...")
        for _ in range(10):
            page.mouse.wheel(0, 3000)
            time.sleep(1)
            
        time.sleep(3) # Espera final para garantir imagens renderizadas
        
        # Pega o HTML carregado
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    
    # Busca por todos os links do Mercado Livre ou links externos
    links_elementos = soup.find_all("a", href=True)
    links_ml = [a["href"] for a in links_elementos if "mercadolivre" in a["href"] or "mercadolibo" in a["href"]]
    
    # Remove duplicados mantendo a ordem
    links_ml = list(dict.fromkeys(links_ml))
    print(f"🔗 Encontrados {len(links_ml)} links do Mercado Livre.")

    # Busca por todas as imagens da página
    imgs = soup.find_all("img")
    urls_imagens = []
    for img in imgs:
        src = img.get("src") or img.get("data-src")
        if src and ("http" in src):
            urls_imagens.append(src)

    produtos = []
    
    # Se encontrou menos links que 33, cria a lista base expandida com 33 itens para garantir os quadrantes
    total_itens = max(33, len(links_ml))
    
    for i in range(1, total_itens + 1):
        # Seleciona o link do ML se existir
        link_produto = links_ml[i - 1] if i <= len(links_ml) else "https://www.mercadolivre.com.br"
        
        # Seleciona ou baixa a imagem
        caminho_imagem = "/produtos/escudo.png" # Imagem padrão se falhar
        
        if i <= len(urls_imagens):
            img_url = urls_imagens[i - 1]
            try:
                # Baixa a imagem localmente
                res = requests.get(img_url, timeout=5)
                if res.status_code == 200:
                    nome_img = f"produto_{i}.webp"
                    caminho_local = os.path.join(PASTA_IMAGENS, nome_img)
                    with open(caminho_local, "wb") as f:
                        f.write(res.content)
                    caminho_imagem = f"/produtos/{nome_img}"
            except Exception as e:
                pass

        # Monta o objeto do produto
        produto = {
            "id": i,
            "titulo": f"Produto Flamengo #{i}",
            "preco": "R$ 0,00",
            "avaliacao": 5.0,
            "imagem": caminho_imagem,
            "linkMercadoLivre": link_produto
        }
        produtos.append(produto)

    # Garante a pasta src se não existir
    os.makedirs(os.path.dirname(ARQUIVO_JSON), exist_ok=True)

    # Salva o JSON final
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)

    print(f"✅ Sucesso! {len(produtos)} quadrantes/produtos gerados no {ARQUIVO_JSON}!")

if __name__ == "__main__":
    extrair_produtos()