import { useMemo, useState } from 'react';

import { InsigniaPrioridad, Puntuacion } from '@/components/insignias';
import { Vacio } from '@/components/estados';
import type { Alerta } from '@/hooks/use-consola';
import { euros, fechaHora } from '@/lib/formato';
import { cn } from '@/lib/utils';

const FILTROS = ['Todas', 'Alta', 'Media', 'Baja'] as const;
type Filtro = (typeof FILTROS)[number];

interface ColaProps {
  alertas: Alerta[];
  seleccionada: string | null;
  alSeleccionar: (alertaId: string) => void;
}

/** Cola de alertas pendientes, de mayor a menor puntuación de riesgo. */
export function ColaAlertas({ alertas, seleccionada, alSeleccionar }: ColaProps) {
  const [filtro, setFiltro] = useState<Filtro>('Todas');
  const visibles = useMemo(
    () => (filtro === 'Todas' ? alertas : alertas.filter((a) => a.prioridad === filtro)),
    [alertas, filtro]
  );

  return (
    <section aria-label="Alertas pendientes" className="flex min-h-0 flex-col gap-300">
      <div role="group" aria-label="Filtrar por prioridad" className="flex gap-100">
        {FILTROS.map((f) => {
          const n = f === 'Todas' ? alertas.length : alertas.filter((a) => a.prioridad === f).length;
          return (
            <button
              key={f}
              type="button"
              aria-pressed={filtro === f}
              onClick={() => setFiltro(f)}
              className={cn(
                'rounded-full border px-300 py-100 text-300 font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                filtro === f
                  ? 'border-primary bg-primary text-primary-foreground'
                  : 'border-border bg-card text-foreground hover:bg-hover'
              )}
            >
              {f} <span className="opacity-70">{n}</span>
            </button>
          );
        })}
      </div>

      {visibles.length === 0 ? (
        <Vacio
          titulo="No hay alertas pendientes"
          pista="Cuando el motor antifraude genere alertas nuevas aparecerán aquí."
        />
      ) : (
        <ul className="flex min-h-0 flex-col gap-200 overflow-y-auto pr-100 pb-200">
          {visibles.map((a) => {
            const activa = a.alertaId === seleccionada;
            return (
              <li key={a.alertaId}>
                <button
                  type="button"
                  onClick={() => alSeleccionar(a.alertaId)}
                  aria-current={activa ? 'true' : undefined}
                  className={cn(
                    'flex w-full items-center gap-300 rounded-xl border bg-card px-300 py-300 text-left transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                    activa ? 'border-brand ring-1 ring-brand' : 'border-border hover:bg-hover'
                  )}
                >
                  <Puntuacion valor={a.puntuacion} />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-200">
                      <p className="truncate text-300 font-semibold text-foreground">{a.tipoAlerta}</p>
                      <InsigniaPrioridad prioridad={a.prioridad} />
                    </div>
                    <p className="truncate text-300 text-muted-foreground">
                      {a.cliente} · {a.comercio}
                    </p>
                    <p className="text-200 text-muted-foreground">
                      <span className="font-[family-name:var(--font-monospace)]">{a.alertaId}</span> ·{' '}
                      {fechaHora(a.fechaHora)}
                    </p>
                  </div>
                  <p className="shrink-0 font-[family-name:var(--font-numeric)] text-300 font-medium text-foreground">
                    {euros(a.importe)}
                  </p>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
