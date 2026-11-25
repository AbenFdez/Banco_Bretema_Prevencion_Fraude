# Fase 5 · Alertas automáticas con Activator

Que alguien mire el panel no basta: cuando aparece una ráfaga, el equipo de fraude tiene que enterarse solo. **Activator** ejecuta una consulta KQL cada pocos minutos y avisa cuando se cumple una condición.

## Pasos

1. En el conjunto de consultas `KQL_Fraude`, escribe y ejecuta:

   ```kql
   fn_rafagas(10m)
   | project inicio, cliente, oficina, tarjeta_enmascarada, operaciones, importe_total
   ```

2. Con la consulta seleccionada, pulsa **Establecer alerta** (Set alert) en la barra superior.
3. Configura la alerta:
   - **Ejecutar consulta cada**: 5 minutos.
   - **Condición**: cuando haya resultados (número de filas mayor que 0).
   - **Acción**: correo electrónico o mensaje de Teams para ti, con el texto «Ráfaga de fraude detectada en Banco Brétema».
   - **Guardar en**: un Activator nuevo, `ACT_Rafagas`, en el área de trabajo de la demo.
4. **Crear**. El Activator queda en marcha.

También puedes crear la alerta desde el mosaico de ráfagas del Real-Time Dashboard (**… › Establecer alerta**).

## Comprobación

Con el simulador en marcha, en un máximo de 5 minutos después de la primera ráfaga tiene que llegarte el aviso.

> En una F2, detén el Activator al terminar (**Detener** en el elemento): cada ejecución de la consulta consume capacidad.

## Qué apuntar en la bitácora

- Cuánto tardó en llegar el primer aviso.
- El texto del aviso, por si quieres cambiarlo para la demo.

Siguiente: [Fase 6 · Ontología y agente](06-ontologia.md)
