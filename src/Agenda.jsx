import { useState } from 'react';
import Header from './Header.jsx';
import proximosJogos from './data/nextMatch.json';
import jogosEncerrados from './data/matches.json';
import classificacaoBrasileirao from './data/classificacaoBrasileirao.json';
import classificacaoLibertadores from './data/classificacaoLibertadores.json';
import { FiCalendar, FiMapPin, FiAward } from 'react-icons/fi';
import { RiTrophyLine } from 'react-icons/ri';

const FLAMENGO_ESCUDO_URL =
  'https://s.sde.globo.com/media/organizations/2018/04/10/Flamengo-2018.svg';
const FLAMENGO_ESCUDO_FALLBACK =
  'https://upload.wikimedia.org/wikipedia/commons/2/2e/Flamengo_braz_logo.svg';

const LOGOS_TIMES = {
  'Palmeiras': 'https://s.sde.globo.com/media/organizations/2019/07/06/Palmeiras.svg',
  'Flamengo': 'https://s.sde.globo.com/media/organizations/2018/04/10/Flamengo-2018.svg',
  'Athletico Paranaense': 'https://s.sde.globo.com/media/organizations/2026/01/07/Athletico-PR.svg',
  'Fluminense': 'https://s.sde.globo.com/media/organizations/2018/03/11/fluminense.svg',
  'Cruzeiro': 'https://s.sde.globo.com/media/organizations/2021/02/13/cruzeiro_2021.svg',
  'Bahia': 'https://s.sde.globo.com/media/organizations/2018/03/11/bahia.svg',
  'Red Bull Bragantino': 'https://s.sde.globo.com/media/organizations/2021/06/28/bragantino.svg',
  'Atlético Mineiro': 'https://s.sde.globo.com/media/organizations/2018/03/10/atletico-mg.svg',
  'Corinthians': 'https://s.sde.globo.com/media/organizations/2024/10/09/Corinthians_2024_Q4ahot4.svg',
  'Coritiba': 'https://s.sde.globo.com/media/organizations/2018/03/11/coritiba.svg',
  'Botafogo': 'https://s.sde.globo.com/media/organizations/2019/02/04/botafogo-svg.svg',
  'Vitória': 'https://s.sde.globo.com/media/organizations/2025/12/18/Vitoria_2025.svg',
  'São Paulo': 'https://s.sde.globo.com/media/organizations/2018/03/11/sao-paulo.svg',
  'Santos': 'https://s.sde.globo.com/media/organizations/2018/03/12/santos.svg',
  'Grêmio': 'https://s.sde.globo.com/media/organizations/2018/03/12/gremio.svg',
  'Internacional': 'https://s.sde.globo.com/media/organizations/2018/03/11/internacional.svg',
  'Mirassol': 'https://s.sde.globo.com/media/organizations/2026/07/17/MIrassol.svg',
  'Remo': 'https://s.sde.globo.com/media/organizations/2021/02/25/Remo-PA.svg',
  'Vasco da Gama': 'https://s.sde.globo.com/media/organizations/2021/09/04/vasco_SVG.svg',
  'Chapecoense': 'https://s.sde.globo.com/media/organizations/2021/06/21/CHAPECOENSE-2018.svg',
};

function estiloZona(posicao) {
  if (posicao >= 1 && posicao <= 4) {
    return { bg: 'bg-cyan-500/10 hover:bg-cyan-500/20', borda: 'border-cyan-400' };
  }
  if (posicao >= 5 && posicao <= 6) {
    return { bg: 'bg-cyan-300/10 hover:bg-cyan-300/20', borda: 'border-cyan-200' };
  }
  if (posicao >= 7 && posicao <= 16) {
    return { bg: 'bg-slate-700/25 hover:bg-slate-700/35', borda: 'border-slate-500' };
  }
  return { bg: 'bg-rose-500/10 hover:bg-rose-500/20', borda: 'border-rose-400' };
}

function formatarData(iso) {
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
}

