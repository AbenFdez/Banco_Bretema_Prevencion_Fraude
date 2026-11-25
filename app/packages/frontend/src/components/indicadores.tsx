import type { Alerta, Revision } from '@/hooks/use-consola';
import { esHoy, euros } from '@/lib/formato';
import { cn } from '@/lib/utils';

interface IndicadoresProps {
  pendientes: Alerta[];
  revisiones: Revision[];
}

export function Indicadores({ pendientes, revisiones }: IndicadoresProps) {
  const altas = pendientes.filter((a) => a.prioridad === 'Alta').length;
  const hoy = revisiones.filter((r) => esHoy(r.revisadaEn));
  const fraudesHoy = hoy.filter((r) => r.decision === 'Fraude confirmado').length;
  const enRevision = pendientes.reduce((total, a) => total + (a.importe ?? 0), 0);

  const tarjetas = [
    { etiqueta: 'Alertas pendientes', valor: String(pendientes.length), nota: 'abiertas y sin decidir' },
    { etiqueta: 'Prioridad alta', valor: String(altas), nota: 'puntuación de 80 o más', destacado: altas > 0 },
    { etiqueta: 'Decididas hoy', valor: String(hoy.length), nota: `${fraudesHoy} con fraude confirmado` },
    { etiqueta: 'Importe en revisión', valor: euros(enRevision), nota: 'operaciones que dispararon las alertas' },
  ];

  return (
    <section aria-label="Indicadores" className="grid grid-cols-2 gap-300 lg:grid-cols-4">
      {tarjetas.map((t) => (
        <div
          key={t.etiqueta}
          className={cn(
            'rounded-xl border bg-card px-400 py-300',
            t.destacado ? 'border-riesgo-alto/40' : 'border-border'
          )}
        >
          <p className="text-200 font-semibold uppercase tracking-wide text-muted-foreground">{t.etiqueta}</p>
          <p
            className={cn(
              'mt-100 font-[family-name:var(--font-numeric)] text-[length:var(--text-600)] leading-600',
              t.destacado ? 'text-riesgo-alto' : 'text-foreground'
            )}
          >
            {t.valor}
          </p>
          <p className="text-200 text-muted-foreground">{t.nota}</p>
        </div>
      ))}
    </section>
  );
}
