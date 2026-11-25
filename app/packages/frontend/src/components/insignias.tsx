import type { Decision } from '@rayfin-app/shared';

import { cn } from '@/lib/utils';

const COLOR_PRIORIDAD = {
  Alta: 'border-riesgo-alto/40 bg-riesgo-alto/10 text-riesgo-alto',
  Media: 'border-riesgo-medio/40 bg-riesgo-medio/10 text-riesgo-medio',
  Baja: 'border-riesgo-bajo/40 bg-riesgo-bajo/10 text-riesgo-bajo',
} as const;

export function InsigniaPrioridad({ prioridad }: { prioridad: 'Alta' | 'Media' | 'Baja' }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-200 py-100-nudge text-[length:var(--text-200)] font-semibold uppercase tracking-wide',
        COLOR_PRIORIDAD[prioridad]
      )}
    >
      {prioridad}
    </span>
  );
}

/** Puntuación de riesgo de 0 a 100 en un anillo, con el color de su prioridad. */
export function Puntuacion({ valor, tamano = 'md' }: { valor: number; tamano?: 'md' | 'lg' }) {
  const color =
    valor >= 80 ? 'var(--color-riesgo-alto)' : valor >= 60 ? 'var(--color-riesgo-medio)' : 'var(--color-riesgo-bajo)';
  const grande = tamano === 'lg';
  return (
    <div
      role="img"
      aria-label={`Puntuación de riesgo ${valor} sobre 100`}
      className={cn('relative grid shrink-0 place-items-center rounded-full', grande ? 'size-16' : 'size-11')}
      style={{ background: `conic-gradient(${color} ${valor * 3.6}deg, var(--color-muted) 0deg)` }}
    >
      <span
        className={cn(
          'grid place-items-center rounded-full bg-card font-[family-name:var(--font-numeric)] font-medium text-foreground',
          grande ? 'size-12 text-[length:var(--text-500)]' : 'size-8 text-[length:var(--text-300)]'
        )}
      >
        {valor}
      </span>
    </div>
  );
}

const COLOR_DECISION: Record<Decision, string> = {
  'Fraude confirmado': 'border-riesgo-alto/40 bg-riesgo-alto/10 text-riesgo-alto',
  'Falso positivo': 'border-exito/40 bg-exito/10 text-exito',
  'Escalada al gestor': 'border-riesgo-medio/40 bg-riesgo-medio/10 text-riesgo-medio',
};

export function InsigniaDecision({ decision }: { decision: Decision }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-200 py-100-nudge text-[length:var(--text-200)] font-semibold',
        COLOR_DECISION[decision]
      )}
    >
      {decision}
    </span>
  );
}
