import { useState } from 'react';
import Header from './Header.jsx';
import proximosJogos from './data/nextMatch.json';
import jogosEncerrados from './data/matches.json';
import classificacaoBrasileirao from './data/classificacaoBrasileirao.json';
import classificacaoLibertadores from './data/classificacaoLibertadores.json';
import libertadores from './data/libertadores.json';
import copaDoBrasil from './data/copaDoBrasil.json';
import carioca from './data/carioca.json';
import odds from './data/odds.json';
import mapaEscudos from './data/mapa_escudos.json';
import { FiCalendar, FiMapPin, FiAward, FiTrendingUp } from 'react-icons/fi';
import { RiTrophyLine } from 'react-icons/ri';

const FLAMENGO_ESCUDO_URL =
  'https://s.sde.globo.com/media/organizations/2018/04/10/Flamengo-2018.svg';
const FLAMENGO_ESCUDO_FALLBACK =
  'https://upload.wikimedia.org/wikipedia/commons/2/2e/Flamengo_braz_logo.svg';

const LOGOS_TIMES = {
  ...mapaEscudos,
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

function CardOdds() {
  const jogos = [...odds.jogos].sort((a, b) => new Date(a.date) - new Date(b.date));
  const proximo = jogos[0];

  if (!proximo || !proximo.odds) {
    return null;
  }

  const o = proximo.odds;
  const mandante = proximo.isHome ? 'Flamengo' : proximo.opponent;
  const visitante = proximo.isHome ? proximo.opponent : 'Flamengo';
  const real = proximo.source === 'flashscore';

  const cotacoes = [
    { label: '1', sub: mandante, valor: o['1'], destaque: !!proximo.isHome },
    { label: 'X', sub: 'Empate', valor: o['X'], destaque: false },
    { label: '2', sub: visitante, valor: o['2'], destaque: !proximo.isHome },
  ];

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6 flex flex-col lg:col-span-2">
      <CabecalhoCard
        icone={<FiTrendingUp className="w-5 h-5" />}
        titulo="Odds (1X2)"
        descricao={`Próximo jogo: Flamengo x ${proximo.opponent}`}
      />

      <div className="flex items-center justify-between mb-3">
        <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
          {formatarData(proximo.date)} • {proximo.competition}
        </span>
        {real && proximo.bookmaker ? (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border bg-amber-500/15 text-amber-300 border-amber-500/30">
            {proximo.bookmaker}
          </span>
        ) : (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border bg-slate-600/30 text-slate-400 border-slate-500/30">
            estimada
          </span>
        )}
      </div>

      <div className="grid grid-cols-3 gap-2">
        {cotacoes.map((c) => (
          <div
            key={c.label}
            className={`rounded-xl border p-3 flex flex-col items-center ${
              c.destaque
                ? 'border-red-500/50 bg-red-600/10'
                : 'border-slate-800 bg-slate-950/60'
            }`}
          >
            <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">
              {c.label}
            </span>
            <span className="text-xl font-black text-white tabular-nums my-0.5">
              {c.valor != null ? c.valor : '-'}
            </span>
            <span className="text-[10px] text-slate-500 truncate max-w-full">
              {c.sub}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function LinhaJogo({ rotulo, jogo }) {
  const indefinido = !jogo || jogo.placarCasa == null || jogo.placarFora == null;
  if (indefinido) {
    return (
      <p className="text-xs text-slate-300">
        <span className="text-slate-500">{rotulo}:</span>{' '}
        <span className="italic text-slate-500">a definir</span>
        {jogo && jogo.data && (
          <span className="text-slate-500">
            {' · '}
            {formatarData(jogo.data)}
            {formatarHora(jogo.data) !== '00:00' ? ` ${formatarHora(jogo.data)}` : ''}
          </span>
        )}
      </p>
    );
  }
  return (
    <p className="text-xs text-slate-300">
      <span className="text-slate-500">{rotulo}:</span> {jogo.casa}{' '}
      <span className="font-bold text-white tabular-nums">{jogo.placarCasa}</span>
      <span className="text-slate-500"> x </span>
      <span className="font-bold text-white tabular-nums">{jogo.placarFora}</span>{' '}
      {jogo.fora}
      {jogo.data && (
        <span className="text-slate-500">
          {' · '}
          {formatarData(jogo.data)}
          {formatarHora(jogo.data) !== '00:00' ? ` ${formatarHora(jogo.data)}` : ''}
        </span>
      )}
    </p>
  );
}

function CardMataMata({ confronto }) {
  const flamengoNoJogo = confronto.timeA === 'Flamengo' || confronto.timeB === 'Flamengo';
  let badge;
  if (confronto.status === 'A_DEFINIR') {
    badge = { texto: 'A definir', cor: 'bg-sky-500/20 text-sky-300 border-sky-500/40' };
  } else if (flamengoNoJogo) {
    if (confronto.status === 'EM_ANDAMENTO') {
      badge = { texto: 'Em andamento', cor: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40' };
    } else if (confronto.classificado === 'Flamengo') {
      badge = { texto: 'Classificado', cor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' };
    } else {
      badge = { texto: 'Eliminado', cor: 'bg-rose-500/20 text-rose-300 border-rose-500/40' };
    }
  } else if (confronto.status === 'EM_ANDAMENTO') {
    badge = { texto: 'Em andamento', cor: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40' };
  } else {
    badge = {
      texto: `Classificado: ${confronto.classificado}`,
      cor: 'bg-slate-600/30 text-slate-300 border-slate-500/40',
    };
  }

  const destaqueA = confronto.timeA === 'Flamengo';
  const destaqueB = confronto.timeB === 'Flamengo';

  return (
    <div
      className={`rounded-xl border p-4 flex flex-col gap-3 bg-slate-950/60 ${
        flamengoNoJogo ? 'border-red-500/60 ring-1 ring-red-500/40' : 'border-slate-800'
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
          {confronto.fase}
        </span>
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${badge.cor}`}
        >
          {badge.texto}
        </span>
      </div>

      {confronto.data && (
        <p className="-mt-1 text-[11px] text-slate-400">
          {formatarData(confronto.data)}
          {formatarHora(confronto.data) !== '00:00' ? ` ${formatarHora(confronto.data)}` : ''}
          {confronto.status === 'A_DEFINIR' ? ' · adversário a definir' : ''}
        </p>
      )}

      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <EscudoJogo src={LOGOS_TIMES[confronto.timeA]} fallback={null} nome={confronto.timeA} className="w-7 h-7 shrink-0" />
          <span className={`text-sm font-bold truncate ${destaqueA ? 'text-red-300' : 'text-white'}`}>
            {confronto.timeA}
          </span>
        </div>
        <span className="text-[10px] text-slate-500 font-semibold px-1">VS</span>
        <div className="flex items-center gap-2 min-w-0 flex-1 justify-end">
          <span className={`text-sm font-bold truncate ${destaqueB ? 'text-red-300' : 'text-white'}`}>
            {confronto.timeB}
          </span>
          <EscudoJogo src={LOGOS_TIMES[confronto.timeB]} fallback={null} nome={confronto.timeB} className="w-7 h-7 shrink-0" />
        </div>
      </div>

      <div className="space-y-1 border-t border-slate-800 pt-2">
        <LinhaJogo rotulo="Ida" jogo={confronto.ida} />
        <LinhaJogo rotulo="Volta" jogo={confronto.volta} />
        <p className="text-xs text-slate-300">
          <span className="text-slate-500">Agregado:</span>{' '}
          {confronto.agregado.timeA == null || confronto.agregado.timeB == null ? (
            <span className="italic text-slate-500">a definir</span>
          ) : (
            <>
              <span className="font-bold text-white tabular-nums">{confronto.agregado.timeA}</span>
              <span className="text-slate-500"> x </span>
              <span className="font-bold text-white tabular-nums">{confronto.agregado.timeB}</span>
            </>
          )}
        </p>
      </div>
    </div>
  );
}

function ChaveMataMata({ dados }) {
  return (
    <div>
      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-2">
        {dados.fase}
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {dados.confrontos.map((c) => (
          <CardMataMata key={c.id} confronto={c} />
        ))}
      </div>
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
    { id: 'copadobrasil', rotulo: 'Copa do Brasil' },
    { id: 'carioca', rotulo: 'Carioca' },
  ];

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6">
      <CabecalhoCard
        icone={<RiTrophyLine className="w-5 h-5" />}
        titulo="Tabela de Classificação"
        descricao="Brasileirão, Libertadores, Copa do Brasil e Carioca"
      />

      <div className="flex items-center gap-2 mb-5 flex-wrap">
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

      {aba === 'brasileirao' && (
        <TabelaClassificacao linhas={classificacaoBrasileirao} />
      )}

      {aba === 'libertadores' && (
        <div className="space-y-5">
          <ChaveMataMata dados={libertadores} />
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

      {aba === 'copadobrasil' && (
        <div className="space-y-5">
          <ChaveMataMata dados={copaDoBrasil} />
          <p className="text-xs text-slate-500">
            Estrutura de mata-mata (ida/volta, agregado e classificado). Times ainda não
            definidos aparecem como &quot;A definir&quot;.
          </p>
        </div>
      )}

      {aba === 'carioca' && (
        <div className="space-y-5">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-2">
            Taça Guanabara
          </h3>
          <TabelaClassificacao linhas={carioca.classificacao || carioca} />

          {Array.isArray(carioca.flamengoJogos) && carioca.flamengoJogos.length > 0 && (
            <div>
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-2">
                Jogos do Flamengo no Estadual
              </h3>
              <div className="space-y-2">
                {carioca.flamengoJogos.map((j, i) => {
                  const encerrado = j.placarMandante != null && j.placarVisitante != null;
                  return (
                    <div
                      key={i}
                      className="flex items-center justify-between gap-2 rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <EscudoJogo
                          src={j.isHome ? LOGOS_TIMES['Flamengo'] : j.adversarioLogo}
                          fallback={null}
                          nome={j.isHome ? 'Flamengo' : j.adversario}
                          className="w-6 h-6 shrink-0"
                        />
                        <span className="text-sm font-semibold truncate text-white">
                          {j.mandante}
                        </span>
                        <span className="text-slate-500 text-xs">x</span>
                        <span className="text-sm font-semibold truncate text-white">
                          {j.visitante}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {encerrado ? (
                          <span className="font-bold text-white tabular-nums text-sm">
                            {j.placarMandante} x {j.placarVisitante}
                          </span>
                        ) : (
                          <span className="text-xs italic text-slate-500">a definir</span>
                        )}
                        {j.data && (
                          <span className="text-[11px] text-slate-400">
                            {formatarData(j.data)}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
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
          <CardOdds />
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