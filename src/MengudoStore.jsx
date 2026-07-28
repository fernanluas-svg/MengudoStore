import React from 'react';
import produtosData from './produtos.json';

export default function MengudoStore() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Header / Navegação */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-600 rounded-lg flex items-center justify-center font-black text-xl shadow-lg shadow-red-600/30">
              M
            </div>
            <span className="font-black text-xl tracking-wider text-white">
              MENGUDO <span className="text-red-500">STORE</span>
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 hidden sm:block">
            As melhores ofertas e produtos do Mengão selecionados para você
          </p>
        </div>
      </header>

      {/* Seção Hero / Destaque com Efeitos Neon e Brilhos */}
      <div className="relative bg-black text-white py-16 px-6 sm:px-12 overflow-hidden">
        {/* Imagem de fundo do Maracanã */}
        <img
          src="/hero.png"
          alt="Maracanã Nação Rubro-Negra"
          className="absolute inset-0 w-full h-full object-cover opacity-100"
        />

        {/* Sombreamento escuro */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/70 to-transparent" />

        {/* Luz Neon Vermelha no Fundo (Glow Orb) */}
        <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-72 h-72 bg-red-600/30 rounded-full blur-3xl pointer-events-none" />

        {/* Conteúdo de Texto */}
        <div className="relative max-w-4xl mx-auto z-10 flex flex-col items-start gap-3">
          <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-none uppercase">
            OS MELHORES PRODUTOS SELECIONADOS PARA A{' '}
            <span className="text-red-500 font-black drop-shadow-[0_0_15px_rgba(220,38,38,0.8)]">
              NAÇÃO RUBRO-NEGRA
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-200 max-w-2xl font-medium mt-1 drop-shadow">
            Os melhores produtos do Flamengo, futebol e equipamentos que eu uso no canal. Todos testados e aprovados.
          </p>

          {/* Selo Mercado Livre Pulsante e Iluminado */}
          <div className="mt-2 flex items-center gap-2 bg-slate-900/90 backdrop-blur border border-red-500/50 shadow-lg shadow-red-600/30 animate-pulse px-4 py-2 rounded-full text-xs sm:text-sm font-semibold text-white">
            <span>🛡️</span>
            <span>Compra 100% segura via Mercado Livre</span>
          </div>
        </div>
      </div>

      {/* Seção Principal de Produtos */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col gap-1 mb-8 border-l-4 border-red-600 pl-4">
          <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
            Produtos em Destaque
          </h2>
          <p className="text-slate-400 text-sm">
            Links diretos e seguros para compra no Mercado Livre
          </p>
        </div>

        {/* Grid de Cards de Produtos */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {produtosData.map((produto) => (
            <div
              key={produto.id}
              className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden flex flex-col hover:border-red-600/50 transition-all duration-300 hover:-translate-y-1 shadow-lg group"
            >
              {/* Imagem do Produto */}
              <div className="relative aspect-square overflow-hidden bg-slate-950">
                <img
                  src={produto.imagem}
                  alt={produto.nome}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute top-3 right-3 bg-slate-900/90 backdrop-blur px-2.5 py-1 rounded-full text-xs font-bold text-amber-400 border border-slate-700 flex items-center gap-1">
                  ★ {produto.avaliacao}
                </div>
              </div>

              {/* Informações do Produto */}
              <div className="p-5 flex flex-col flex-1">
                <span className="text-xs font-bold uppercase tracking-wider text-red-500 mb-1">
                  {produto.categoria}
                </span>
                <h3 className="text-lg font-bold text-white mb-2 line-clamp-2">
                  {produto.nome}
                </h3>
                <p className="text-sm text-slate-400 mb-4 line-clamp-2 flex-1">
                  {produto.descricao}
                </p>

                <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                  <div>
                    <span className="text-xs text-slate-500 block">Preço</span>
                    <span className="text-2xl font-black text-white">
                      {produto.preco}
                    </span>
                  </div>

                  <a
                    href={produto.linkMercadoLivre}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2.5 rounded-lg font-bold text-sm transition-all shadow-md shadow-red-600/20 hover:shadow-red-600/40 active:scale-95"
                  >
                    Comprar
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Rodapé */}
      <footer className="border-t border-slate-800 bg-slate-900 py-6 text-center text-slate-500 text-sm">
        <p>© {new Date().getFullYear()} Mengudo Store. Todos os direitos reservados.</p>
      </footer>
    </div>
  );
}