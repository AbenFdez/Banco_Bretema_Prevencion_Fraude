import { entity, date, decimal, text, role } from '@microsoft/rayfin-core';
import { Source } from '@microsoft/rayfin-connectors';

/**
 * Tabla `dbo.app_movimientos` del Lakehouse Bretema_LH: las transacciones con
 * tarjeta y los datos del comercio, para enseñar los últimos movimientos.
 *
 * Generada a mano a partir del esquema que crea notebooks/01_cargar_lakehouse.ipynb,
 * siguiendo el contrato de generación de @microsoft/rayfin-connector-fabric-graphql.
 * El Lakehouse no publica claves primarias, así que `transaccionId` se declara como
 * clave lógica (la columna es NOT NULL y única). Solo lectura.
 */
@role('authenticated', ['read'])
@entity()
export class AppMovimientos extends Source({ schema: 'dbo', table: 'app_movimientos', primaryKey: ['transaccionId'] }) {
  @text({ column: 'transaccion_id', max: 8000 }) transaccionId!: string;
  @text({ column: 'tarjeta_id', max: 8000 }) tarjetaId!: string;
  @date({ optional: true, column: 'fecha_hora' }) fechaHora?: Date;
  @decimal({ optional: true, column: 'importe_eur' }) importeEur?: number;
  @text({ optional: true, max: 8000 }) canal?: string;
  @text({ optional: true, max: 8000 }) pais?: string;
  @text({ optional: true, max: 8000 }) resultado?: string;
  @text({ optional: true, max: 8000 }) comercio?: string;
  @text({ optional: true, column: 'categoria_comercio', max: 8000 }) categoriaComercio?: string;
  @text({ optional: true, column: 'municipio_comercio', max: 8000 }) municipioComercio?: string;
  @text({ optional: true, column: 'riesgo_comercio', max: 8000 }) riesgoComercio?: string;
}
