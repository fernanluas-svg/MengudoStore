import React, { useState, useEffect, useRef } from 'react';
import produtosData from './produtos.json';
import acessoriosData from './acessorios.json';
import linhaInfantilData from './linhaInfantil.json';
import equipamentosData from './equipamentosDoCanal.json';
import flaFemininoData from './flaFeminino.json';
import tacasImg from './assets/tacas.png';
import NovidadesCarrossel from './NovidadesCarrossel.jsx';

const FLAMENGO_ESCUDO_URL =
  'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/orE554NToSkH6nuwofe7Yg_500x500.png';
const FLAMENGO_ESCUDO_FALLBACK =
  'https://upload.wikimedia.org/wikipedia/commons/2/2e/Flamengo_braz_logo.svg';
const FLAMENGO_API_ID = 318;

const NEXT_MATCH = {
  opponent: 'Cruzeiro',
  opponentLogo:
    'https://ssl.gstatic.com/onebox/media/sports/logos/optimized/Tcv9X__nIh-6wFNJPMwIXQ_500x500.png',
  date: '2026-08-19T21:30:00-03:00', // Data/Hora ISO para o Timer
  competition: 'CONMEBOL Libertadores',
  stadium: 'Maracanã - Rio de Janeiro, RJ'
};

function ProdutoCard({ produto }) {
  return (
    <div className="group bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden hover:border-red-500/50 hover:shadow-[0_0_30px_rgba(220,38,38,0.15)] transition-all duration-300">
      <div className="relative h-64 bg-slate-800 overflow-hidden">
        <img
          src={produto.imagem}
          alt={produto.titulo}
          loading="lazy"
          className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute top-3 right-3 bg-slate-900/80 backdrop-blur-sm text-xs text-yellow-400 px-1.5 py-0.5 rounded-full flex items-center gap-1 border border-slate-700">
          ⭐ {produto.avaliacao}
        </div>
      </div>
      <div className="p-3 sm:p-4">
        <h3 className="text-xs sm:text-sm font-semibold text-slate-100 line-clamp-2 h-10 leading-tight group-hover:text-red-400 transition-colors">
          {produto.titulo}
        </h3>
        <div className="mt-3">
          <a
            href={produto.linkMercadoLivre}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex items-center justify-center gap-1 sm:gap-2 text-xs font-bold bg-red-600 hover:bg-red-500 text-white px-2 py-2 sm:text-sm sm:px-4 sm:py-3 rounded-full transition-colors shadow-lg shadow-red-900/20 animate-btn-pulse whitespace-nowrap"
          >
            VER OFERTA <span className="text-[0.75em] leading-none">➔</span>
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
      <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3 lg:grid-cols-4">
        {produtos.map((produto) => (
          <ProdutoCard key={produto.id} produto={produto} />
        ))}
      </div>
    </section>
  );
}

