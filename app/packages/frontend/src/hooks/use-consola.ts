import type { Decision } from '@rayfin-app/shared';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { useAuth } from '@/hooks/auth.context';
import { aBooleano, aFecha, mensajeError } from '@/lib/formato';
import { getRayfinClient } from '@/lib/rayfin-client';

/** Una alerta abierta del Lakehouse, ya normalizada para la interfaz. */
export interface Alerta {
  alertaId: string;
  fechaHora: Date | null;
  tipoAlerta: string;
  motivo: string;
  puntuacion: number;
  prioridad: 'Alta' | 'Media' | 'Baja';
  importe: number | null;
  canal: string;
  pais: string;
  comercio: string;
  categoriaComercio: string;
  municipioComercio: string;
  transaccionId: string;
  tarjetaId: string;
  tipoTarjeta: string;
  tarjetaEnmascarada: string;
  estadoTarjeta: string;
  clienteId: string;
  cliente: string;
  segmento: string;
  provinciaCliente: string;
  oficina: string;
  gestor: string;
  gastoMedio: number | null;
}

/** Una decisión registrada en la consola (tabla RevisionAlertas de la app). */
export interface Revision {
  id: string;
  alertaId: string;
  decision: Decision;
  bloquearTarjeta: boolean;
  comentario: string | null;
  analistaEmail: string;
  revisadaEn: Date | null;
}

export interface NuevaRevision {
  alertaId: string;
  decision: Decision;
  bloquearTarjeta: boolean;
  comentario: string;
}

type Estado = 'cargando' | 'listo' | 'error';

const CAMPOS_ALERTA = [
  'alertaId',
  'fechaHora',
  'tipoAlerta',
  'motivo',
  'puntuacionRiesgo',
  'prioridad',
  'importeEur',
  'canal',
  'pais',
  'comercio',
  'categoriaComercio',
  'municipioComercio',
  'transaccionId',
  'tarjetaId',
  'tipoTarjeta',
  'tarjetaEnmascarada',
  'estadoTarjeta',
  'clienteId',
  'cliente',
  'segmento',
  'provinciaCliente',
  'oficina',
  'gestor',
  'gastoMedioEur',
] as const;

const CAMPOS_REVISION = [
  'id',
  'alerta_id',
  'decision',
  'bloquear_tarjeta',
  'comentario',
  'analista_email',
  'revisada_en',
] as const;

function prioridadValida(valor: string | undefined): Alerta['prioridad'] {
  return valor === 'Alta' || valor === 'Media' ? valor : 'Baja';
}

/**
 * Estado de la consola: las alertas abiertas del Lakehouse (conector `bretema`)
 * y las decisiones guardadas en la app (`RevisionAlerta`). Una alerta está
 * pendiente si está abierta en el Lakehouse y nadie la ha decidido todavía en la
 * consola.
 */
