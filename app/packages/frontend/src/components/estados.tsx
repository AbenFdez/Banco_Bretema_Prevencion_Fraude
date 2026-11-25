import { AlertTriangle, Inbox, RotateCw } from 'lucide-react';

export function Cargando({ filas = 4, etiqueta = 'Cargando' }: { filas?: number; etiqueta?: string }) {
  return (
    <div className="space-y-200" role="status" aria-busy="true" aria-label={etiqueta}>
      {Array.from({ length: filas }, (_, i) => (
        <div key={i} className="h-16 animate-pulse rounded-xl bg-muted" />
      ))}
    </div>
  );
}

export function Vacio({ titulo, pista }: { titulo: string; pista?: string }) {
  return (
    <div className="flex flex-col items-center gap-200 rounded-xl border border-dashed border-border px-600 py-800 text-center">
      <Inbox aria-hidden="true" className="icon-size-500 text-muted-foreground" />
      <p className="text-400 font-semibold text-foreground">{titulo}</p>
      {pista ? <p className="max-w-sm text-300 text-muted-foreground">{pista}</p> : null}
    </div>
  );
}

export function ErrorCarga({ mensaje, alReintentar }: { mensaje: string; alReintentar?: () => void }) {
  return (
    <div
      role="alert"
      className="flex items-start gap-300 rounded-xl border border-riesgo-alto/40 bg-riesgo-alto/10 px-400 py-300 text-foreground"
    >
      <AlertTriangle aria-hidden="true" className="mt-100 icon-size-300 shrink-0 text-riesgo-alto" />
      <div className="flex-1 space-y-100">
        <p className="text-300 font-semibold">No se han podido cargar los datos</p>
        <p className="text-300 text-muted-foreground">{mensaje}</p>
      </div>
      {alReintentar ? (
        <button
          type="button"
          onClick={alReintentar}
          className="inline-flex items-center gap-100 rounded-lg border border-border bg-card px-300 py-100 text-300 font-medium hover:bg-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <RotateCw aria-hidden="true" className="icon-size-200" />
          Reintentar
        </button>
      ) : null}
    </div>
  );
}
