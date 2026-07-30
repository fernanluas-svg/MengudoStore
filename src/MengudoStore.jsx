import React from 'react';
import produtosData from './produtos.json';
import acessoriosData from './acessorios.json';
import linhaInfantilData from './linhaInfantil.json';
import equipamentosData from './equipamentosDoCanal.json';
import tacasImg from './assets/tacas.png';

function ProdutoCard({ produto }) {
  return (
    <div className="group bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden hover:border-red-500/50 hover:shadow-[0_0_30px_rgba(220,38,38,0.15)] transition-all duration-300">
      <div className="relative h-48 bg-slate-800 overflow-hidden">
        <img
          src={produto.imagem}
          alt={produto.titulo}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute top-3 right-3 bg-slate-900/80 backdrop-blur-sm text-xs text-yellow-400 px-2 py-1 rounded-full flex items-center gap-1 border border-slate-700">
          ⭐ {produto.avaliacao}
        </div>
      </div>
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
  );
}

function SecaoProdutos({ titulo, descricao, produtos }) {
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 w-full">
      <div className="flex items-center gap-4 mb-10">
        <div className="w-1 h-8 bg-red-600 rounded-full"></div>
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white">{titulo}</h2>
          <p className="text-sm text-slate-400 mt-1">{descricao}</p>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {produtos.map((produto) => (
          <ProdutoCard key={produto.id} produto={produto} />
        ))}
      </div>
    </section>
  );
}

function EquipamentoCard({ produto }) {
  return (
    <div className="group bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden hover:border-red-500/50 hover:shadow-[0_0_30px_rgba(220,38,38,0.15)] transition-all duration-300 flex flex-col">
      <div className="relative h-56 bg-slate-800 overflow-hidden">
        <img
          src={produto.imagem}
          alt={produto.titulo}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute top-3 right-3 bg-slate-900/80 backdrop-blur-sm text-xs text-yellow-400 px-2 py-1 rounded-full flex items-center gap-1 border border-slate-700">
          ⭐ {produto.avaliacao}
        </div>
      </div>
      <div className="p-5 flex flex-col flex-1">
        <h3 className="text-base font-semibold text-slate-100 leading-tight group-hover:text-red-400 transition-colors">
          {produto.titulo}
        </h3>
        {produto.descricao && (
          <p className="text-sm text-slate-400 mt-2 leading-relaxed">{produto.descricao}</p>
        )}
        <div className="mt-auto pt-4 flex items-center justify-between">
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
  );
}

const confiançaCards = [
  {
    titulo: "Compra 100% Segura",
    descricao: "Todos os links levam para o Mercado Livre, onde sua compra é protegida.",
    icone: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    )
  },
  {
    titulo: "Pagamento Seguro",
    descricao: "Pague utilizando os métodos oficiais da plataforma, com total segurança.",
    icone: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
      </svg>
    )
  },
  {
    titulo: "Entrega para Todo o Brasil",
    descricao: "Os produtos são enviados conforme a logística do Mercado Livre.",
    icone: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
      </svg>
    )
  },
  {
    titulo: "Compra com Confiança",
    descricao: "Escolha entre vendedores bem avaliados e acompanhe seu pedido diretamente pela plataforma.",
    icone: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  }
];

