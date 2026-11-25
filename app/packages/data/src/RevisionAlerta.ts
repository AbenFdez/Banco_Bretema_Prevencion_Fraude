import { boolean, date, entity, role, set, text, uuid } from '@microsoft/rayfin-core';

/**
 * Decisión de una analista de fraude sobre una alerta del motor antifraude.
 *
 * Es el único dato que la consola escribe. Rayfin lo guarda en la SQL database
 * de la Fabric App, en la tabla `RevisionAlertas` (el nombre de la clase en
 * plural). Fabric replica esa base de datos en OneLake, y el notebook
 * `02_sincronizar_revisiones` la copia al Lakehouse para que la ontología la
 * enlace como entidad `Revision`.
 *
 * Permisos:
 * - Todo el equipo autenticado puede leer todas las revisiones (es un trabajo
 *   compartido y la cola tiene que saber qué alertas ya están decididas).
 * - Cada analista solo puede crear revisiones a su nombre: la política compara
 *   `analista_id` con el `sub` de su sesión, así que no se puede suplantar.
 * - No se permite editar ni borrar: las decisiones son un registro de auditoría.
 *   Para corregir una decisión se registra una revisión nueva.
 *
 * Las propiedades van en snake_case para que las columnas de la tabla coincidan
 * con las del Lakehouse. Todos los textos llevan `max` para que MSSQL no cree
 * columnas NVARCHAR(MAX).
 */
@entity()
@role('authenticated', 'read')
@role('authenticated', 'create', {
  policy: (claims, item) => claims.sub.eq(item.analista_id),
})
export class RevisionAlerta {
  @uuid() id!: string;
  @text({ min: 8, max: 20 }) alerta_id!: string;
  @set('Fraude confirmado', 'Falso positivo', 'Escalada al gestor')
  decision!: 'Fraude confirmado' | 'Falso positivo' | 'Escalada al gestor';
  @boolean({ default: false }) bloquear_tarjeta!: boolean;
  @text({ optional: true, max: 1000 }) comentario?: string;
  @text({ max: 200 }) analista_id!: string;
  @text({ max: 320 }) analista_email!: string;
  @date() revisada_en!: Date;
}
