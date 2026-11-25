import { CreditCard, MapPin, Store, UserRound } from 'lucide-react';
import type { ReactNode } from 'react';

import { Cargando, ErrorCarga } from '@/components/estados';
import { FormularioDecision } from '@/components/formulario-decision';
import { InsigniaPrioridad, Puntuacion } from '@/components/insignias';
import type { Alerta, NuevaRevision } from '@/hooks/use-consola';
import { useDetalle } from '@/hooks/use-detalle';
import { euros, fecha, fechaHora, plural } from '@/lib/formato';
import { cn } from '@/lib/utils';

interface DetalleProps {
  alerta: Alerta;
  alRegistrar: (revision: NuevaRevision) => Promise<unknown>;
}

function Bloque({ icono, titulo, children }: { icono: ReactNode; titulo: string; children: ReactNode }) {
  return (
    <div className="rounded-xl border border-border bg-card p-300">
      <p className="mb-100 flex items-center gap-100 text-200 font-semibold uppercase tracking-wide text-muted-foreground">
        {icono}
        {titulo}
      </p>
      {children}
    </div>
  );
}

export function DetalleAlerta({ alerta, alRegistrar }: DetalleProps) {
  const { cargando, error, movimientos, historial } = useDetalle(alerta);
  const veces = alerta.importe && alerta.gastoMedio ? alerta.importe / alerta.gastoMedio : null;
  const falsos = historial.filter((h) => h.resolucion === 'Falso positivo').length;
  const fraudes = historial.filter((h) => h.resolucion === 'Fraude confirmado').length;

  return (
    <article aria-labelledby="titulo-detalle" className="flex flex-col gap-400">
      <header className="flex items-start gap-400">
        <Puntuacion valor={alerta.puntuacion} tamano="lg" />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-200">
            <h2 id="titulo-detalle" className="font-heading text-[length:var(--text-600)] leading-600 text-foreground">
              {alerta.tipoAlerta}
            </h2>
            <InsigniaPrioridad prioridad={alerta.prioridad} />
          </div>
          <p className="text-300 text-muted-foreground">
            <span className="font-[family-name:var(--font-monospace)]">{alerta.alertaId}</span> ·{' '}
            {fechaHora(alerta.fechaHora)} · transacción{' '}
            <span className="font-[family-name:var(--font-monospace)]">{alerta.transaccionId}</span>
          </p>
        </div>
      </header>

      <p className="rounded-xl border-l-4 border-brand bg-accent px-400 py-300 text-300 text-accent-foreground">
        {alerta.motivo}
      </p>

      <div className="grid gap-300 md:grid-cols-3">
        <Bloque icono={<UserRound aria-hidden="true" className="icon-size-200" />} titulo="Cliente">
          <p className="text-300 font-semibold text-foreground">{alerta.cliente}</p>
          <p className="text-200 text-muted-foreground">
            {alerta.segmento} · {alerta.provinciaCliente}
          </p>
          <p className="text-200 text-muted-foreground">
            Oficina {alerta.oficina} · gestor/a {alerta.gestor}
          </p>
        </Bloque>
        <Bloque icono={<CreditCard aria-hidden="true" className="icon-size-200" />} titulo="Tarjeta">
          <p className="font-[family-name:var(--font-monospace)] text-300 font-semibold text-foreground">
            {alerta.tipoTarjeta} •••• {alerta.ultimosDigitos}
          </p>
          <p className="text-200 text-muted-foreground">Estado: {alerta.estadoTarjeta}</p>
          <p className="text-200 text-muted-foreground">
            Historial del cliente:{' '}
            {historial.length === 0
              ? 'sin alertas previas'
              : `${plural(falsos, 'falso positivo', 'falsos positivos')}, ${plural(fraudes, 'fraude', 'fraudes')}`}
          </p>
        </Bloque>
        <Bloque icono={<Store aria-hidden="true" className="icon-size-200" />} titulo="Operación">
          <p className="font-[family-name:var(--font-numeric)] text-[length:var(--text-500)] text-foreground">
            {euros(alerta.importe)}
          </p>
          <p className="text-200 text-muted-foreground">
            {alerta.comercio} · {alerta.categoriaComercio}
          </p>
          <p className="flex items-center gap-100 text-200 text-muted-foreground">
            <MapPin aria-hidden="true" className="icon-size-100" />
            {alerta.canal} · {alerta.municipioComercio ? `${alerta.municipioComercio}, ` : ''}
            {alerta.pais}
          </p>
          {veces ? (
            <p className={cn('text-200', veces >= 4 ? 'text-riesgo-alto' : 'text-muted-foreground')}>
              {veces.toLocaleString('es-ES', { maximumFractionDigits: 1 })} veces su gasto medio (
              {euros(alerta.gastoMedio)})
            </p>
          ) : null}
        </Bloque>
      </div>

      <section aria-labelledby="titulo-movimientos" className="rounded-xl border border-border bg-card p-300">
        <h3 id="titulo-movimientos" className="mb-200 text-300 font-semibold text-foreground">
          Últimos movimientos de la tarjeta
        </h3>
        {cargando ? (
          <Cargando filas={3} etiqueta="Cargando movimientos" />
        ) : error ? (
          <ErrorCarga mensaje={error} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-300">
              <thead className="text-200 uppercase tracking-wide text-muted-foreground">
                <tr>
                  <th className="py-100 pr-300 font-semibold">Fecha</th>
                  <th className="py-100 pr-300 font-semibold">Comercio</th>
                  <th className="py-100 pr-300 font-semibold">Canal</th>
                  <th className="py-100 pr-300 font-semibold">País</th>
                  <th className="py-100 text-right font-semibold">Importe</th>
                </tr>
              </thead>
              <tbody>
                {movimientos.map((m) => {
                  const esLaAlerta = m.transaccionId === alerta.transaccionId;
                  return (
                    <tr
                      key={m.transaccionId}
                      className={cn('border-t border-border', esLaAlerta && 'bg-riesgo-alto/10 font-semibold')}
                    >
                      <td className="whitespace-nowrap py-100 pr-300">{fechaHora(m.fechaHora)}</td>
                      <td className="py-100 pr-300">
                        {m.comercio}
                        {m.riesgoComercio === 'Alto' ? (
                          <span className="ml-100 rounded-full bg-riesgo-alto/10 px-100 text-200 text-riesgo-alto">
                            riesgo alto
                          </span>
                        ) : null}
                      </td>
                      <td className="py-100 pr-300">{m.canal}</td>
                      <td className="py-100 pr-300">{m.pais}</td>
                      <td className="whitespace-nowrap py-100 text-right font-[family-name:var(--font-numeric)]">
                        {euros(m.importe)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        {historial.length > 0 ? (
          <p className="mt-200 text-200 text-muted-foreground">
            Última alerta cerrada del cliente: {historial[0].tipoAlerta} del {fecha(historial[0].fechaHora)} (
            {historial[0].resolucion.toLowerCase()}).
          </p>
        ) : null}
      </section>

      <FormularioDecision key={alerta.alertaId} alerta={alerta} alRegistrar={alRegistrar} />
    </article>
  );
}
