import { useEffect, useState } from 'react';

import type { Alerta } from '@/hooks/use-consola';
import { aFecha, mensajeError } from '@/lib/formato';
import { getRayfinClient } from '@/lib/rayfin-client';

export interface Movimiento {
  transaccionId: string;
  fechaHora: Date | null;
  importe: number | null;
  canal: string;
  pais: string;
  resultado: string;
  comercio: string;
  categoria: string;
  riesgoComercio: string;
}

export interface AlertaAnterior {
  alertaId: string;
  fechaHora: Date | null;
  tipoAlerta: string;
  resolucion: string;
}

interface Detalle {
  cargando: boolean;
  error: string | null;
  movimientos: Movimiento[];
  historial: AlertaAnterior[];
}

const VACIO: Detalle = { cargando: false, error: null, movimientos: [], historial: [] };

/**
 * Contexto de una alerta, leído del Lakehouse: los últimos movimientos de la
 * tarjeta y las alertas anteriores del mismo cliente que ya se cerraron.
 */
export function useDetalle(alerta: Alerta | null): Detalle {
  const [resultado, setResultado] = useState<(Omit<Detalle, 'cargando'> & { clave: string }) | null>(null);

  useEffect(() => {
    if (!alerta) return;
    let cancelado = false;
    (async () => {
      try {
        const client = await getRayfinClient();
        const [movs, previas] = await Promise.all([
          client.connectors.bretema.AppMovimientos.select([
            'transaccionId',
            'fechaHora',
            'importeEur',
            'canal',
            'pais',
            'resultado',
            'comercio',
            'categoriaComercio',
            'riesgoComercio',
          ])
            .where({ tarjetaId: { eq: alerta.tarjetaId } })
            .orderBy({ fechaHora: 'desc' })
            .first(12)
            .execute(),
          client.connectors.bretema.AppAlertas.select(['alertaId', 'fechaHora', 'tipoAlerta', 'resolucion'])
            .where({ clienteId: { eq: alerta.clienteId }, estado: { eq: 'Cerrada' } })
            .orderBy({ fechaHora: 'desc' })
            .first(20)
            .execute(),
        ]);
        if (cancelado) return;
        setResultado({
          clave: alerta.alertaId,
          error: null,
          movimientos: movs.map((m) => ({
            transaccionId: m.transaccionId,
            fechaHora: aFecha(m.fechaHora),
            importe: m.importeEur ?? null,
            canal: m.canal ?? '',
            pais: m.pais ?? '',
            resultado: m.resultado ?? '',
            comercio: m.comercio ?? '',
            categoria: m.categoriaComercio ?? '',
            riesgoComercio: m.riesgoComercio ?? '',
          })),
          historial: previas.map((p) => ({
            alertaId: p.alertaId,
            fechaHora: aFecha(p.fechaHora),
            tipoAlerta: p.tipoAlerta ?? '',
            resolucion: p.resolucion ?? '',
          })),
        });
      } catch (e) {
        if (!cancelado)
          setResultado({ clave: alerta.alertaId, error: mensajeError(e), movimientos: [], historial: [] });
      }
    })();
    return () => {
      cancelado = true;
    };
  }, [alerta]);

  if (!alerta) return VACIO;
  if (!resultado || resultado.clave !== alerta.alertaId) return { ...VACIO, cargando: true };
  return {
    cargando: false,
    error: resultado.error,
    movimientos: resultado.movimientos,
    historial: resultado.historial,
  };
}
