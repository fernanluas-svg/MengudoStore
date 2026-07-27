import React from 'react';

const products = [
  {
    id: 1,
    title: "Produto Oficial Flamengo - Manto / Artigo",
    description: "Garanta já o seu produto com o melhor preço e envio para todo o Brasil.",
    price: "R$ 99,90",
    image: "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?q=80&w=600&auto=format&fit=crop",
    affiliateLink: "https://mercadolivre.com"
  },
];

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Cabeçalho do Site */}
      <header className="py-8 px-4 text-center border-b border-red-900/40 bg-gradient-to-b from-red-950/60 to-slate-950">
        <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-red-600 mb-2">
          🔴⚫ MENGUDO STORE
        </h1>
        <p className="text-slate-400 text-sm md:text-base max-w-xl mx-auto">
          As melhores ofertas e produtos do Mengão selecionados para você com link direto no Mercado Livre.
        </p>
      </header>

      {/* Vitrine de Produtos */}
      <main className="max-w-6xl mx-auto px-4 py-12">
        <h2 className="text-xl font-semibold mb-6 border-l-4 border-red-600 pl-3 text-slate-200">
          Produtos em Destaque
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {products.map((product) => (
            <div 
              key={product.id}
              className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-lg hover:border-red-600/50 transition-all duration-300 flex flex-col justify-between"
            >
              <div>
                {/* Imagem do Produto */}
                <div className="h-48 bg-slate-800 flex items-center justify-center overflow-hidden">
                  <img 
                    src={product.image} 
                    alt={product.title} 
                    className="object-cover h-full w-full hover:scale-105 transition-transform duration-500"
                  />
                </div>

                {/* Informações */}
                <div className="p-5">
                  <h3 className="font-bold text-lg mb-2 text-white line-clamp-2">
                    {product.title}
                  </h3>
                  <p className="text-slate-400 text-sm mb-4 line-clamp-2">
                    {product.description}
                  </p>
                  <span className="text-red-500 font-bold text-xl block mb-4">
                    {product.price}
                  </span>
                </div>
              </div>

              {/* Botão de Afiliado */}
              <div className="p-5 pt-0">
                <a 
                  href={product.affiliateLink} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-xl transition-colors duration-200 flex items-center justify-center gap-2 shadow-md shadow-red-950/50"
                >
                  Ver no Mercado Livre 🛒
                </a>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Rodapé */}
      <footer className="text-center py-6 text-xs text-slate-500 border-t border-slate-900">
        © 2026 Canal do Mengudo • Todos os direitos reservados.
      </footer>
    </div>
  );
}