function SecaoConfianca() {
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 w-full">
      <div className="flex items-center gap-4 mb-10">
        <div className="w-1 h-8 bg-red-600 rounded-full"></div>
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white">Compre com Segurança</h2>
          <p className="text-sm text-slate-400 mt-1">
            Todos os produtos deste site direcionam para o Mercado Livre, uma das maiores plataformas de e-commerce da América Latina.
          </p>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {confiançaCards.map((card, i) => (
          <div
            key={card.titulo}
            className="group bg-slate-900/50 border border-slate-800 rounded-xl p-6 hover:border-red-500/50 hover:shadow-[0_0_30px_rgba(220,38,38,0.15)] transition-all duration-300 animate-fade-in"
            style={{ animationDelay: `${i * 0.15}s` }}
          >
            <div className="w-12 h-12 rounded-lg bg-emerald-600/10 border border-emerald-600/20 flex items-center justify-center text-emerald-400 mb-4 group-hover:bg-emerald-600/20 group-hover:scale-110 transition-all duration-300">
              {card.icone}
            </div>
            <h3 className="text-base font-semibold text-slate-100 mb-2">{card.titulo}</h3>
            <p className="text-sm text-slate-400 leading-relaxed">{card.descricao}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function SecaoEquipamentos({ titulo, descricao, produtos }) {
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 w-full">
      <div className="flex items-center gap-4 mb-10">
        <div className="w-1 h-8 bg-red-600 rounded-full"></div>
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white">{titulo}</h2>
          <p className="text-sm text-slate-400 mt-1">{descricao}</p>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
        {produtos.map((produto) => (
          <EquipamentoCard key={produto.id} produto={produto} />
        ))}
      </div>
    </section>
  );
}

export default function Mengudostore() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Estilo do Brilho Metálico (Sheen) - faixa diagonal como reflexo de lâmina */}
      <style>{`
        .btn-shine {
          position: relative;
          overflow: hidden;
        }
        .btn-shine::before {
          content: '';
          position: absolute;
          top: -50%;
          left: -100%;
          width: 50%;
          height: 200%;
          background: linear-gradient(
            115deg,
            transparent 0%,
            transparent 30%,
            rgba(255,255,255,0.15) 40%,
            rgba(255,255,255,0.5) 45%,
            rgba(255,255,255,0.8) 50%,
            rgba(255,255,255,0.5) 55%,
            rgba(255,255,255,0.15) 60%,
            transparent 70%,
            transparent 100%
          );
          transform: skewX(-18deg);
          animation: sheen 3.5s ease-in-out 2s infinite;
        }
        @keyframes sheen {
          0% { left: -100%; }
          85% { left: 100%; }
          100% { left: 100%; }
        }
        @keyframes fade-in-up {
          0% { opacity: 0; transform: translateY(20px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in-up 0.6s ease-out forwards;
          opacity: 0;
        }
        .stars-layer {
          background-image:
            radial-gradient(1px 1px, rgba(255,255,255,0.3) 100%, transparent 100%),
            radial-gradient(1.5px 1.5px, rgba(255,255,255,0.15) 100%, transparent 100%),
            radial-gradient(2px 2px, rgba(127,29,29,0.2) 100%, transparent 100%),
            radial-gradient(1px 1px, rgba(180,60,60,0.12) 100%, transparent 100%);
          background-size:
            50px 50px,
            80px 80px,
            120px 120px,
            160px 160px;
          background-position:
            0 0,
            25px 25px,
            60px 10px,
            90px 70px;
          animation: stars-drift 90s linear infinite;
        }
        .stars-layer-pulse {
          background-image: radial-gradient(1.5px 1.5px, rgba(255,255,255,0.2) 100%, transparent 100%);
          background-size: 100px 100px;
          background-position: 45px 55px;
          animation: stars-pulse 8s ease-in-out infinite;
        }
        @keyframes stars-drift {
          0% { background-position: 0 0, 25px 25px, 60px 10px, 90px 70px; }
          100% { background-position: 50px 50px, 105px 105px, 180px 130px, 250px 230px; }
        }
        @keyframes stars-pulse {
          0%, 100% { opacity: 0.4; }
          50% { opacity: 1; }
        }
      `}</style>

      {/* ========================================= */}
      {/* Header / Navegação com Escudo do Mengão */}
      {/* ========================================= */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          
          {/* Container da Esquerda - Escudo, Nome e Taças */}
          <div className="flex items-center gap-3">
            
            {/* Imagem do escudo */}
            <img 
              src="https://i.ibb.co/WvsR3rBX/Fundo-preto.png" 
              alt="Escudo Mengudo Store" 
              className="h-16 w-auto object-contain drop-shadow-lg"
            />

            {/* Nome da loja e Taças */}
            <div className="flex flex-col leading-tight">
              <div className="flex items-center gap-2">
                <span className="text-xl md:text-3xl font-black text-white tracking-wide">
                  MENGUDO <span className="text-red-500">STORE</span>
                </span>

                <div className="flex items-center gap-1">
                  <img src={tacasImg} alt="Taça Libertadores" className="h-7 w-auto object-contain" />
                  <img src={tacasImg} alt="Taça Libertadores" className="h-7 w-auto object-contain" />
                  <img src={tacasImg} alt="Taça Libertadores" className="h-7 w-auto object-contain" />
                  <img src={tacasImg} alt="Taça Libertadores" className="h-7 w-auto object-contain" />
                </div>
              </div>
              
              <span className="text-[10px] text-gray-400 tracking-widest hidden md:block">
                Recomendações Canal do @MENGUDO1
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

          {/* Botão de Compra Segura com Brilho Metálico */}
          <button className="btn-shine mt-4 flex items-center gap-2 bg-slate-900/90 border border-slate-700 hover:bg-slate-800 text-white px-6 py-3 rounded-full text-sm font-medium transition-all backdrop-blur-sm shadow-lg group">
            <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
            Compra 100% segura via Mercado Livre
            <span className="group-hover:translate-x-1 transition-transform">→</span>
          </button>
        </div>

      </div>

      {/* ========================================= */}
      {/* Conteúdo com Fundo Gradiente Sutil */}
      {/* ========================================= */}
      <div className="relative">
        {/* Camada de estrelas/partículas */}
        <div
          className="pointer-events-none absolute inset-0 overflow-hidden stars-layer"
          style={{ zIndex: 0 }}
        />
        <div
          className="pointer-events-none absolute inset-0 overflow-hidden stars-layer-pulse"
          style={{ zIndex: 0 }}
        />

        {/* Seções com z-index acima do fundo */}
        <div className="relative z-10">
          <SecaoProdutos
            titulo="Produtos em Destaque"
            descricao="Links diretos e seguros para compra no Mercado Livre"
            produtos={produtosData.slice(0, 8)}
          />

          <SecaoProdutos
            titulo="Acessórios do Mengão"
            descricao="Bonés, mochilas, chaveiros, copos, canecas, bandeiras e muito mais."
            produtos={acessoriosData}
          />

          <SecaoProdutos
            titulo="Linha Infantil"
            descricao="Rubro-negro desde pequeno."
            produtos={linhaInfantilData}
          />

          <SecaoEquipamentos
            titulo="Equipamentos que uso no canal"
            descricao="Do estúdio."
            produtos={equipamentosData}
          />

          <SecaoConfianca />
        </div>
      </div>
    </div>
  );
}