import { DECISIONES, type Decision } from '@rayfin-app/shared';
import { CheckCircle2, ShieldAlert, ShieldCheck, UserRoundSearch } from 'lucide-react';
import { useId, useState, type FormEvent } from 'react';

import type { Alerta, NuevaRevision } from '@/hooks/use-consola';
import { mensajeError } from '@/lib/formato';
import { cn } from '@/lib/utils';

const OPCIONES: Record<Decision, { icono: typeof ShieldAlert; texto: string; clase: string }> = {
  'Fraude confirmado': {
    icono: ShieldAlert,
    texto: 'El cliente no reconoce la operación',
    clase: 'peer-checked:border-riesgo-alto peer-checked:bg-riesgo-alto/10',
  },
  'Falso positivo': {
    icono: ShieldCheck,
    texto: 'La operación es legítima',
    clase: 'peer-checked:border-exito peer-checked:bg-exito/10',
  },
  'Escalada al gestor': {
    icono: UserRoundSearch,
    texto: 'Hay que hablar con el cliente',
    clase: 'peer-checked:border-riesgo-medio peer-checked:bg-riesgo-medio/10',
  },
};

interface FormularioProps {
  alerta: Alerta;
  alRegistrar: (revision: NuevaRevision) => Promise<unknown>;
}

/** Se monta con `key={alerta.alertaId}`, así que empieza limpio en cada alerta. */
export function FormularioDecision({ alerta, alRegistrar }: FormularioProps) {
  const id = useId();
  const [decision, setDecision] = useState<Decision | null>(null);
  const [bloquear, setBloquear] = useState(false);
  const [comentario, setComentario] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function elegir(nueva: Decision) {
    setDecision(nueva);
    setBloquear(nueva === 'Fraude confirmado');
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    if (!decision) return;
    setEnviando(true);
    setError(null);
    try {
      await alRegistrar({ alertaId: alerta.alertaId, decision, bloquearTarjeta: bloquear, comentario });
    } catch (e) {
      setError(mensajeError(e));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={enviar} className="space-y-300 rounded-xl border border-border bg-card p-400">
      <fieldset className="space-y-200">
        <legend className="mb-200 text-300 font-semibold text-foreground">Decisión de la analista</legend>
        <div className="grid gap-200 sm:grid-cols-3">
          {DECISIONES.map((d) => {
            const { icono: Icono, texto, clase } = OPCIONES[d];
            return (
              <label key={d} className="block cursor-pointer">
                <input
                  type="radio"
                  name={`${id}-decision`}
                  value={d}
                  checked={decision === d}
                  onChange={() => elegir(d)}
                  className="peer sr-only"
                />
                <span
                  className={cn(
                    'flex h-full flex-col gap-100 rounded-lg border border-border px-300 py-200 transition hover:bg-hover peer-focus-visible:ring-2 peer-focus-visible:ring-ring',
                    clase
                  )}
                >
                  <span className="flex items-center gap-100 text-300 font-semibold text-foreground">
                    <Icono aria-hidden="true" className="icon-size-200" />
                    {d}
                  </span>
                  <span className="text-200 text-muted-foreground">{texto}</span>
                </span>
              </label>
            );
          })}
        </div>
      </fieldset>

      <label className="flex items-center gap-200 text-300 text-foreground">
        <input
          type="checkbox"
          checked={bloquear}
          onChange={(e) => setBloquear(e.target.checked)}
          className="size-4 accent-[var(--color-riesgo-alto)]"
        />
        Pedir el bloqueo de la tarjeta •••• {alerta.ultimosDigitos}
      </label>

      <div className="space-y-100">
        <label htmlFor={`${id}-comentario`} className="text-300 font-medium text-foreground">
          Comentario <span className="font-normal text-muted-foreground">(opcional)</span>
        </label>
        <textarea
          id={`${id}-comentario`}
          value={comentario}
          onChange={(e) => setComentario(e.target.value)}
          maxLength={1000}
          rows={2}
          placeholder="Por ejemplo: el cliente confirma por teléfono que no ha hecho estas compras."
          className="w-full rounded-lg border border-input bg-background px-300 py-200 text-300 text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
      </div>

      {error ? (
        <p role="alert" className="text-300 text-riesgo-alto">
          {error}
        </p>
      ) : null}

      <div className="flex items-center justify-between gap-300">
        <p className="text-200 text-muted-foreground">
          La decisión se guarda en la SQL database de la app y queda registrada con tu usuario.
        </p>
        <button
          type="submit"
          disabled={!decision || enviando}
          className="inline-flex shrink-0 items-center gap-200 rounded-lg bg-primary px-400 py-200 text-300 font-semibold text-primary-foreground shadow-sm transition hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <CheckCircle2 aria-hidden="true" className="icon-size-200" />
          {enviando ? 'Guardando…' : 'Registrar decisión'}
        </button>
      </div>
    </form>
  );
}
