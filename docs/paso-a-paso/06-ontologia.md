# Fase 6 · Ontología y agente de datos

La ontología da nombre de negocio a lo que hay en el Lakehouse y en el Eventhouse. Se sigue el mismo patrón que el tutorial de Microsoft: **las entidades estáticas se enlazan al Lakehouse y las que llegan en tiempo real, al Eventhouse**.

| Entidad | Origen | Tabla | Clave |
| --- | --- | --- | --- |
| Oficina | Lakehouse `LH_Bretema` | `oficinas` | `oficina_id` |
| Gestor | Lakehouse | `gestores` | `gestor_id` |
| Cliente | Lakehouse | `clientes` | `cliente_id` |
| Cuenta | Lakehouse | `cuentas` | `cuenta_id` |
| Tarjeta | Lakehouse | `tarjetas` | `tarjeta_id` |
| Comercio | Lakehouse | `comercios` | `comercio_id` |
| Transaccion | **Eventhouse `EH_Bretema`** | `transacciones` (histórico y tiempo real) | `transaccion_id` |
| Alerta | **Eventhouse** | `alertas` | `alerta_id` |
| Revision | Lakehouse | `revisiones` (solo si haces la fase 7) | `revision_id` |

## Pasos

Los pasos detallados, con las relaciones, las reglas y las instrucciones del agente, están en [ontologia/README.md](../../ontologia/README.md). En resumen:

1. **Nuevo elemento › Ontology (preview)**, con el nombre `BancoBretemaFraude`.
2. **Import ontology** con `ontologia/banco_bretema.ttl`: crea 9 entidades y 12 relaciones con descripciones y sinónimos.
3. Enlaza cada entidad con su tabla según la tabla de arriba (**Bind data › OneLake catalog**). Para Transaccion y Alerta, abre el Eventhouse `EH_Bretema` en lugar del Lakehouse. Si el asistente pide una columna de marca de tiempo, elige `fecha_hora`.
4. Elige la clave de cada entidad y configura las 12 relaciones.
5. Añade las cuatro reglas de negocio.
6. **Grafo**: materialízalo con las entidades del Lakehouse. Las del Eventhouse no entran en el grafo, que solo admite tablas Delta de Lakehouse o bases de datos reflejadas.
7. **Agente de datos** `AG_Bretema` con la ontología como fuente y las instrucciones del README de la ontología.

### Si quieres el histórico dentro del grafo

Ejecuta el notebook `01_cargar_lakehouse` (crea también `transacciones` y `alertas` en el Lakehouse) y enlaza Transaccion y Alerta a esas tablas en lugar de al Eventhouse. Ganas recorridos por el grafo, pero pierdes el tiempo real en la ontología.

## Preguntas para probar el agente

| Pregunta | Respuesta esperada |
| --- | --- |
| ¿Cuántas alertas abiertas hay y qué oficinas tienen más? | 53; Vigo Centro 12, Vigo Bouzas 5, Ourense Centro 4 |
| De las tarjetas con fraude confirmado desde el 15 de octubre, ¿en qué comercio coincidieron más en los 60 días anteriores? | Gasolineira Ponte Alta, 23 de 27 |
| ¿Cuántas operaciones ha hecho en la última hora la tarjeta de la última ráfaga y en qué comercios? | La anunciada por el simulador (requiere Transaccion enlazada al Eventhouse) |

Más preguntas y respuestas en el [guion de la demo](../guion-demo.md).

## Qué apuntar en la bitácora

- El resumen de la importación del Turtle: cuántos elementos quedaron como *Preserved*, *Fixed automatically* o *Not supported*.
- Si el enlace con el Eventhouse pidió columna de tiempo y cómo se comportó.
- Las respuestas reales del agente a cada pregunta.

Siguiente: [Fase 7 · Fabric App](07-fabric-app.md)
