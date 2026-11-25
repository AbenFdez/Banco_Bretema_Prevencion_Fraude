/**
 * Contratos que comparten el paquete de datos y el frontend.
 *
 * Mantén cada registro alineado con su entidad decorada en `@rayfin-app/data`.
 * Este paquete tiene que poder ejecutarse en el navegador: no importes aquí las
 * clases decoradas.
 */

export const DECISIONES = ['Fraude confirmado', 'Falso positivo', 'Escalada al gestor'] as const;
export type Decision = (typeof DECISIONES)[number];

export interface RevisionAlertaRecord {
  id: string;
  alerta_id: string;
  decision: Decision;
  bloquear_tarjeta: boolean;
  comentario?: string | null;
  analista_id: string;
  analista_email: string;
  revisada_en: Date;
}

export type UniversalAppSchema = {
  RevisionAlerta: RevisionAlertaRecord;
};
