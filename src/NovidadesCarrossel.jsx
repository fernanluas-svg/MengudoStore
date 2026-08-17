import { useEffect, useLayoutEffect, useRef, useState } from 'react';

const CARD_W = 260;
const GAP = 24;
const STEP = CARD_W + GAP;

export default function NovidadesCarrossel({ produtos }) {
  const containerRef = useRef(null);
  const [offset, setOffset] = useState(0);
  const [containerW, setContainerW] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const isPausedRef = useRef(false);
  isPausedRef.current = isPaused;
  const [hoveredId, setHoveredId] = useState(null);

  const setWidth = produtos.length * STEP;
  const items = [...produtos, ...produtos, ...produtos];

  useEffect(() => {
    let raf;
    let last = performance.now();

    const tick = (now) => {
      const delta = now - last;
      last = now;
      if (!isPausedRef.current) {
        setOffset((prev) => {
          const next = prev + 0.055 * delta;
          return next >= setWidth ? next - setWidth : next;
        });
      }
      raf = requestAnimationFrame(tick);
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [setWidth]);

  useLayoutEffect(() => {
    const measure = () => {
      if (containerRef.current) {
        setContainerW(containerRef.current.offsetWidth);
      }
    };
    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, []);

  const containerCenter = containerW / 2;

  let activeIdx = 0;
  let minDist = Infinity;
  for (let i = 0; i < items.length; i++) {
    const cardCenter = i * STEP + CARD_W / 2 - offset;
    const d = Math.abs(cardCenter - containerCenter);
    if (d < minDist) {
      minDist = d;
      activeIdx = i;
    }
  }

  return (
    <div
      ref={containerRef}
      className="relative overflow-hidden py-8 select-none"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* Sombras laterais para dar profundidade */}
      <div className="pointer-events-none absolute inset-y-0 left-0 w-16 sm:w-32 z-20 bg-gradient-to-r from-slate-950 to-transparent"></div>
      <div className="pointer-events-none absolute inset-y-0 right-0 w-16 sm:w-32 z-20 bg-gradient-to-l from-slate-950 to-transparent"></div>

      <div
        className="flex items-center will-change-transform"
        style={{ transform: `translateX(${-offset}px)` }}
      >
        {items.map((produto, i) => {
          const cardCenter = i * STEP + CARD_W / 2 - offset;
          const dist = Math.abs(cardCenter - containerCenter);
          const t = Math.min(dist / (CARD_W * 1.6), 1);

          const isHovered = hoveredId === produto.id;
          const isCentered = i === activeIdx;
          const isFocused = hoveredId !== null ? isHovered : isCentered;

          const scale = isFocused ? 1.18 : 1.18 - 0.18 * t;
          const opacity = isFocused ? 1 : 1 - 0.3 * t;
          const lift = isFocused ? -15 : -15 * (1 - t);
          const zIndex = isFocused ? 40 : Math.round((1 - t) * 20);

          return (
            <div
              key={`${produto.id}-${i}`}
              onMouseEnter={() => setHoveredId(produto.id)}
              onMouseLeave={() => setHoveredId(null)}
              className="shrink-0 transition-opacity duration-300"
              style={{
                width: CARD_W,
                marginRight: GAP,
                opacity,
                transform: `translateY(${lift}px) scale(${scale})`,
                zIndex,
                transition: isHovered ? 'transform 200ms ease-out' : 'transform 300ms ease-out',
              }}
            >
              <div
                className={`group bg-slate-900/90 border rounded-xl overflow-hidden transition-all duration-300 ${
                  isFocused
                    ? 'border-red-500 shadow-[0_0_55px_rgba(218,41,28,0.9),0_25px_60px_rgba(218,41,28,0.45)] shadow-red-600/50'
                    : 'border-slate-800 hover:border-red-500/40'
                }`}
              >
                <div className="relative h-48 bg-slate-800 overflow-hidden">
                  <img
                    src={produto.imagem}
                    alt={produto.titulo}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-3 right-3 bg-slate-950/80 backdrop-blur-sm text-xs text-yellow-400 px-2 py-1 rounded-full flex items-center gap-1 border border-slate-700">
                    {produto.avaliacao ? `⭐ ${produto.avaliacao}` : 'NOVO'}
                  </div>
                </div>

                <div className="p-4">
                  <h3 className="text-sm font-semibold text-slate-100 line-clamp-2 h-10 leading-tight">
                    {produto.titulo}
                  </h3>
                  <div className="mt-3 flex items-center justify-between gap-2">
                    <span className="text-lg font-bold text-white">{produto.preco}</span>
                    <a
                      href={produto.linkMercadoLivre}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-medium bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded-full transition-colors shadow-lg shadow-red-900/20 whitespace-nowrap"
                    >
                      Comprar
                    </a>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}