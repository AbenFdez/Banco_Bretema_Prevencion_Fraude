/** Utilidades de formato en español de España. */

const EUROS = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' });
const FECHA_HORA = new Intl.DateTimeFormat('es-ES', {
  day: '2-digit',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
  timeZone: 'UTC',
});
const FECHA = new Intl.DateTimeFormat('es-ES', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC' });
const HORA_LOCAL = new Intl.DateTimeFormat('es-ES', { hour: '2-digit', minute: '2-digit' });

/**
 * Las fechas del Lakehouse son horas de reloj sin zona (se guardan en UTC tal
 * cual vienen en los CSV), así que se muestran en UTC para no desplazarlas.
 * Las fechas que crea la app (revisada_en) son instantes reales y se muestran
 * en la hora local del navegador.
 */
export function aFecha(valor: Date | string | null | undefined): Date | null {
  if (valor === null || valor === undefined || valor === '') return null;
  const fecha = valor instanceof Date ? valor : new Date(valor);
  return Number.isNaN(fecha.getTime()) ? null : fecha;
}

export function euros(valor: number | null | undefined): string {
  return valor === null || valor === undefined ? '—' : EUROS.format(valor);
}

export function fechaHora(valor: Date | string | null | undefined): string {
  const fecha = aFecha(valor);
  return fecha ? FECHA_HORA.format(fecha) : '—';
}

export function fecha(valor: Date | string | null | undefined): string {
  const f = aFecha(valor);
  return f ? FECHA.format(f) : '—';
}

export function horaLocal(valor: Date | string | null | undefined): string {
  const f = aFecha(valor);
  return f ? HORA_LOCAL.format(f) : '—';
}

export function esHoy(valor: Date | string | null | undefined): boolean {
  const f = aFecha(valor);
  if (!f) return false;
  const hoy = new Date();
  return f.getFullYear() === hoy.getFullYear() && f.getMonth() === hoy.getMonth() && f.getDate() === hoy.getDate();
}

export function plural(n: number, singular: string, varios: string): string {
  return `${n} ${n === 1 ? singular : varios}`;
}

export function aBooleano(valor: boolean | 'true' | 'false' | null | undefined): boolean {
  return valor === true || valor === 'true';
}

/** Mensaje de error apto para enseñar en pantalla. */
export function mensajeError(error: unknown): string {
  if (error instanceof Error && error.message) return error.message;
  return 'Se ha producido un error inesperado.';
}
