import { useState } from 'react';

import { Cabecera } from '@/components/cabecera';
import { ColaAlertas } from '@/components/cola-alertas';
import { DetalleAlerta } from '@/components/detalle-alerta';
import { Cargando, ErrorCarga, Vacio } from '@/components/estados';
import { Indicadores } from '@/components/indicadores';
import { Revisadas } from '@/components/revisadas';
import { useAuth } from '@/hooks/auth.context';
import { useConsola, type NuevaRevision } from '@/hooks/use-consola';
import { cn } from '@/lib/utils';

type Vista = 'pendientes' | 'revisadas';

function App() {
  const { session } = useAuth();
  const consola = useConsola();
  const [vista, setVista] = useState<Vista>('pendientes');
  const [seleccionada, setSeleccionada] = useState<string | null>(null);
  const [aviso, setAviso] = useState<string | null>(null);

  // Si la alerta elegida deja de estar pendiente (porque se acaba de decidir), se pasa a la primera de la cola
  const alerta = consola.pendientes.find((a) => a.alertaId === seleccionada) ?? consola.pendientes[0] ?? null;

  async function registrar(nueva: NuevaRevision) {
    const revision = await consola.registrar(nueva);
    setAviso(
      `${revision.alertaId}: ${revision.decision.toLowerCase()}${revision.bloquearTarjeta ? ', con bloqueo de tarjeta' : ''}.`
    );
  }

  const pestanas: { id: Vista; texto: string; n: number }[] = [
    { id: 'pendientes', texto: 'Pendientes', n: consola.pendientes.length },
    { id: 'revisadas', texto: 'Decididas en la consola', n: consola.revisiones.length },
  ];

  return (
    <div className="flex min-h-full flex-col bg-background">
      <Cabecera
        email={session?.user?.email ?? null}
        recargando={consola.estado === 'cargando'}
        alRecargar={() => void consola.recargar()}
      />

      <main className="mx-auto flex w-full max-w-[1440px] flex-1 flex-col gap-400 px-600 py-500">
        {consola.estado === 'error' ? (
          <ErrorCarga mensaje={consola.error ?? ''} alReintentar={() => void consola.recargar()} />
        ) : null}

        {consola.estado === 'cargando' && consola.alertas.length === 0 ? (
          <Cargando filas={2} etiqueta="Cargando indicadores" />
        ) : (
          <Indicadores pendientes={consola.pendientes} revisiones={consola.revisiones} />
        )}

        <div className="flex items-end justify-between gap-300 border-b border-border">
          <div role="tablist" aria-label="Vistas de la consola" className="flex gap-100">
            {pestanas.map((p) => (
              <button
                key={p.id}
                type="button"
                role="tab"
                aria-selected={vista === p.id}
                onClick={() => setVista(p.id)}
                className={cn(
                  '-mb-px border-b-2 px-300 py-200 text-300 font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                  vista === p.id
                    ? 'border-brand text-foreground'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                )}
              >
                {p.texto} <span className="font-normal text-muted-foreground">{p.n}</span>
              </button>
            ))}
          </div>
          {aviso ? (
            <p role="status" className="mb-200 truncate text-300 text-exito">
              Decisión registrada · {aviso}
            </p>
          ) : null}
        </div>

        {vista === 'revisadas' ? (
          <Revisadas revisiones={consola.revisiones} alertasPorId={consola.alertasPorId} />
        ) : consola.estado === 'cargando' && consola.alertas.length === 0 ? (
          <Cargando etiqueta="Cargando alertas" />
        ) : (
          <div className="grid min-h-0 flex-1 gap-500 lg:grid-cols-[minmax(320px,400px)_1fr]">
            <div className="flex max-h-[calc(100vh-280px)] min-h-0 flex-col">
              <ColaAlertas
                alertas={consola.pendientes}
                seleccionada={alerta?.alertaId ?? null}
                alSeleccionar={setSeleccionada}
              />
            </div>
            {alerta ? (
              <DetalleAlerta alerta={alerta} alRegistrar={registrar} />
            ) : (
              <Vacio titulo="Cola al día" pista="No quedan alertas abiertas sin decidir." />
            )}
          </div>
        )}
      </main>

      <footer className="px-600 py-300 text-center text-200 text-muted-foreground">
        Banco Brétema es un banco ficticio. Datos sintéticos para la demo de Fabric IQ y Fabric Apps.
      </footer>
    </div>
  );
}

export default App;
