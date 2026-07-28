import React from 'react';
import produtosData from './produtos.json';

export default function Mengudostore() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Estilo da Animação do Brilho Platinado */}
      <style>{`
        @keyframes sweep {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
        .animate-shine {
          animation: sweep 3s infinite ease-in-out;
        }
      `}</style>

      {/* ========================================= */}
      {/* Header / Navegação com Escudo do Mengão */}
      {/* ========================================= */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          
          {/* Container da Esquerda - Escudo e Nome */}
          <div className="flex items-center gap-3">
            
            {/* Imagem do escudo */}
            <img 
              src="https://i.ibb.co/WvsR3rBX/Fundo-preto.png" 
              alt="Escudo Mengudo Store" 
              className="h-14 w-auto object-contain drop-shadow-lg"
            />

            {/* Nome da loja */}
            <div className="flex flex-col leading-tight">
              <span className="text-xl md:text-2xl font-black text-white tracking-wide">
                MENGUDO <span className="text-red-500">STORE</span>
              </span>
              <span className="text-[10px] text-gray-400 tracking-widest uppercase hidden md:block">
                Nação Rubro-Negra
              </span>
            </div>
            
          </div>

          {/* Texto à direita (Slogan) */}
          <p className="text-xs sm:text-sm text-slate-400 hidden sm:block">
            As melhores ofertas e produtos do Mengão selecionados para você
          </p>

        </div>
      </header>

      {/* ========================================= */}
      {/* Seção Hero / Destaque */}
      {/* ========================================= */}
      <div className="relative bg-black text-white py-16 px-6 sm:px-12 overflow-hidden">
        
        {/* Imagem de fundo do Maracanã */}
        <img
          src="/hero.png"
          alt="Maracanã Nação Rubro-Negra"
          className="absolute inset-0 w-full h-full object-cover opacity-100"
        />

        {/* Sombreamento escuro */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/70 to-transparent"></div>

        {/* Luz Neon Vermelha no Fundo */}
        <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-72 h-72 bg-red-600/30 rounded-full blur-[120px]"></div>

        {/* Conteúdo de Texto */}
        <div className="relative max-w-4xl mx-auto z-10 flex flex-col items-start gap-3">
          <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-none uppercase drop-shadow-[0_4px_8px_rgba(0,0,0,0.8)]">
            OS MELHORES PRODUTOS SELECIONADOS PARA A <br />
            <span className="text-red-500 font-black drop-shadow-[0_0_15px_rgba(220,38,38,0.8)]">
              NAÇÃO <br /> RUBRO-NEGRA
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-200 max-w-2xl font-medium mt-1 drop-shadow-md">
            Os melhores produtos do Flamengo, futebol e equipamentos que eu uso no canal. Todos testados e aprovados.
          </p>

          {/* Botão de Compra Segura */}
          <button className="mt-4 flex items-center gap-2 bg-slate-900/90 border border-slate-700 hover:bg-slate-800 text-white px-6 py-3 rounded-full text-sm font-medium transition-all backdrop-blur-sm shadow-lg group">
            <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
            Compra 100% segura via Mercado Livre
            <span className="group-hover:translate-x-1 transition-transform">→</span>
          </button>
        </div>

      </div>

      {/* ========================================= */}
      {/* Seção: Produtos em Destaque */}
      {/* ========================================= */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 w-full">
        
        <div className="flex items-center gap-4 mb-10">
          <div className="w-1 h-8 bg-red-600 rounded-full"></div>
          <div>
            <h2 className="text-2xl sm:text-3xl font-bold text-white">Produtos em Destaque</h2>
            <p className="text-sm text-slate-400 mt-1">Links diretos e seguros para compra no Mercado Livre</p>
          </div>
        </div>

        {/* Grid de Produtos - Usando dados do JSON */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {produtosData.map((produto) => (
            <div 
              key={produto.id} 
              className="group bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden hover:border-red-500/50 hover:shadow-[0_0_30px_rgba(220,38,38,0.15)] transition-all duration-300"
            >
              {/* Imagem do Produto */}
              <div className="relative h-48 bg-slate-800 overflow-hidden">
                <img 
                  src={produto.imagem} 
                  alt={produto.titulo} 
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                {/* Badge de Avaliação */}
                <div className="absolute top-3 right-3 bg-slate-900/80 backdrop-blur-sm text-xs text-yellow-400 px-2 py-1 rounded-full flex items-center gap-1 border border-slate-700">
                  ⭐ {produto.avaliacao}
                </div>
              </div>

              {/* Informações */}
              <div className="p-4">
                <h3 className="text-sm font-semibold text-slate-100 line-clamp-2 h-10 leading-tight group-hover:text-red-400 transition-colors">
                  {produto.titulo}
                </h3>
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-lg font-bold text-white">{produto.preco}</span>
                  <a 
                    href={produto.linkMercadoLivre} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs font-medium bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded-full transition-colors shadow-lg shadow-red-900/20"
                  >
                    Ver Oferta
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

      </section>
    </div>
  );
}