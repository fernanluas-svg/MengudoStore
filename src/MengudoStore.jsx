import React from 'react';
import produtosData from './produtos.json';

export default function MengudoStore() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Cabeçalho / Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        <div className="flex items-center space-x-3">
        <img src="https://i.ibb.co/qYYkHGY7/Fundo-preto.png" alt="Escudo Mengudo Store" className="h-10 w-auto mr-2 object-contain" />
          <h1 className="text-2xl font-black tracking-wider text-red-600 uppercase">
            Mengudo <span className="text-slate-100">Store</span>
          </h1>
        </div>
          <p className="hidden md:block text-sm text-slate-400">
            As melhores ofertas e produtos do Mengão selecionados para você
          </p>
        </div>
      </header>
      {/* Seção Hero / Destaque */}
<div className="relative bg-black text-white py-16 px-6 sm:px-12 overflow-hidden">
  {/* Imagem de fundo do Maracanã */}
  <img 
    src="/hero.png" 
    alt="Maracanã Nação Rubro-Negra" 
    className="absolute inset-0 w-full h-full object-cover opacity-30"
  />

  {/* Sombreamento escuro para destacar o texto */}
  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/70 to-transparent" />

  {/* Conteúdo de Texto */}
  <div className="relative max-w-4xl mx-auto z-10 flex flex-col items-start gap-3">
    <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-none uppercase">
      OS MELHORES PRODUTOS SELECIONADOS PARA A{' '}
      <span className="text-red-600 font-black">NAÇÃO RUBRO-NEGRA</span>
    </h1>

    <p className="text-base sm:text-lg text-slate-200 max-w-2xl font-medium mt-1">
      Os melhores produtos do Flamengo, futebol e equipamentos que eu uso no canal. Todos testados e aprovados.
    </p>

    {/* Selo Mercado Livre */}
    <div className="mt-2 flex items-center gap-2 bg-slate-900/80 backdrop-blur border border-slate-700/60 px-4 py-2 rounded-full text-xs sm:text-sm font-semibold text-green-400">
      <span>🛡️</span>
      <span>Compra 100% segura via Mercado Livre</span>
    </div>
  </div>
</div>

      {/* Conteúdo Principal */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Título da Seção */}
        <div className="mb-8 border-l-4 border-red-600 pl-4">
          <h2 className="text-2xl font-bold text-slate-100">Produtos em Destaque</h2>
          <p className="text-slate-400 text-sm">Links diretos e seguros para compra no Mercado Livre</p>
        </div>

        {/* Grid de Produtos */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {produtosData.map((produto) => (
            <div 
              key={produto.id} 
              className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-red-600/50 transition-all duration-300 flex flex-col group shadow-lg"
            >
              {/* Imagem do Produto */}
              <div className="relative aspect-square overflow-hidden bg-slate-800">
                <img 
                  src={produto.imagem} 
                  alt={produto.titulo} 
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    e.target.onerror = null; 
                    e.target.src = 'https://via.placeholder.com/400x400/1e293b/ffffff?text=Produto+Flamengo';
                  }}
                />
                <div className="absolute top-2 right-2 bg-slate-950/80 backdrop-blur text-yellow-400 px-2.5 py-1 rounded-full text-xs font-semibold flex items-center gap-1 border border-slate-800">
                  ★ {produto.avaliacao.toFixed(1)}
                </div>
              </div>

              {/* Informações do Produto */}
              <div className="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="font-semibold text-slate-100 text-base line-clamp-2 mb-2 group-hover:text-red-500 transition-colors">
                    {produto.titulo}
                  </h3>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-800/80">
                  <div className="text-2xl font-black text-red-500 mb-4">
                    {produto.preco}
                  </div>

                  <a 
                    href={produto.linkMercadoLivre} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="w-full inline-flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg transition-colors duration-200 shadow-md shadow-red-950/50"
                  >
                    <span>Ver no Mercado Livre</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Rodapé / Footer */}
      <footer className="border-t border-slate-800 bg-slate-900 py-6 text-center text-slate-500 text-sm">
        <p>© 2026 Canal do Mengudo • Todos os direitos reservados.</p>
      </footer>
    </div>
  );
}