function formatarHora(iso) {
  return new Date(iso).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function EscudoJogo({ src, fallback, nome, className = 'w-8 h-8' }) {
  const [indice, setIndice] = useState(0);
  const origens = [src, fallback].filter(Boolean);
  if (indice >= origens.length || origens.length === 0) {
    return (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={`${className} text-slate-500`}
        aria-label={nome}
      >
        <path d="M12 2l8 3v6c0 5-3.5 9.5-8 11-4.5-1.5-8-6-8-11V5l8-3z" />
        <path d="M9 12l2 2 4-4" />
      </svg>
    );
  }
  return (
    <img
      src={origens[indice]}
      alt={nome}
      onError={() => setIndice((i) => i + 1)}
      className={`${className} object-contain`}
    />
  );
}

function timesDaPartida(partida) {
  return {
    esquerdo: partida.isHome
      ? { nome: 'Flamengo', src: FLAMENGO_ESCUDO_URL, fallback: FLAMENGO_ESCUDO_FALLBACK }
      : { nome: partida.opponent, src: partida.opponentLogo, fallback: null },
    direito: partida.isHome
      ? { nome: partida.opponent, src: partida.opponentLogo, fallback: null }
      : { nome: 'Flamengo', src: FLAMENGO_ESCUDO_URL, fallback: FLAMENGO_ESCUDO_FALLBACK },
  };
}

function CabecalhoCard({ icone, titulo, descricao }) {
  return (
    <header className="flex items-center gap-3 mb-5">
      <div className="w-10 h-10 rounded-lg bg-red-600/20 border border-red-600/30 flex items-center justify-center text-red-400 shrink-0">
        {icone}
      </div>
      <div>
        <h2 className="text-lg font-bold text-white">{titulo}</h2>
        <p className="text-xs text-slate-400">{descricao}</p>
      </div>
    </header>
  );
}

function CardAgenda() {
  const partidas = proximosJogos
    .filter((jogo) => jogo.status === 'SCHEDULED')
    .sort((a, b) => new Date(a.date) - new Date(b.date))
    .slice(0, 5);

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6 flex flex-col">
      <CabecalhoCard
        icone={<FiCalendar className="w-5 h-5" />}
        titulo="Agenda de Jogos"
        descricao="Os próximos 5 confrontos do Mengão"
      />

      {partidas.length === 0 ? (
        <p className="text-sm text-slate-400">Nenhum próximo confronto no momento.</p>
      ) : (
        <ul className="space-y-3">
          {partidas.map((partida) => {
            const { esquerdo, direito } = timesDaPartida(partida);
            return (
            <li
              key={partida.id}
              className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 sm:p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
                  {formatarData(partida.date)} • {formatarHora(partida.date)}
                </span>
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                    partida.isHome
                      ? 'bg-emerald-600/20 text-emerald-400 border-emerald-600/30'
                      : 'bg-red-600/20 text-red-400 border-red-600/30'
                  }`}
                >
                  {partida.isHome ? 'Mandante' : 'Visitante'}
                </span>
              </div>

              <div className="flex items-center justify-center gap-2 sm:gap-3">
                <div className="flex flex-col items-center gap-1 flex-1 min-w-0">
                  <EscudoJogo src={esquerdo.src} fallback={esquerdo.fallback} nome={esquerdo.nome} />
                  <span className="text-xs font-bold text-white truncate w-full text-center">
                    {esquerdo.nome}
                  </span>
                </div>
                <span className="text-lg font-black text-red-500 shrink-0">X</span>
                <div className="flex flex-col items-center gap-1 flex-1 min-w-0">
                  <EscudoJogo src={direito.src} fallback={direito.fallback} nome={direito.nome} />
                  <span className="text-xs font-bold text-white truncate w-full text-center">
                    {direito.nome}
                  </span>
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-slate-800 flex items-center justify-center gap-1.5 text-xs text-slate-400 flex-wrap">
                <FiMapPin className="w-3.5 h-3.5 shrink-0" />
                <span>{partida.stadium}</span>
                <span className="text-slate-600">•</span>
                <span>{partida.competition}</span>
              </div>
            </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function CardResultados() {
  const encerradas = jogosEncerrados
    .filter((jogo) => jogo.status === 'FINISHED' && jogo.homeScore != null && jogo.awayScore != null)
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5);

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6 flex flex-col">
      <CabecalhoCard
        icone={<FiAward className="w-5 h-5" />}
        titulo="Resumo de Resultados"
        descricao="Os últimos 5 resultados do Mengão"
      />

      {encerradas.length === 0 ? (
        <div className="flex flex-col items-center justify-center flex-1 py-12 text-center">
          <FiAward className="w-12 h-12 text-slate-700 mb-4" />
          <p className="text-sm text-slate-300 font-medium">
            Nenhum resultado recente registrado.
          </p>
          <p className="text-xs text-slate-500 mt-2 max-w-[260px]">
            Acompanhe os próximos confrontos ao lado! Os placares aparecerão aqui após cada jogo.
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {encerradas.map((partida) => {
            const { esquerdo, direito } = timesDaPartida(partida);
            return (
            <li
              key={partida.id}
              className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 sm:p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
                  {formatarData(partida.date)} • {partida.competition}
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border bg-slate-700/40 text-slate-300 border-slate-600">
                  Encerrado
                </span>
              </div>
              <div className="flex items-center justify-center gap-2 sm:gap-3">
                <div className="flex flex-col items-center gap-1 flex-1 min-w-0">
                  <EscudoJogo src={esquerdo.src} fallback={esquerdo.fallback} nome={esquerdo.nome} />
                  <span className="text-xs font-bold text-white truncate w-full text-center">
                    {esquerdo.nome}
                  </span>
                </div>
                <span className="text-lg font-black text-white tabular-nums whitespace-nowrap">
                  {partida.homeScore} <span className="text-slate-500">x</span> {partida.awayScore}
                </span>
                <div className="flex flex-col items-center gap-1 flex-1 min-w-0">
                  <EscudoJogo src={direito.src} fallback={direito.fallback} nome={direito.nome} />
                  <span className="text-xs font-bold text-white truncate w-full text-center">
                    {direito.nome}
                  </span>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-slate-800 flex items-center justify-center gap-1.5 text-xs text-slate-400 flex-wrap">
                <FiMapPin className="w-3.5 h-3.5 shrink-0" />
                <span>{partida.stadium}</span>
                <span className="text-slate-600">•</span>
                <span>{partida.competition}</span>
              </div>
            </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function TabelaClassificacao({ linhas }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-slate-400 text-[11px] uppercase tracking-wider">
            <th className="text-left py-2 pl-2 font-semibold">#</th>
            <th className="text-left py-2 font-semibold">Time</th>
            <th className="text-center py-2 font-semibold">P</th>
            <th className="text-center py-2 font-semibold hidden sm:table-cell">J</th>
            <th className="text-center py-2 font-semibold hidden md:table-cell">V</th>
            <th className="text-center py-2 font-semibold hidden md:table-cell">E</th>
            <th className="text-center py-2 font-semibold hidden md:table-cell">D</th>
            <th className="text-center py-2 font-semibold">SG</th>
          </tr>
        </thead>
        <tbody>
          {linhas.map((linha) => {
            const destaque = linha.time === 'Flamengo';
            const { bg, borda } = estiloZona(linha.posicao);
            return (
              <tr
                key={linha.posicao}
                className={`${bg} ${
                  destaque
                    ? 'ring-1 ring-inset ring-red-500/60 text-red-200 font-semibold'
                    : 'text-slate-300'
                } border-b border-slate-800/60 transition-colors`}
              >
                <td className={`py-2 pl-2 font-semibold border-l-2 ${borda}`}>{linha.posicao}</td>
                <td className="py-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <EscudoJogo
                      src={LOGOS_TIMES[linha.time]}
                      fallback={null}
                      nome={linha.time}
                      className="w-7 h-7 shrink-0"
                    />
                    <span className="truncate">{linha.time}</span>
                  </div>
                </td>
                <td className="py-2 text-center font-bold">{linha.pontos}</td>
                <td className="py-2 text-center hidden sm:table-cell">{linha.jogos}</td>
                <td className="py-2 text-center hidden md:table-cell">{linha.vitorias}</td>
                <td className="py-2 text-center hidden md:table-cell">{linha.empates}</td>
                <td className="py-2 text-center hidden md:table-cell">{linha.derrotas}</td>
                <td className="py-2 text-center tabular-nums">
                  {linha.saldoGols > 0 ? `+${linha.saldoGols}` : linha.saldoGols}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function CardClassificacao() {
  const [aba, setAba] = useState('brasileirao');
  const abas = [
    { id: 'brasileirao', rotulo: 'Brasileirão' },
    { id: 'libertadores', rotulo: 'Libertadores' },
  ];

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6">
      <CabecalhoCard
        icone={<RiTrophyLine className="w-5 h-5" />}
        titulo="Tabela de Classificação"
        descricao="Brasileirão e Libertadores"
      />

      <div className="flex items-center gap-2 mb-5">
        {abas.map((item) => (
          <button
            key={item.id}
            onClick={() => setAba(item.id)}
            className={`px-4 py-2 rounded-lg text-sm font-semibold border-2 transition-all duration-200 ${
              aba === item.id
                ? 'bg-white text-slate-900 border-white shadow-[0_0_14px_rgba(255,255,255,0.3)]'
                : 'text-white border-white/40 hover:border-white/80 hover:bg-white/10'
            }`}
          >
            {item.rotulo}
          </button>
        ))}
      </div>

      {aba === 'brasileirao' ? (
        <TabelaClassificacao linhas={classificacaoBrasileirao} />
      ) : (
        <div className="space-y-5">
          {classificacaoLibertadores.map((grupo) => (
            <div key={grupo.grupo}>
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-2">
                {grupo.grupo}
              </h3>
              <TabelaClassificacao linhas={grupo.classificacao} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Agenda() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header />

      <main className="relative flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb-16 w-full">
        <div className="flex items-center gap-4 mb-10">
          <div className="w-1 h-8 bg-red-600 rounded-full"></div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white">Central de Jogos</h1>
            <p className="text-sm text-slate-400 mt-1">
              Agenda, resultados e classificação do Mengão em um só lugar.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CardAgenda />
          <CardResultados />
        </div>

        <div className="mt-6">
          <CardClassificacao />
        </div>
      </main>

      <footer className="bg-black text-center py-8">
        <p className="text-slate-500 text-xs">© 2026 Canal do Mengudo. Todos os direitos reservados.</p>
        <a href="/" className="inline-block mt-2 text-slate-400 text-xs hover:text-red-400 transition-colors underline underline-offset-2">
          Voltar para o Início
        </a>
      </footer>
    </div>
  );
}