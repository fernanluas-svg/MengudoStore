import React, { useMemo, useState } from 'react';
import produtosData from './produtos.json';
import acessoriosData from './acessorios.json';
import linhaInfantilData from './linhaInfantil.json';
import equipamentosData from './equipamentosDoCanal.json';
import flaFemininoData from './flaFeminino.json';
import tacasImg from './assets/tacas.png';

function ProdutoCard({ produto }) {
  return (
    <div className="group bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden hover:border-red-500/50 hover:shadow-[0_0_30px_rgba(220,38,38,0.15)] transition-all duration-300">
      <div className="relative h-64 bg-slate-800 overflow-hidden">
        <img
          src={produto.imagem}
          alt={produto.titulo}
          className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute top-3 right-3 bg-slate-900/80 backdrop-blur-sm text-xs text-yellow-400 px-2 py-1 rounded-full flex items-center gap-1 border border-slate-700">
          ⭐ {produto.avaliacao}
        </div>
      </div>
      <div className="p-4">
        <h3 className="text-sm font-semibold text-slate-100 line-clamp-2 h-10 leading-tight group-hover:text-red-400 transition-colors">
          {produto.titulo}
        </h3>
        <div className="mt-3">
          <a
            href={produto.linkMercadoLivre}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex items-center justify-center gap-2 text-sm font-bold bg-red-600 hover:bg-red-500 text-white px-4 py-3 rounded-full transition-colors shadow-lg shadow-red-900/20 animate-btn-pulse"
          >
            VER OFERTA ➔
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
      <div className="relative h-64 bg-slate-800 overflow-hidden">
        <img
          src={produto.imagem}
          alt={produto.titulo}
          className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-500"
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
        <div className="mt-auto pt-4">
          <a
            href={produto.linkMercadoLivre}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex items-center justify-center gap-2 text-sm font-bold bg-red-600 hover:bg-red-500 text-white px-4 py-3 rounded-full transition-colors shadow-lg shadow-red-900/20 animate-btn-pulse"
          >
            VER OFERTA ➔
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
      <svg className="w-8 h-8 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    )
  },
  {
    titulo: "Pagamento Seguro",
    descricao: "Pague utilizando os métodos oficiais da plataforma, com total segurança.",
    icone: (
      <svg className="w-8 h-8 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
      </svg>
    )
  },
  {
    titulo: "Entrega para Todo o Brasil",
    descricao: "Os produtos são enviados conforme a logística do Mercado Livre.",
    icone: (
      <svg className="w-8 h-8 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
      </svg>
    )
  },
  {
    titulo: "Compra com Confiança",
    descricao: "Escolha entre vendedores bem avaliados e acompanhe seu pedido diretamente pela plataforma.",
    icone: (
      <svg className="w-8 h-8 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            <div className="w-12 h-12 rounded-lg bg-emerald-600/10 border border-emerald-600/20 flex items-center justify-center text-emerald-400 mb-4 group-hover:bg-emerald-600/20 group-hover:scale-110 transition-all duration-300 shadow-[0_0_25px_rgba(16,185,129,0.4)] group-hover:shadow-[0_0_40px_rgba(16,185,129,0.6)]">
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

const particulas = Array.from({ length: 48 }, (_, i) => {
  const variants = ['particle-1', 'particle-2', 'particle-3', 'particle-4', 'particle-5', 'particle-6'];
  const cores = [
    'rgba(255,255,255,',
    'rgba(255,255,255,',
    'rgba(220,200,200,',
    'rgba(127,29,29,',
    'rgba(180,60,60,',
    'rgba(200,200,210,',
  ];
  const idx = i % cores.length;
  const isDestaque = i % 3 === 0;
  const opacidade = isDestaque ? (0.5 + Math.random() * 0.1).toFixed(2) : (0.35 + Math.random() * 0.15).toFixed(2);
  return {
    top: `${(Math.random() * 90 + 5).toFixed(1)}%`,
    left: `${(Math.random() * 90 + 5).toFixed(1)}%`,
    tamanho: `${(3 + Math.random() * 4).toFixed(1)}px`,
    cor: `${cores[idx]}${opacidade})`,
    animacao: variants[i % variants.length],
    duracao: `${(20 + Math.random() * 20).toFixed(1)}s`,
    atraso: `${(Math.random() * 12).toFixed(1)}s`,
    brilho: isDestaque
      ? `drop-shadow(0 0 ${(3 + Math.random() * 5).toFixed(1)}px ${cores[idx]}${(0.25 + Math.random() * 0.2).toFixed(2)})`
      : Math.random() > 0.5
        ? `drop-shadow(0 0 ${(2 + Math.random() * 3).toFixed(1)}px ${cores[idx]}${(0.12 + Math.random() * 0.13).toFixed(2)})`
        : 'none',
  };
});

function ParticulasFundo() {
  return (
    <>
      {particulas.map((p, i) => (
        <div
          key={i}
          className="absolute rounded-full"
          style={{
            top: p.top,
            left: p.left,
            width: p.tamanho,
            height: p.tamanho,
            background: p.cor,
            filter: p.brilho,
            animation: `${p.animacao} ${p.duracao} ease-in-out ${p.atraso} infinite`,
          }}
        />
      ))}
    </>
  );
}

export default function Mengudostore() {
  const [politicaAberta, setPoliticaAberta] = useState(false);

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
        @keyframes btn-pulse {
          0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(220,38,38,0.5); }
          50% { transform: scale(1.06); box-shadow: 0 0 20px 4px rgba(220,38,38,0.35); }
        }
        .animate-btn-pulse {
          animation: btn-pulse 2s ease-in-out infinite;
        }
        .animate-btn-pulse:hover {
          animation-play-state: paused;
        }
        @keyframes particle-1 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          20% { transform: translate(40px, -50px) scale(1.2); }
          40% { transform: translate(80px, -10px) scale(0.9); }
          60% { transform: translate(50px, 30px) scale(1.1); }
          80% { transform: translate(10px, -20px) scale(0.95); }
        }
        @keyframes particle-2 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(-60px, 30px) scale(1.15); }
          50% { transform: translate(-20px, 70px) scale(0.85); }
          75% { transform: translate(-40px, 10px) scale(1.05); }
        }
        @keyframes particle-3 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          20% { transform: translate(30px, 40px) scale(0.9); }
          40% { transform: translate(-30px, 80px) scale(1.1); }
          60% { transform: translate(-10px, 30px) scale(1.15); }
          80% { transform: translate(20px, -10px) scale(0.95); }
        }
        @keyframes particle-4 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(-70px, -40px) scale(1.1); }
          66% { transform: translate(-30px, 20px) scale(0.9); }
        }
        @keyframes particle-5 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(50px, 60px) scale(0.85); }
          50% { transform: translate(90px, 20px) scale(1.2); }
          75% { transform: translate(40px, -30px) scale(1); }
        }
        @keyframes particle-6 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          20% { transform: translate(-40px, -60px) scale(1.15); }
          40% { transform: translate(-80px, -20px) scale(0.9); }
          60% { transform: translate(-50px, 40px) scale(1.05); }
          80% { transform: translate(-10px, -30px) scale(0.95); }
        }
        @keyframes heroFadeIn {
          from {
            opacity: 0;
            transform: translateY(25px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .hero-title {
          animation: heroFadeIn 0.9s ease-out forwards;
          animation-delay: 0.1s;
          opacity: 0;
        }
        .hero-subtitle {
          animation: heroFadeIn 0.9s ease-out forwards;
          animation-delay: 0.4s;
          opacity: 0;
        }
        @keyframes modal-pop {
          from { opacity: 0; transform: scale(0.95) translateY(10px); }
          to { opacity: 1; transform: scale(1) translateY(0); }
        }
        .modal-pop {
          animation: modal-pop 0.25s ease-out forwards;
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
          <h1 className="hero-title text-3xl sm:text-5xl font-black tracking-tight leading-none uppercase drop-shadow-[0_4px_8px_rgba(0,0,0,0.8)]">
            OS MELHORES PRODUTOS SELECIONADOS PARA A <br />
            <span className="text-red-500 font-black drop-shadow-[0_0_15px_rgba(220,38,38,0.8)]">
              NAÇÃO <br /> RUBRO-NEGRA
            </span>
          </h1>

          <p className="hero-subtitle text-base sm:text-lg text-slate-200 max-w-2xl font-medium mt-1 drop-shadow-md">
            Os melhores produtos do Flamengo, futebol e equipamentos que eu uso no canal. Todos testados e aprovados.
          </p>

          {/* Botão de Compra Segura com Brilho Metálico */}
          <button className="btn-shine mt-4 flex items-center gap-2 bg-slate-900/90 border border-slate-700 hover:bg-slate-800 text-white px-6 py-3 rounded-full text-sm font-medium transition-all backdrop-blur-sm shadow-lg group">
            <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
            Compra 100% Segura Via Shopee e Mercado Livre
            <span className="group-hover:translate-x-1 transition-transform">→</span>
          </button>
        </div>

      </div>

      {/* ========================================= */}
      {/* Conteúdo com Fundo Gradiente Sutil */}
      {/* ========================================= */}
      <div className="relative">
        {/* Partículas flutuantes */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden" style={{ zIndex: 0 }}>
          <ParticulasFundo />
        </div>

        {/* Seções com z-index acima do fundo */}
        <div className="relative z-10">
          <SecaoProdutos
            titulo="Produtos em Destaque"
            descricao="Os Produtos Mais Procurados"
            produtos={produtosData.slice(0, 8)}
          />

          <SecaoProdutos
            titulo="FLA Feminino"
            descricao="Para As Nossas Rubro-Negras"
            produtos={flaFemininoData}
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

      <a
        href="https://www.youtube.com/@mengudo1"
        target="_blank"
        rel="noopener noreferrer"
        className="block bg-black pt-12 pb-8"
      >
        <div className="flex flex-col items-center justify-center gap-6">
          <div className="flex items-center gap-4">
            <img
              src="https://i.ibb.co/WvsR3rBX/Fundo-preto.png"
              alt="Canal do Mengudo"
              className="h-16 w-auto object-contain"
            />
            <div>
              <p className="text-white font-bold text-2xl underline decoration-2 underline-offset-4">Canal do Mengudo</p>
              <p className="text-white font-bold text-2xl underline decoration-2 underline-offset-4">Recomenda</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-white font-bold text-lg tracking-wider">INSCREVA-SE NO CANAL</span>
            <svg className="w-10 h-10" viewBox="0 0 24 24" fill="currentColor">
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" fill="#FF0000"/>
            </svg>
          </div>
        </div>
      </a>
      <div className="bg-black text-center pb-8 flex flex-col items-center gap-2">
        <p className="text-slate-500 text-xs">© 2026 Canal do Mengudo. Todos os direitos reservados.</p>
        <button
          onClick={() => setPoliticaAberta(true)}
          className="text-slate-400 text-xs hover:text-slate-200 underline underline-offset-2 transition-colors"
        >
          Política de Privacidade
        </button>
      </div>

      {politicaAberta && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center p-4"
          onClick={() => setPoliticaAberta(false)}
        >
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm"></div>
          <div
            className="modal-pop relative bg-slate-900 border border-slate-700 rounded-xl shadow-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg sm:text-xl font-bold text-white">Política de Privacidade</h2>
              <button
                onClick={() => setPoliticaAberta(false)}
                aria-label="Fechar"
                className="w-8 h-8 flex items-center justify-center rounded-full bg-slate-800 hover:bg-red-600 text-slate-300 hover:text-white transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-3 text-sm text-slate-300 leading-relaxed">
              <p>
                Respeitamos a sua privacidade. Este site utiliza cookies básicos para melhorar a experiência de navegação.
              </p>
              <p>
                Alguns dos links exibidos em nosso site são links de afiliados de plataformas como Shopee e Mercado Livre.
                Quando você clica nesses links e realiza uma compra, podemos receber uma comissão sem nenhum custo
                adicional para você.
              </p>
              <p>
                Não coletamos, armazenamos ou vendemos dados pessoais sensíveis dos usuários.
              </p>
            </div>
            <div className="mt-6 text-right">
              <button
                onClick={() => setPoliticaAberta(false)}
                className="bg-red-600 hover:bg-red-500 text-white text-sm font-semibold px-5 py-2 rounded-full transition-colors"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}