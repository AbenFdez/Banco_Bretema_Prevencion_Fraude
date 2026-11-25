# Bitácora de la demo

Diario de cómo vamos construyendo la demo: qué se ha hecho, qué se ha decidido y por qué, qué se ha probado y qué falta. La entrada más reciente va arriba.

Para cada sesión nueva, copia la plantilla del final.

---

## 25 de noviembre de 2026 · Datos para Eventhouse y simulador en tiempo real

**Cambio de enfoque.** La demo se construye paso a paso en directo a partir de datos en CSV. El centro pasa a ser un **Eventhouse** con transacciones en tiempo real que se analizan con **KQL**.

**Hecho**
- CSV reorganizados según el patrón del tutorial de ontologías de Microsoft: seis tablas estáticas para el Lakehouse y el histórico de transacciones y alertas para el Eventhouse.
- Coordenadas en `oficinas` y `comercios` para pintar mapas.
- La tarjeta se guarda como texto enmascarado (`**** 0120`) en lugar de `ultimos_digitos`, para que ningún asistente de carga la convierta en número y pierda los ceros. Se han actualizado el notebook 01 y la Fabric App.
- **Simulador en tiempo real** (`simulador/simulador_transacciones.py`). Envía operaciones a un Eventstream por el protocolo de Event Hubs, con cuatro escenarios: ráfaga de fraude en tarjetas que pasaron por Ponte Alta, compra en Portugal, importe inusual y tarjeta bloqueada. Cómo está hecho: [simulador/README.md](../simulador/README.md).
- Notebook `03_simulador_tiempo_real` para lanzarlo desde Fabric.
- Scripts KQL: tablas y mapeo JSON (01), funciones de detección (02), consultas de la demo (03), Real-Time Dashboard (04) y política de actualización opcional (05).
- Guía paso a paso en 8 fases: [docs/paso-a-paso](paso-a-paso/README.md).

**Decisiones**
- *Las alertas en tiempo real se calculan al consultar, con funciones KQL, y no con una política de actualización.* El Eventhouse tiene activada por defecto la ingesta en streaming, y una política de actualización que cruza tablas obliga a desactivarla: la latencia pasaría de 1 o 2 segundos a unos 10. La política queda como opción en `kql/05_opcional_politica_actualizacion.kql`.
- *Transaccion y Alerta se enlazan en la ontología al Eventhouse.* Así la ontología ve también el tiempo real. Contrapartida: no entran en el grafo, que solo admite tablas Delta de Lakehouse o de bases de datos reflejadas. Si se necesita el grafo con transacciones, se cargan también en el Lakehouse con el notebook 01.
- *El simulador se ejecuta en el ordenador*, no en Fabric, para no consumir la F2 con una sesión de notebook abierta. Por defecto envía 2 operaciones por segundo.
- *Las ráfagas del simulador usan tarjetas activas que pasaron por Ponte Alta en octubre*, para que el directo continúe la historia del histórico y la consulta del punto de compromiso tenga sentido.

**Probado**
- Las cifras de la historia salen igual tras añadir coordenadas: los CSV de clientes, cuentas, gestores, transacciones y alertas son idénticos a los anteriores.
- Notebook 01 con PySpark en local: 8 tablas, 2 tablas de la app y las 5 comprobaciones en `OK`.
- Simulador: un minuto con los valores por defecto da 133 operaciones y los 4 escenarios; todas las tarjetas y comercios existen en los CSV y los identificadores no se repiten.
- Cliente de Event Hubs creado con una cadena de conexión de prueba.
- Fabric App: tipos, lint y 53 tests en verde tras renombrar la columna de la tarjeta.

**Pendiente**
- [ ] Probar el envío real al Eventstream con la cadena de conexión de `ES_Transacciones` (fase 3) y anotar la latencia.
- [ ] Ejecutar los scripts KQL en `EH_Bretema` y confirmar las cifras del bloque C. Los scripts no se han podido ejecutar en un Eventhouse real todavía.
- [ ] Importar `banco_bretema.ttl` y anotar el resumen de la importación.
- [ ] Conectar GitHub a Claude para subir el repositorio y actualizarlo sobre la marcha.

---

## 25 de noviembre de 2026 · Primera versión

**Hecho**
- Banco ficticio **Banco Brétema**, con sede histórica en Santiago de Compostela, y caso de uso de **prevención del fraude con tarjetas**. Logo propio en `assets/`.
- Datos sintéticos con semilla fija y tres historias: el punto de compromiso en la Gasolineira Ponte Alta (Vigo), los falsos positivos por compras en Portugal y el fraude que la regla no vio. Cómo se generaron: [modelo-datos.md](modelo-datos.md#cómo-se-generaron-los-datos).
- Ontología en Turtle con 9 entidades y 12 relaciones, reglas de negocio e instrucciones para el agente de datos.
- Fabric App «Consola de alertas» con la CLI de Rayfin: lee el Lakehouse con un conector y guarda las decisiones en su SQL database.

**Decisiones**
- Experiencia **nueva** de Ontology. La antigua se retira el 31 de enero de 2027.
- Importes como `DOUBLE`, porque el grafo no admite `DECIMAL`.
- Las decisiones de la app vuelven al Lakehouse con un notebook, porque el grafo solo admite tablas Delta de Lakehouse o de bases de datos reflejadas.

---

## Plantilla

```markdown
## AAAA-MM-DD · Título de la sesión

**Hecho**
-

**Decisiones**
- *Qué se decidió.* Por qué.

**Probado**
-

**Problemas y soluciones**
-

**Cifras reales** (latencias, tiempos de carga, consumo de la F2)
-

**Capturas** (guárdalas en `assets/capturas/`)
-

**Pendiente**
- [ ]
```
