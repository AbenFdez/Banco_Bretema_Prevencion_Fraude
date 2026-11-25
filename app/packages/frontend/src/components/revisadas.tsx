import { Lock } from 'lucide-react';

import { Vacio } from '@/components/estados';
import { InsigniaDecision } from '@/components/insignias';
import type { Alerta, Revision } from '@/hooks/use-consola';
import { euros, fecha, horaLocal } from '@/lib/formato';

interface RevisadasProps {
  revisiones: Revision[];
  alertasPorId: Map<string, Alerta>;
}

/** Decisiones registradas en la consola por todo el equipo, de la más reciente a la más antigua. */
export function Revisadas({ revisiones, alertasPorId }: RevisadasProps) {
  if (revisiones.length === 0) {
    return (
      <Vacio
        titulo="Todavía no hay decisiones"
        pista="Cuando registres una decisión sobre una alerta aparecerá aquí, y el notebook 02 la llevará al Lakehouse y a la ontología."
      />
    );
  }
  return (
    <div className="overflow-x-auto rounded-xl border border-border bg-card">
      <table className="w-full text-left text-300">
        <thead className="bg-muted text-200 uppercase tracking-wide text-muted-foreground">
          <tr>
            <th className="px-300 py-200 font-semibold">Cuándo</th>
            <th className="px-300 py-200 font-semibold">Alerta</th>
            <th className="px-300 py-200 font-semibold">Cliente</th>
            <th className="px-300 py-200 font-semibold">Decisión</th>
            <th className="px-300 py-200 font-semibold">Comentario</th>
            <th className="px-300 py-200 font-semibold">Analista</th>
          </tr>
        </thead>
        <tbody>
          {revisiones.map((r) => {
            const alerta = alertasPorId.get(r.alertaId);
            return (
              <tr key={r.id} className="border-t border-border align-top">
                <td className="whitespace-nowrap px-300 py-200">
                  {fecha(r.revisadaEn)} · {horaLocal(r.revisadaEn)}
                </td>
                <td className="px-300 py-200">
                  <p className="font-[family-name:var(--font-monospace)]">{r.alertaId}</p>
                  {alerta ? (
                    <p className="text-200 text-muted-foreground">
                      {alerta.tipoAlerta} · {euros(alerta.importe)}
                    </p>
                  ) : null}
                </td>
                <td className="px-300 py-200">{alerta?.cliente ?? '—'}</td>
                <td className="px-300 py-200">
                  <div className="flex flex-col items-start gap-100">
                    <InsigniaDecision decision={r.decision} />
                    {r.bloquearTarjeta ? (
                      <span className="inline-flex items-center gap-100 text-200 text-riesgo-alto">
                        <Lock aria-hidden="true" className="icon-size-100" />
                        bloqueo de tarjeta solicitado
                      </span>
                    ) : null}
                  </div>
                </td>
                <td className="max-w-xs px-300 py-200 text-muted-foreground">{r.comentario ?? '—'}</td>
                <td className="px-300 py-200 text-muted-foreground">{r.analistaEmail}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
