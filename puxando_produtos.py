import json
import os

# Lista de produtos da Mengudo Store
# Você pode adicionar, remover ou alterar os produtos, links e imagens aqui!
produtos_flamengo = [
    {
        "id": 1,
        "titulo": "Manto Sagrado Oficial Flamengo I 2024/25",
        "preco": "R$ 349,90",
        "avaliacao": 5.0,
        "imagem": "https://http2.mlstatic.com/D_NQ_NP_603831-MLA74673822187_022024-O.webp",
        "linkMercadoLivre": "https://www.mercadolivre.com.br"
    },
    {
        "id": 2,
        "titulo": "Camisa Flamengo Edição Especial Retrô Zico",
        "preco": "R$ 189,90",
        "avaliacao": 4.9,
        "imagem": "https://http2.mlstatic.com/D_NQ_NP_898492-MLB72619711681_112023-O.webp",
        "linkMercadoLivre": "https://www.mercadolivre.com.br"
    },
    {
        "id": 3,
        "titulo": "Casaco Agasalho Treino Flamengo Rubro-Negro",
        "preco": "R$ 279,90",
        "avaliacao": 4.8,
        "imagem": "https://http2.mlstatic.com/D_NQ_NP_729451-MLB71689302198_092023-O.webp",
        "linkMercadoLivre": "https://www.mercadolivre.com.br"
    },
    {
        "id": 4,
        "titulo": "Boné Aba Curva Oficial Flamengo CRF",
        "preco": "R$ 89,90",
        "avaliacao": 4.7,
        "imagem": "https://http2.mlstatic.com/D_NQ_NP_918512-MLB70541298123_072023-O.webp",
        "linkMercadoLivre": "https://www.mercadolivre.com.br"
    }
]

def gerar_json_produtos():
    # Caminho onde o JSON será salvo (dentro da pasta src do React)
    caminho_saida = os.path.join("src", "produtos.json")
    
    # Salva os dados em formato JSON formatado
    with open(caminho_saida, "w", encoding="utf-8") as file:
        json.dump(produtos_flamengo, file, ensure_ascii=False, indent=2)
        
    print(f"✅ Sucesso! {len(produtos_flamengo)} produtos gerados e salvos em: {caminho_saida}")

if __name__ == "__main__":
    gerar_json_produtos()