# Bitácora de la demo

Diario de cómo vamos construyendo la demo: qué se ha hecho, qué se ha decidido y por qué, qué se ha probado y qué falta. La entrada más reciente va arriba.

Para cada sesión nueva, copia la plantilla del final.

---

## 26 de noviembre de 2026 · Fase 0: capacidad F2 y área de trabajo

**Hecho**
- Localizada la suscripción de Azure de las demos y su capacidad de Fabric: **F2**, región **Spain Central**, estado activo.
- Comprobado en **Portal de administración › Capacity settings › Fabric Capacity** que la capacidad aparece y que la cuenta es administradora del inquilino (se ve **Tenant settings**).
- Creada el área de trabajo **`Bretema`** sobre la F2, con el logo del banco. La guía y los comandos usan ya ese nombre.
- Fase 1 en marcha: creado el Lakehouse **`Bretema_LH`**, con esquemas, subidos los ocho CSV a `Files/` e importado el notebook `01_cargar_lakehouse`. La guía y el resto del repositorio usan ya ese nombre (antes `LH_Bretema`).

**Notebooks**
- Nuevo `notebooks/01_crear_tablas_sql.ipynb`: crea las mismas tablas que `01_cargar_lakehouse`, pero con `CREATE TABLE` e `INSERT … SELECT` en Spark SQL, una sentencia por celda. Lee los CSV de `Files/`.

**Probado**
- `01_crear_tablas_sql` en local con Spark 3.5: las 32 sentencias se ejecutan y las 13 comprobaciones salen en `OK`. En local las tablas se guardaron en Parquet, porque no hay Delta instalado; falta ejecutarlo en Fabric.

**Capturas**
- `assets/capturas/00-area-de-trabajo-fabric.png`: el área de trabajo recién creada, vacía y con el rombo de capacidad. Está en la [fase 0](paso-a-paso/00-preparacion.md) y en la diapositiva 19 de la presentación.
- `assets/capturas/10-lakehouse-csv-subidos.png`: el Lakehouse con los ocho CSV subidos. En la [fase 1](paso-a-paso/01-lakehouse.md); todavía no está en la presentación.
- `assets/capturas/11-lakehouse-y-punto-sql.png`: la lista del área de trabajo con el notebook importado, el Lakehouse y el punto de conexión SQL que Fabric crea con él (recorte). En la [fase 1](paso-a-paso/01-lakehouse.md); todavía no está en la presentación.
- `assets/capturas/00-capacidad-f2-azure.png`: la capacidad F2 en el portal de Azure, activa y en Spain Central. Está recortada y con el identificador de la suscripción tapado. En la [fase 0](paso-a-paso/00-preparacion.md); todavía no está en la presentación.

**Presentación**
- Diapositiva nueva, la 19: «Fase 0: el área de trabajo sobre la F2». La presentación pasa a 36 diapositivas y las siguientes se desplazan un puesto.

**Lo que aprendimos**
- *Dos cuentas, dos papeles.* La suscripción de Azure cuelga de una cuenta personal, pero Fabric no admite cuentas personales: se entra con una cuenta profesional del directorio de esa suscripción. Conviene tener apuntadas las dos (fuera del repositorio, que es público).
- *La opción «Fabric» salía en gris al crear el área de trabajo*, aunque la capacidad estaba activa en Azure y los permisos ya eran correctos en el portal de administración. **Se resolvió recargando la página de Fabric**: el panel se había abierto antes de que Fabric reconociera la capacidad. Qué comprobar si recargar no basta: [fase 0](paso-a-paso/00-preparacion.md#si-la-opción-fabric-sale-en-gris).
- *Los ajustes del inquilino pueden tardar hasta una hora*, no unos minutos como decía la guía. Corregido.

**Decisiones**
- *Haremos las dos variantes de la ontología*, cada una en su elemento: `BancoBretemaFraude`, con todo enlazado al Lakehouse, y `BancoBretemaFraude_RT`, con Transaccion y Alerta enlazadas al Eventhouse. Así la demo enseña el compromiso entre recorridos por el grafo y tiempo real, y queda resuelta la duda de dónde enlazar las transacciones. Detalle en la [fase 6](paso-a-paso/06-ontologia.md#dos-variantes-dos-ontologías).
- Orden de montaje: primero el Eventhouse (fase 2) y después el Lakehouse con el notebook 01, que hace falta para la variante A.

**Estado de los ajustes del inquilino**
- «Users can create Fabric items»: activado.
- «Users can create Ontology (preview) items»: desactivado al empezar la sesión.

**Pendiente**
- [ ] Activar los ajustes de ontología, agente de datos, Copilot / Azure OpenAI y Fabric Apps, y anotar si algún nombre es distinto al de la guía.
- [ ] Fase 1: ejecutar en Fabric uno de los dos notebooks 01 (el de SQL, o el de PySpark con `ORIGEN = "files"` y `CARPETA = "Files"`), y anotar el tiempo y el resultado de las comprobaciones. Los dos se han probado solo en local.
- [ ] Actualizar la presentación: todavía dice `LH_Bretema` y le faltan las capturas de la capacidad y del Lakehouse.
- [ ] Pausar la capacidad al terminar cada sesión.

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

**Capturas**
- `assets/capturas/00-github-push-vscode.png`: la subida a GitHub desde la terminal de VS Code. Documentada en [publicar-en-github.md](publicar-en-github.md) y reservada para la presentación.

**Presentación**
- Primera versión: [`Fraude_en_tiempo_real_Banco_Bretema_NTT_DATA.pptx`](presentacion/Fraude_en_tiempo_real_Banco_Bretema_NTT_DATA.pptx), 35 diapositivas (36 desde el 26 de noviembre; los números de abajo son los actuales) con el branding de NTT DATA, hecha sobre la plantilla de la charla «De la capa gold a la capa ontológica». Estructura y lista de capturas: [presentacion/README.md](presentacion/README.md).
- Incluye la captura de la subida a GitHub (recortada, diapositiva 31) y la vista previa local de la consola (diapositiva 29).
- Cinco diapositivas tienen un hueco marcado como **CAPTURA PENDIENTE**: Eventstream (17), panel (23), Activator (24), importación del Turtle (26) y respuesta del agente (28).
- Las cifras de la presentación son las de `scripts/comprobar_historia.py`. Las notas del orador marcan lo que aún no se ha confirmado en Fabric.

**Cómo actualizamos el repositorio**
- La copia de trabajo está en OneDrive: `Eventos/Formacion_NTT_Ontologias/Banco_Bretema_Prevencion_Fraude`.
- Cada cambio llega como un archivo `.patch`, que se aplica desde esa carpeta con `git am ruta/al/archivo.patch` y se sube con `git push`. Así cada cambio entra como un commit con su descripción.
- Antes de cada `git push`, esperar a que OneDrive termine de sincronizar.

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
- [x] Decidir dónde se enlazan Transaccion y Alerta para la demo del agente: se hacen las dos variantes (decisión del 26 de noviembre).
- [ ] Hacer las capturas pendientes de la presentación y sustituir los huecos (lista en [presentacion/README.md](presentacion/README.md)).
- [x] Repositorio subido a GitHub desde la terminal de VS Code (`git push -u origin main`).

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
