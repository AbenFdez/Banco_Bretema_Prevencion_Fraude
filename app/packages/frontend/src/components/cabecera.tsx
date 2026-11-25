import { Moon, RotateCw, Sun } from 'lucide-react';

import { useTheme } from '@/hooks/theme.context';

interface CabeceraProps {
  email: string | null;
  recargando: boolean;
  alRecargar: () => void;
}

/** Banda azul marino con el emblema del banco, como el fondo del logo. */
export function Cabecera({ email, recargando, alRecargar }: CabeceraProps) {
  const { isDark, toggleTheme } = useTheme();
  const botonClaro =
    'inline-flex items-center gap-100 rounded-lg border border-white/20 px-300 py-100 text-300 text-white/90 transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 disabled:opacity-50';

  return (
    <header className="bg-marino text-white">
      <div className="mx-auto flex max-w-[1440px] flex-wrap items-center gap-400 px-600 py-300">
        <img src="/emblema-bretema.png" alt="" className="size-12 rounded-lg" width={48} height={48} />
        <div className="mr-auto">
          <p className="font-heading text-[length:var(--text-500)] leading-500 tracking-[0.08em]">BANCO BRÉTEMA</p>
          <p className="text-200 uppercase tracking-[0.14em] text-white/70">
            Prevención del fraude · Consola de alertas
          </p>
        </div>
        {email ? <span className="hidden text-300 text-white/80 sm:inline">{email}</span> : null}
        <button type="button" onClick={alRecargar} disabled={recargando} className={botonClaro}>
          <RotateCw aria-hidden="true" className={recargando ? 'icon-size-200 animate-spin' : 'icon-size-200'} />
          Actualizar
        </button>
        <button
          type="button"
          onClick={toggleTheme}
          className={botonClaro}
          aria-label={isDark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'}
        >
          {isDark ? (
            <Sun aria-hidden="true" className="icon-size-200" />
          ) : (
            <Moon aria-hidden="true" className="icon-size-200" />
          )}
        </button>
      </div>
    </header>
  );
}