function ProximoJogoWidget() {
  const [match, setMatch] = useState(NEXT_MATCH);

  const calcularTempo = (dateStr) => {
    const diff = new Date(dateStr).getTime() - Date.now();
    if (diff <= 0) {
      return { dias: 0, horas: 0, minutos: 0, segundos: 0, encerrado: true };
    }
    return {
      dias: Math.floor(diff / 86400000),
      horas: Math.floor((diff / 3600000) % 24),
      minutos: Math.floor((diff / 60000) % 60),
      segundos: Math.floor((diff / 1000) % 60),
      encerrado: false
    };
  };

  const [tempo, setTempo] = useState(() => calcularTempo(NEXT_MATCH.date));

  useEffect(() => {
    const atualizarTempo = () => setTempo(calcularTempo(match.date));
    atualizarTempo();
    const id = setInterval(atualizarTempo, 1000);
    return () => clearInterval(id);
  }, [match.date]);

  useEffect(() => {
    const key = import.meta.env.VITE_FOOTBALL_API_KEY;
    if (!key) return;

    const controlador = new AbortController();
    let ativo = true;

    fetch(
      `https://api.sportmonks.com/v3/football/schedules/teams/${FLAMENGO_API_ID}?api_token=${key}&include=participants;venue;league`,
      { signal: controlador.signal }
    )
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (!ativo) return;
        const fixtures = Array.isArray(data?.data) ? data.data : [];
        const agora = Date.now();
        const proxima = fixtures
          .map((f) => ({
            ...f,
            inicio:
              (Number(f.starting_at_timestamp) || 0) * 1000 ||
              new Date(f.starting_at).getTime() ||
              0
          }))
          .filter((f) => f.inicio >= agora)
          .sort((a, b) => a.inicio - b.inicio)[0];
        if (!proxima) return;
        const participantes = Array.isArray(proxima.participants) ? proxima.participants : [];
        const adversario =
          participantes.find((p) => Number(p.id) !== FLAMENGO_API_ID) || participantes[0];
        const venue = proxima.venue;
        const cidade = venue?.city;
        setMatch({
          opponent: adversario?.name || NEXT_MATCH.opponent,
          opponentLogo: adversario?.image_path || NEXT_MATCH.opponentLogo,
          date: new Date(proxima.inicio).toISOString() || NEXT_MATCH.date,
          competition: proxima.league?.name || NEXT_MATCH.competition,
          stadium: [venue?.name, cidade].filter(Boolean).join(' - ') || NEXT_MATCH.stadium
        });
      })
      .catch((error) => {
        if (!ativo) return;
        console.log('Erro na API Futebol:', error);
      })
      .finally(() => {
        ativo = false;
      });

    return () => {
      ativo = false;
      controlador.abort();
    };
  }, []);

  const unidades = [
    { label: 'Dias', value: tempo.dias },
    { label: 'Horas', value: tempo.horas },
    { label: 'Min', value: tempo.minutos },
    { label: 'Seg', value: tempo.segundos }
  ];

  const trocarParaFallback = (e, fallback) => {
    e.currentTarget.onerror = null;
    e.currentTarget.src = fallback;
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur-md border border-red-600/30 rounded-2xl p-6 text-center shadow-xl">
      <div className="flex items-center justify-center gap-2 mb-4">
        <span className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></span>
        <h3 className="text-xs sm:text-sm font-bold tracking-widest text-red-400 uppercase">Próximo Jogo do Mengão</h3>
      </div>

      {tempo.encerrado ? (
        <p className="text-sm text-slate-300 mb-4">O jogo já começou!</p>
      ) : (
        <div className="flex justify-center gap-2 sm:gap-3 mb-5">
          {unidades.map((u) => (
            <div
              key={u.label}
              className="bg-slate-950/60 border border-slate-700/60 rounded-xl px-2 py-2 sm:px-3 min-w-[62px]"
            >
              <div className="text-xl sm:text-2xl font-black text-white tabular-nums">
                {String(u.value).padStart(2, '0')}
              </div>
              <div className="text-[10px] text-slate-400 uppercase tracking-wider mt-1">{u.label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center justify-center gap-3 sm:gap-4 mb-5">
        <div className="flex flex-col items-center gap-2 flex-1">
          <img
            src={FLAMENGO_ESCUDO_URL}
            alt="Flamengo"
            onError={(e) => trocarParaFallback(e, FLAMENGO_ESCUDO_FALLBACK)}
            className="w-14 h-14 sm:w-16 sm:h-16 object-contain drop-shadow-[0_0_12px_rgba(220,38,38,0.5)]"
          />
          <span className="text-xs sm:text-sm font-bold text-white">Flamengo</span>
        </div>
        <span className="text-2xl sm:text-3xl font-black text-red-500">X</span>
        <div className="flex flex-col items-center gap-2 flex-1">
          <img
            src={match.opponentLogo}
            alt={match.opponent}
            onError={(e) => trocarParaFallback(e, NEXT_MATCH.opponentLogo)}
            className="w-14 h-14 sm:w-16 sm:h-16 object-contain"
          />
          <span className="text-xs sm:text-sm font-bold text-white">{match.opponent}</span>
        </div>
      </div>

      <div className="space-y-1.5 pt-4 border-t border-slate-800">
        <p className="text-xs sm:text-sm font-medium text-slate-200">{match.competition}</p>
        <p className="text-xs sm:text-sm text-slate-400 flex items-center justify-center gap-1.5">
          <svg className="w-4 h-4 text-red-500 shrink-0" fill="currentColor" viewBox="0 0 24 24">
            <path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M11.54 22.351l.07.04.028.016a.76.76 0 00.723 0l.028-.015.071-.041a16.975 16.975 0 001.144-.742 19.58 19.58 0 002.683-2.282c1.944-1.99 3.963-4.98 3.963-8.827a8.25 8.25 0 00-16.5 0c0 3.846 2.02 6.837 3.963 8.827a19.58 19.58 0 002.682 2.282 16.975 16.975 0 001.145.742zM12 13.5a3 3 0 100-6 3 3 0 000 6z"
            />
          </svg>
          {match.stadium}
        </p>
      </div>
    </div>
  );
}

function EquipamentoCard({ produto }) {
  return (
    <div className="group bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden hover:border-red-500/50 hover:shadow-[0_0_30px_rgba(220,38,38,0.15)] transition-all duration-300 flex flex-col">
      <div className="relative h-64 bg-slate-800 overflow-hidden">
        <img
          src={produto.imagem}
          alt={produto.titulo}
          loading="lazy"
          className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute top-3 right-3 bg-slate-900/80 backdrop-blur-sm text-xs text-yellow-400 px-1.5 py-0.5 rounded-full flex items-center gap-1 border border-slate-700">
          ⭐ {produto.avaliacao}
        </div>
      </div>
      <div className="p-3 sm:p-5 flex flex-col flex-1">
        <h3 className="text-xs sm:text-sm font-semibold text-slate-100 line-clamp-2 leading-tight group-hover:text-red-400 transition-colors">
          {produto.titulo}
        </h3>
        {produto.descricao && (
          <p className="text-xs sm:text-sm text-slate-400 mt-1 sm:mt-2 leading-relaxed">{produto.descricao}</p>
        )}
        <div className="mt-auto pt-3 sm:pt-4">
          <a
            href={produto.linkMercadoLivre}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex items-center justify-center gap-1 sm:gap-2 text-xs font-bold bg-red-600 hover:bg-red-500 text-white px-2 py-2 sm:text-sm sm:px-4 sm:py-3 rounded-full transition-colors shadow-lg shadow-red-900/20 animate-btn-pulse whitespace-nowrap"
          >
            VER OFERTA <span className="text-[0.75em] leading-none">➔</span>
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
      <svg className="w-6 h-6 sm:w-8 sm:h-8 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    )
  },
  {
    titulo: "Pagamento Seguro",
    descricao: "Pague utilizando os métodos oficiais da plataforma, com total segurança.",
    icone: (
      <svg className="w-6 h-6 sm:w-8 sm:h-8 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
      </svg>
    )
  },
  {
    titulo: "Entrega para Todo o Brasil",
    descricao: "Os produtos são enviados conforme a logística do Mercado Livre.",
    icone: (
      <svg className="w-6 h-6 sm:w-8 sm:h-8 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
      </svg>
    )
  },
  {
    titulo: "Compra com Confiança",
    descricao: "Escolha entre vendedores bem avaliados e acompanhe seu pedido diretamente pela plataforma.",
    icone: (
      <svg className="w-6 h-6 sm:w-8 sm:h-8 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  }
];

const palavrasChaveSEO = [
  "Camisa do Flamengo", "Manto Sagrado", "Jaqueta Corta Vento Flamengo", "Agasalho do Flamengo", "Blusa do Flamengo", "Regata do Flamengo", "Shorts do Flamengo", "Calça Treino Flamengo", "Moletom Flamengo", "Uniforme Flamengo", "Camisa Oficial Flamengo", "Camisa Retrô Flamengo", "Kit Infantil Flamengo", "Camisa Feminina Flamengo", "Chinelo do Flamengo", "Boné do Flamengo", "Meião Flamengo", "Roupas do Flamengo", "Manto 1 Flamengo", "Manto 2 Flamengo", "Manto 3 Flamengo", "Coleção Licenciada Flamengo", "Moda Esportiva Rubro-Negra", "Acessórios do Flamengo", "Moda Rubro-Negra", "Loja do Flamengo", "Mengão Stores", "Produtos do Flamengo Shopee", "Comprar Camisa do Flamengo", "Promoção Manto Sagrado", "Desconto Roupas do Flamengo", "Manto Sagrado Barato", "Ofertas Flamengo", "Loja Rubro-Negra Online", "Produtos Licenciados Flamengo", "Camisa Flamengo Promoção", "Melhores Ofertas Flamengo", "Cupom Desconto Flamengo", "Artigos Esportivos Flamengo", "Presentes do Flamengo", "Comprar Corta Vento Flamengo", "Preço Camisa do Flamengo", "Loja Virtual Flamengo", "Melhores Preços Mengão", "Achadinhos do Flamengo", "Produtos Torcedor Flamengo", "Vitrine Rubro-Negra", "E-commerce Flamengo", "Colecionáveis Flamengo", "Roupas Baratas do Flamengo", "Mengão", "Mengudo", "Flamengo", "Clube de Regatas do Flamengo", "CR Flamengo", "Rubro-Negro", "Mais Querido", "Nação Rubro-Negra", "Maracanã", "Urubu", "Mengão do Meu Coração", "Raça Rubro-Negra", "Torcida do Flamengo", "Maior Torcida do Mundo", "Garotos do Ninho", "Fla", "Ninho do Urubu", "Raça Amor e Paixão", "SRN", "Vamos Flamengo", "Zico", "Gabigol", "Bruno Henrique", "Arrascaeta", "Libertadores da América", "Bi da Libertadores", "Tri da Libertadores", "Campeão Mundial 1981", "Brasileirão Flamengo", "Octacampeão", "Copa do Brasil Flamengo", "Cariocão Flamengo", "Ídolos do Flamengo", "Títulos do Flamengo", "Jogos do Flamengo", "Mengão Campeão", "História do Flamengo", "Conquistas Rubro-Negras", "Elenco do Flamengo", "Jogadores do Flamengo", "Futebol Brasileiro", "Paixão Rubro-Negra", "Estilo Torcedor", "Orgulho Rubro-Negro", "Vestir o Manto", "Dia de Flamengo", "Coleção Flamengo 2026", "Lançamento Manto Flamengo", "Modinha Rubro-Negra", "Nação Rubro-Negra Online"
];

const faqItens = [
  {
    pergunta: "Os produtos são oficiais e de qualidade?",
    resposta: "Sim! Selecionamos e indicamos apenas produtos licenciados, oficiais e itens com excelente avaliação de compradores no marketplace da Shopee."
  },
  {
    pergunta: "Como faço para comprar um produto?",
    resposta: "É muito simples! Ao clicar no botão de compra em qualquer item da nossa loja, você será redirecionado com segurança para a página oficial do produto na Shopee, onde poderá finalizar a compra com a sua conta."
  },
  {
    pergunta: "Qual é o prazo e o valor do frete?",
    resposta: "O valor e o prazo de entrega variam de acordo com o seu CEP. Ao ser redirecionado para a Shopee, você poderá calcular o frete exato e aplicar cupons de frete grátis oferecidos pela própria Shopee."
  },
  {
    pergunta: "Como acompanho o rastreamento do meu pedido?",
    resposta: "Todo o pagamento, envio e rastreio são geridos diretamente pela plataforma da Shopee. Assim que finalizar a compra por lá, você poderá acompanhar todo o trajeto do seu pedido na aba \"Meus Pedidos\" do app ou site da Shopee."
  },
  {
    pergunta: "A compra pelo Mengudo Stores é segura?",
    resposta: "Totalmente segura! O Mengudo Stores funciona como uma vitrine de recomendação de produtos. Você não insere dados de pagamento ou cartão no nosso site; toda a transação é processada em ambiente 100% criptografado e seguro dentro da Shopee."
  },
  {
    pergunta: "Como funcionam trocas e devoluções?",
    resposta: "Como a compra é concluída na Shopee, qualquer solicitação de troca, devolução ou reembolso segue as diretrizes da Garantia Shopee. Basta solicitar diretamente pelo aplicativo da Shopee no prazo estipulado após o recebimento."
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
      <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3 lg:grid-cols-4">
        {confiançaCards.map((card, i) => (
          <div
            key={card.titulo}
            className="group bg-slate-900/50 border border-slate-800 rounded-xl p-3 sm:p-6 hover:border-red-500/50 hover:shadow-[0_0_30px_rgba(220,38,38,0.15)] transition-all duration-300 animate-fade-in"
            style={{ animationDelay: `${i * 0.15}s` }}
          >
            <div className="w-9 h-9 sm:w-12 sm:h-12 rounded-lg bg-emerald-600/10 border border-emerald-600/20 flex items-center justify-center text-emerald-400 mb-2 sm:mb-4 group-hover:bg-emerald-600/20 group-hover:scale-110 transition-all duration-300 shadow-[0_0_25px_rgba(16,185,129,0.4)] group-hover:shadow-[0_0_40px_rgba(16,185,129,0.6)]">
              {card.icone}
            </div>
            <h3 className="text-xs sm:text-sm font-semibold text-slate-100 mb-2">{card.titulo}</h3>
            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">{card.descricao}</p>
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
      <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3 lg:grid-cols-4 max-w-5xl mx-auto">
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
  const [seoAberto, setSeoAberta] = useState(false);
  const [faqAberto, setFaqAberta] = useState(false);
  const [mostrarBotaoTopo, setMostrarBotaoTopo] = useState(false);
  const [headerVisivel, setHeaderVisivel] = useState(true);
  const [novidadesVisivel, setNovidadesVisivel] = useState(false);
  const novidadesTituloRef = useRef(null);

  useEffect(() => {
    const el = novidadesTituloRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setNovidadesVisivel(true);
          obs.disconnect();
        }
      },
      { threshold: 0.3 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    let ultimaPosicao = window.scrollY;

    const aoRolar = () => {
      const posicaoAtual = window.scrollY;

      setMostrarBotaoTopo(posicaoAtual > 300);

      if (posicaoAtual <= 0) {
        setHeaderVisivel(true);
      } else {
        const diferenca = posicaoAtual - ultimaPosicao;
        if (Math.abs(diferenca) > 8) {
          setHeaderVisivel(diferenca < 0);
        }
      }
      ultimaPosicao = posicaoAtual;
    };
    window.addEventListener('scroll', aoRolar, { passive: true });
    aoRolar();
    return () => window.removeEventListener('scroll', aoRolar);
  }, []);

  const voltarAoTopo = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

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
        .security-badge-icon {
          color: #C0C0C0;
        }
        @keyframes pulseShield {
          0% { transform: scale(1); }
          50% { transform: scale(1.1); }
          100% { transform: scale(1); }
        }
        .security-badge:hover .security-badge-icon {
          animation: pulseShield 1s infinite ease-in-out;
        }
        .social-proof {
          color: #FFD700;
          animation: fade-in-up 0.9s ease-out 0.7s both;
        }
        .social-proof p {
          color: #e2e8f0;
        }
        .social-proof-star {
          animation: starGlow 4s ease-in-out infinite;
        }
        @keyframes starGlow {
          0%, 100% { opacity: 0.9; text-shadow: 0 0 5px rgba(255,215,0,0.2); }
          50% { opacity: 1; text-shadow: 0 0 10px rgba(255,215,0,0.45); }
        }
        .novidades-reveal {
          transform: translateX(0);
          transition: transform 0.9s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .novidades-reveal-hidden {
          transform: translateX(-108%);
        }
        .novidades-reveal-mask {
          overflow: hidden;
        }
      `}</style>

      {/* ========================================= */}
      {/* Header / Navegação com Escudo do Mengão */}
      {/* ========================================= */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur-md transition-transform duration-300 ease-in-out ${
          headerVisivel ? 'translate-y-0' : '-translate-y-full'
        }`}
      >
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
      <div className="relative bg-black text-white py-16 px-6 sm:px-12 overflow-hidden pt-28">
        
        {/* Vídeo de fundo da Nação Rubro-Negra */}
        <video
          src="/hero-bg.mp4"
          poster="/hero.png"
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover"
        ></video>

        {/* Sombreamento escuro para garantir contraste */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/70 to-transparent"></div>

        {/* Luz Neon Vermelha no Fundo */}
        <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-72 h-72 bg-red-600/30 rounded-full blur-[120px]"></div>

        {/* Conteúdo de Texto */}
        <div className="relative max-w-7xl mx-auto z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-7 flex flex-col items-start gap-3">
            <h1 className="hero-title text-3xl sm:text-5xl font-black tracking-tight leading-none uppercase drop-shadow-[0_4px_8px_rgba(0,0,0,0.8)]">
              OS MELHORES PRODUTOS SELECIONADOS PARA A <br />
              <span className="text-red-500 font-black drop-shadow-[0_0_15px_rgba(220,38,38,0.8)]">
                NAÇÃO <br /> RUBRO-NEGRA
              </span>
            </h1>

            <p className="hero-subtitle text-base sm:text-lg text-slate-200 max-w-2xl font-medium mt-1 drop-shadow-md">
              Os melhores produtos do Flamengo, futebol e equipamentos que eu uso no canal. Todos testados e aprovados.
            </p>

            {/* Grupo de Confiança: Botão de Compra Segura + Prova Social */}
            <div className="mt-4 flex flex-col items-center">
              <button className="security-badge btn-shine flex items-center gap-2 bg-slate-900/90 border border-slate-700 hover:bg-slate-800 text-white px-6 py-3 rounded-full text-sm font-medium transition-all backdrop-blur-sm shadow-lg group">
                <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
                Compra 100% Segura Via Shopee e Mercado Livre
                <span className="security-badge-icon flex items-center">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
                  </svg>
                </span>
              </button>

              {/* Prova Social */}
              <div className="social-proof mt-3 flex flex-col items-center gap-1.5">
                <div className="flex items-center gap-1">
                  {[0, 1, 2, 3, 4].map((i) => (
                    <svg
                      key={i}
                      className="social-proof-star w-5 h-5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.196-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.783-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                  ))}
                </div>
                <p className="text-sm sm:text-base text-slate-200 font-medium tracking-wide">
                  4.9/5 • Mais de 1.500 rubro-negros satisfeitos
                </p>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5">
            <ProximoJogoWidget />
          </div>
        </div>

      </div>

      {/* ========================================= */}
      {/* Seção: Novidades do Mengão */}
      {/* ========================================= */}
      <section className="w-full py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" ref={novidadesTituloRef}>
          <div className="flex items-center justify-center gap-4 mb-12 text-center">
            <div className="w-1 h-8 bg-red-600 rounded-full shrink-0 relative z-10"></div>
            <div className="novidades-reveal-mask">
              <div className={`novidades-reveal ${novidadesVisivel ? '' : 'novidades-reveal-hidden'}`}>
                <h2 className="text-2xl sm:text-3xl font-bold text-white">Novidades do Mengão</h2>
                <p className="text-sm text-slate-400 mt-1">As últimas novidades e lançamentos do Mengão em primeira mão</p>
              </div>
            </div>
          </div>
        </div>

        <NovidadesCarrossel />
      </section>

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
        <div className="flex items-center justify-center gap-3 flex-wrap">
          <button
            onClick={() => setPoliticaAberta(true)}
            className="text-slate-400 text-xs hover:text-slate-200 underline underline-offset-2 transition-colors"
          >
            Política de Privacidade
          </button>
          <span className="text-slate-600">•</span>
          <button
            onClick={() => setSeoAberta(true)}
            className="text-slate-400 text-xs hover:text-slate-200 underline underline-offset-2 transition-colors"
          >
            Termos & Tags (SEO)
          </button>
          <span className="text-slate-600">•</span>
          <button
            onClick={() => setFaqAberta(true)}
            className="text-slate-400 text-xs hover:text-slate-200 underline underline-offset-2 transition-colors"
          >
            Perguntas Frequentes (FAQ)
          </button>
        </div>
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

      {/* Modal SEO / Palavras-chave */}
      {seoAberto && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center p-4"
          onClick={() => setSeoAberta(false)}
        >
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm"></div>
          <div
            className="modal-pop relative bg-slate-900 border border-slate-700 rounded-xl shadow-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg sm:text-xl font-bold text-white">Palavras-Chave e Termos de Busca - Mengudo Stores</h2>
              <button
                onClick={() => setSeoAberta(false)}
                aria-label="Fechar"
                className="w-8 h-8 flex items-center justify-center rounded-full bg-slate-800 hover:bg-red-600 text-slate-300 hover:text-white transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="mb-4">
              <p className="text-sm text-slate-400 mb-2 leading-relaxed">
                Confira as principais tags e termos relacionados aos nossos produtos e ao Mengão:
              </p>
              <div className="flex flex-wrap gap-2">
                {palavrasChaveSEO.map((tag, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center px-3 py-1.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-xs hover:bg-slate-700 hover:text-white transition-colors cursor-default"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            <div className="mt-6 text-right">
              <button
                onClick={() => setSeoAberta(false)}
                className="bg-red-600 hover:bg-red-500 text-white text-sm font-semibold px-5 py-2 rounded-full transition-colors"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal FAQ / Perguntas Frequentes */}
      {faqAberto && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center p-4"
          onClick={() => setFaqAberta(false)}
        >
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm"></div>
          <div
            className="modal-pop relative bg-slate-900 border border-slate-700 rounded-xl shadow-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg sm:text-xl font-bold text-white">Perguntas Frequentes (FAQ) - Mengudo Stores</h2>
              <button
                onClick={() => setFaqAberta(false)}
                aria-label="Fechar"
                className="w-8 h-8 flex items-center justify-center rounded-full bg-slate-800 hover:bg-red-600 text-slate-300 hover:text-white transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="mb-4">
              <p className="text-sm text-slate-400 mb-4 leading-relaxed">
                Tire suas dúvidas sobre como comprar os produtos do Mengão através do nosso site:
              </p>
              <div className="space-y-3">
                {faqItens.map((item, i) => (
                  <details
                    key={i}
                    className="group border border-slate-700 rounded-lg bg-slate-800/50 open:bg-slate-800 transition-colors"
                  >
                    <summary className="cursor-pointer list-none p-4 flex items-center justify-between text-slate-100 font-semibold hover:text-red-400 transition-colors">
                      <span className="pr-4">
                        <span className="text-red-500 mr-1">Q{i + 1}:</span>{' '}
                        {item.pergunta}
                      </span>
                      <svg
                        className="w-5 h-5 text-slate-400 group-hover:text-red-500 transition-transform duration-200 group-open:rotate-180 flex-shrink-0"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </summary>
                    <div className="px-4 pb-4 text-sm text-slate-300 leading-relaxed">
                      <span className="text-red-500 mr-1 font-medium">R:</span>{' '}
                      {item.resposta}
                    </div>
                  </details>
                ))}
              </div>
            </div>
            <div className="mt-6 text-right">
              <button
                onClick={() => setFaqAberta(false)}
                className="bg-red-600 hover:bg-red-500 text-white text-sm font-semibold px-5 py-2 rounded-full transition-colors"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Botão Voltar ao Topo */}
      <button
        onClick={voltarAoTopo}
        aria-label="Voltar ao topo"
        className={`fixed bottom-6 right-6 z-[200] w-12 h-12 rounded-full bg-black border-2 border-red-600/60 shadow-[0_0_20px_rgba(218,41,28,0.35)] flex items-center justify-center text-[#DA291C] hover:bg-red-600 hover:text-white hover:border-red-500 transition-all duration-300 ${
          mostrarBotaoTopo ? 'opacity-100 translate-y-0 pointer-events-auto' : 'opacity-0 translate-y-4 pointer-events-none'
        }`}
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2.5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
        </svg>
      </button>
    </div>
  );
}