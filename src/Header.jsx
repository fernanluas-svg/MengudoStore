import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { FiHome, FiCalendar } from 'react-icons/fi';
import tacasImg from './assets/tacas.png';

const botaoNavegacao = ({ isActive }) =>
  `flex items-center gap-1.5 sm:gap-2 px-3 sm:px-5 py-2 sm:py-2.5 rounded-lg text-sm font-semibold border-2 transition-all duration-200 whitespace-nowrap ${
    isActive
      ? 'bg-white text-slate-900 border-white shadow-[0_0_18px_rgba(255,255,255,0.4)]'
      : 'text-white border-white/80 hover:bg-white/10 hover:border-white hover:shadow-[0_0_14px_rgba(255,255,255,0.25)] hover:-translate-y-0.5'
  }`;

export default function Header() {
  const [headerVisivel, setHeaderVisivel] = useState(true);

  useEffect(() => {
    let ultimaPosicao = window.scrollY;

    const aoRolar = () => {
      const posicaoAtual = window.scrollY;

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

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur-md transition-transform duration-300 ease-in-out ${
        headerVisivel ? 'translate-y-0' : '-translate-y-full'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-3">
        <NavLink to="/" className="flex items-center gap-3">
          <img
            src="https://i.ibb.co/WvsR3rBX/Fundo-preto.png"
            alt="Escudo Mengudo Store"
            className="h-16 w-auto object-contain drop-shadow-lg"
          />
          <div className="flex flex-col leading-tight">
            <div className="flex items-center gap-2">
              <span className="text-xl md:text-3xl font-black text-white tracking-wide">
                MENGUDO <span className="text-red-500">STORE</span>
              </span>
              <div className="hidden sm:flex items-center gap-1">
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
        </NavLink>

        <nav className="flex items-center gap-2 sm:gap-3">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center justify-center w-10 h-10 sm:w-auto sm:h-auto sm:gap-2 sm:px-5 sm:py-2.5 rounded-lg border-2 transition-all duration-200 ${
                isActive
                  ? 'bg-white text-slate-900 border-white shadow-[0_0_18px_rgba(255,255,255,0.4)] sm:hover:-translate-y-0.5'
                  : 'bg-white text-slate-900 border-white sm:bg-transparent sm:text-white sm:border-white/80 sm:hover:bg-white/10 sm:hover:border-white sm:hover:shadow-[0_0_14px_rgba(255,255,255,0.25)] sm:hover:-translate-y-0.5'
              }`
            }
          >
            <FiHome className="w-4 h-4 sm:w-[18px] sm:h-[18px]" />
            <span className="hidden sm:inline">Início</span>
          </NavLink>
          <NavLink to="/agenda" className={botaoNavegacao}>
            <FiCalendar className="w-4 h-4 sm:w-[18px] sm:h-[18px]" />
            <span className="hidden sm:inline">Agenda de Jogos</span>
            <span className="sm:hidden">Agenda</span>
          </NavLink>
        </nav>
      </div>
    </header>
  );
}