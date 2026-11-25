import { entity, date, decimal, int, text, role } from '@microsoft/rayfin-core';
import { Source } from '@microsoft/rayfin-connectors';

/**
 * Tabla `dbo.app_alertas` del Lakehouse LH_Bretema: una fila por alerta del motor
 * antifraude, ya cruzada con la transacción, el comercio, la tarjeta, el cliente,
 * su oficina y su gestor.
 *
 * Generada a mano a partir del esquema que crea notebooks/01_cargar_lakehouse.ipynb,
 * siguiendo el contrato de generación de @microsoft/rayfin-connector-fabric-graphql.
 * El Lakehouse no publica claves primarias, así que `alertaId` se declara como
 * clave lógica (la columna es NOT NULL y única). Solo lectura.
 */
@role('authenticated', ['read'])
@entity()
export class AppAlertas extends Source({ schema: 'dbo', table: 'app_alertas', primaryKey: ['alertaId'] }) {
  @text({ column: 'alerta_id', max: 8000 }) alertaId!: string;
  @date({ optional: true, column: 'fecha_hora' }) fechaHora?: Date;
  @text({ optional: true, column: 'tipo_alerta', max: 8000 }) tipoAlerta?: string;
  @text({ optional: true, max: 8000 }) motivo?: string;
  @int({ optional: true, column: 'puntuacion_riesgo' }) puntuacionRiesgo?: number;
  @text({ optional: true, max: 8000 }) prioridad?: string;
  @text({ optional: true, max: 8000 }) estado?: string;
  @text({ optional: true, max: 8000 }) resolucion?: string;
  @date({ optional: true, column: 'fecha_resolucion' }) fechaResolucion?: Date;
  @text({ optional: true, column: 'transaccion_id', max: 8000 }) transaccionId?: string;
  @decimal({ optional: true, column: 'importe_eur' }) importeEur?: number;
  @text({ optional: true, max: 8000 }) canal?: string;
  @text({ optional: true, max: 8000 }) pais?: string;
  @text({ optional: true, max: 8000 }) comercio?: string;
  @text({ optional: true, column: 'categoria_comercio', max: 8000 }) categoriaComercio?: string;
  @text({ optional: true, column: 'municipio_comercio', max: 8000 }) municipioComercio?: string;
  @text({ column: 'tarjeta_id', max: 8000 }) tarjetaId!: string;
  @text({ optional: true, column: 'tipo_tarjeta', max: 8000 }) tipoTarjeta?: string;
  @text({ optional: true, column: 'ultimos_digitos', max: 8000 }) ultimosDigitos?: string;
  @text({ optional: true, column: 'estado_tarjeta', max: 8000 }) estadoTarjeta?: string;
  @text({ optional: true, column: 'cliente_id', max: 8000 }) clienteId?: string;
  @text({ optional: true, max: 8000 }) cliente?: string;
  @text({ optional: true, max: 8000 }) segmento?: string;
  @text({ optional: true, column: 'provincia_cliente', max: 8000 }) provinciaCliente?: string;
  @text({ optional: true, max: 8000 }) oficina?: string;
  @text({ optional: true, max: 8000 }) gestor?: string;
  @decimal({ optional: true, column: 'gasto_medio_eur' }) gastoMedioEur?: number;
}
