import { useEffect, useLayoutEffect, useRef, useState } from 'react';

const PRODUCTS = [
  {
    id: 1,
    name: "COPO TÉRMICO EMBORRACHADO - FLAMENGO",
    image: "https://down-br.img.susercontent.com/file/br-11134207-820m5-mrb1f3b60c9247@resize_w900_nl.webp",
    link: "https://s.shopee.com.br/8pl4E4pT9u",
    rating: 4.8
  },
  {
    id: 2,
    name: "Faca para Churrasco Oficial do Flamengo – Licenciada BrasFoot",
    image: "https://down-br.img.susercontent.com/file/br-11134207-81z1k-mg85u1di6qyo8c@resize_w900_nl.webp",
    link: "https://s.shopee.com.br/9ANucmLNVC",
    rating: 4.9
  },
  {
    id: 3,
    name: "Camisa Flamengo Stick Masculina Oficial",
    image: "https://down-br.img.susercontent.com/file/br-11134207-7r98o-ltax1oa3l1q4ea@resize_w900_nl.webp",
    link: "https://s.shopee.com.br/30nHHhKiuL",
    rating: 4.7
  },
  {
    id: 4,
    name: "Taça Dublin Cerveja 400ml Flamengo Série Ouro",
    image: "https://down-br.img.susercontent.com/file/br-11134207-820lc-moa08b94uyv79e@resize_w900_nl.webp",
    link: "https://s.shopee.com.br/W5wJDekXS",
    rating: 4.8
  },
  {
    id: 5,
    name: "Manto Flamengo Masculina Jogo 3 Adidas 2026",
    image: "https://down-br.img.susercontent.com/file/sg-11134201-7rbkk-llu5lizbeghx08@resize_w900_nl.webp",
    link: "https://s.shopee.com.br/1Lf3IqqcEX",
    rating: 5.0
  },
  {
    id: 6,
    name: "Chinelo Havaianas Top Times Flamengo",
    image: "https://down-br.img.susercontent.com/file/br-11134207-81z1k-mh9hl9okbl6o65@resize_w900_nl.webp",
    link: "https://s.shopee.com.br/112CuMxadU",
    rating: 4.8
  }
];

export default function NovidadesCarrossel() {
  const containerRef = useRef(null);
  const firstCardRef = useRef(null);
  const [offset, setOffset] = useState(0);
  const [containerW, setContainerW] = useState(0);
  const [cardW, setCardW] = useState(220);
  const [gap, setGap] = useState(24);
  const [isPaused, setIsPaused] = useState(false);
  const isPausedRef = useRef(false);
  isPausedRef.current = isPaused;
  const [hoveredId, setHoveredId] = useState(null);

  const step = cardW + gap;
  const setWidth = PRODUCTS.length * step;
  const items = [...PRODUCTS, ...PRODUCTS, ...PRODUCTS];

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
      if (firstCardRef.current) {
        const w = firstCardRef.current.offsetWidth;
        if (w > 0) setCardW(w);
        const cs = getComputedStyle(firstCardRef.current);
        const g = parseFloat(cs.marginRight) || 24;
        if (g > 0) setGap(g);
      }
    };
    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, []);

  const containerCenter = containerW / 2;
  const isMobile = containerW > 0 && containerW < 768;
  const focusedScale = isMobile ? 1.1 : 1.18;
  const maxLift = isMobile ? -12 : -15;

  let activeIdx = 0;
  let minDist = Infinity;
  for (let i = 0; i < items.length; i++) {
    const cardCenter = i * step + cardW / 2 - offset;
    const d = Math.abs(cardCenter - containerCenter);
    if (d < minDist) {
      minDist = d;
      activeIdx = i;
    }
  }

  return (
    <div
      ref={containerRef}
      className="relative overflow-x-clip overflow-y-visible pt-10 pb-8 select-none"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* Sombras laterais para dar profundidade */}
      <div className="pointer-events-none absolute inset-y-0 left-0 w-12 sm:w-32 z-20 bg-gradient-to-r from-slate-950 to-transparent"></div>
      <div className="pointer-events-none absolute inset-y-0 right-0 w-12 sm:w-32 z-20 bg-gradient-to-l from-slate-950 to-transparent"></div>

      <div
        className="flex items-center will-change-transform"
        style={{ transform: `translateX(${-offset}px)` }}
      >
        {items.map((product, i) => {
          const cardCenter = i * step + cardW / 2 - offset;
          const dist = Math.abs(cardCenter - containerCenter);
          const t = Math.min(dist / (cardW * 1.6), 1);

          const isHovered = hoveredId === product.id;
          const isCentered = i === activeIdx;
          const isFocused = hoveredId !== null ? isHovered : isCentered;

          const scale = isFocused ? focusedScale : 1 + (focusedScale - 1) * (1 - t);
          const opacity = isFocused ? 1 : 1 - 0.3 * t;
          const lift = isFocused ? maxLift : maxLift * (1 - t);
          const zIndex = isFocused ? 40 : Math.round((1 - t) * 20);

          return (
            <div
              key={`${product.id}-${i}`}
              ref={i === 0 ? firstCardRef : undefined}
              onMouseEnter={() => setHoveredId(product.id)}
              onMouseLeave={() => setHoveredId(null)}
              className="shrink-0 w-[220px] md:w-[280px] transition-opacity duration-300"
              style={{
                marginRight: gap,
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
                <div className="relative h-40 md:h-48 bg-slate-800 overflow-hidden">
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-3 right-3 bg-slate-950/80 backdrop-blur-sm text-xs text-yellow-400 px-2 py-1 rounded-full flex items-center gap-1 border border-slate-700">
                    {product.rating ? `⭐ ${product.rating}` : 'NOVO'}
                  </div>
                </div>

                <div className="p-3 md:p-4">
                  <h3 className="text-sm font-semibold text-slate-100 line-clamp-2 h-10 leading-tight">
                    {product.name}
                  </h3>
                  <div className="mt-3">
                    <a
                      href={product.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full flex items-center justify-center text-xs font-bold bg-red-600 hover:bg-red-500 text-white px-3 md:px-4 py-2 rounded-full transition-colors shadow-lg shadow-red-900/20 whitespace-nowrap"
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