export function useConsola() {
  const { session } = useAuth();
  const [estado, setEstado] = useState<Estado>('cargando');
  const [error, setError] = useState<string | null>(null);
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [revisiones, setRevisiones] = useState<Revision[]>([]);

  const aplicar = useCallback((datos: DatosConsola) => {
    setAlertas(datos.alertas);
    setRevisiones(datos.revisiones);
    setError(null);
    setEstado('listo');
  }, []);

  const fallar = useCallback((e: unknown) => {
    setError(mensajeError(e));
    setEstado('error');
  }, []);

  // Carga inicial: el estado solo cambia cuando llega la respuesta
  useEffect(() => {
    let cancelada = false;
    leerConsola()
      .then((datos) => {
        if (!cancelada) aplicar(datos);
      })
      .catch((e: unknown) => {
        if (!cancelada) fallar(e);
      });
    return () => {
      cancelada = true;
    };
  }, [aplicar, fallar]);

  const recargar = useCallback(async () => {
    setEstado('cargando');
    try {
      aplicar(await leerConsola());
    } catch (e) {
      fallar(e);
    }
  }, [aplicar, fallar]);

  const decididas = useMemo(() => new Set(revisiones.map((r) => r.alertaId)), [revisiones]);
  const pendientes = useMemo(() => alertas.filter((a) => !decididas.has(a.alertaId)), [alertas, decididas]);
  const alertasPorId = useMemo(() => new Map(alertas.map((a) => [a.alertaId, a])), [alertas]);

  const registrar = useCallback(
    async (nueva: NuevaRevision): Promise<Revision> => {
      const usuario = session?.user;
      if (!usuario) throw new Error('La sesión ha caducado. Vuelve a iniciar sesión.');
      const client = await getRayfinClient();
      const creada = await client.data.RevisionAlerta.create({
        alerta_id: nueva.alertaId,
        decision: nueva.decision,
        bloquear_tarjeta: nueva.bloquearTarjeta,
        comentario: nueva.comentario.trim() === '' ? null : nueva.comentario.trim(),
        analista_id: usuario.id,
        analista_email: usuario.email,
        revisada_en: new Date(),
      });
      const revision = aRevision(creada);
      setRevisiones((previas) => [revision, ...previas]);
      return revision;
    },
    [session]
  );

  return { estado, error, alertas, pendientes, revisiones, alertasPorId, registrar, recargar };
}

interface DatosConsola {
  alertas: Alerta[];
  revisiones: Revision[];
}

/** Lee del Lakehouse las alertas abiertas y de la app las revisiones. No toca el estado de React. */
async function leerConsola(): Promise<DatosConsola> {
  const client = await getRayfinClient();
  const [filasAlertas, filasRevisiones] = await Promise.all([
    client.connectors.bretema.AppAlertas.select([...CAMPOS_ALERTA])
      .where({ estado: { eq: 'Abierta' } })
      .orderBy({ puntuacionRiesgo: 'desc' })
      .first(1000)
      .execute(),
    client.data.RevisionAlerta.select([...CAMPOS_REVISION])
      .orderBy({ revisada_en: 'desc' })
      .first(1000)
      .execute(),
  ]);
  const alertas: Alerta[] = filasAlertas.map((f) => ({
    alertaId: f.alertaId,
    fechaHora: aFecha(f.fechaHora),
    tipoAlerta: f.tipoAlerta ?? '',
    motivo: f.motivo ?? '',
    puntuacion: Number(f.puntuacionRiesgo ?? 0),
    prioridad: prioridadValida(f.prioridad),
    importe: f.importeEur ?? null,
    canal: f.canal ?? '',
    pais: f.pais ?? '',
    comercio: f.comercio ?? '',
    categoriaComercio: f.categoriaComercio ?? '',
    municipioComercio: f.municipioComercio ?? '',
    transaccionId: f.transaccionId ?? '',
    tarjetaId: f.tarjetaId,
    tipoTarjeta: f.tipoTarjeta ?? '',
    tarjetaEnmascarada: f.tarjetaEnmascarada ?? '',
    estadoTarjeta: f.estadoTarjeta ?? '',
    clienteId: f.clienteId ?? '',
    cliente: f.cliente ?? '',
    segmento: f.segmento ?? '',
    provinciaCliente: f.provinciaCliente ?? '',
    oficina: f.oficina ?? '',
    gestor: f.gestor ?? '',
    gastoMedio: f.gastoMedioEur ?? null,
  }));
  return { alertas, revisiones: filasRevisiones.map(aRevision) };
}

function aRevision(f: {
  id: string;
  alerta_id: string;
  decision: Decision;
  bloquear_tarjeta: boolean | 'true' | 'false';
  comentario?: string | null;
  analista_email: string;
  revisada_en: Date | string;
}): Revision {
  return {
    id: f.id,
    alertaId: f.alerta_id,
    decision: f.decision,
    bloquearTarjeta: aBooleano(f.bloquear_tarjeta),
    comentario: f.comentario ?? null,
    analistaEmail: f.analista_email,
    revisadaEn: aFecha(f.revisada_en),
  };
}
