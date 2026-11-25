# Fase 1 · Datos estáticos en el Lakehouse

Los datos que cambian poco (oficinas, gestores, clientes, cuentas, tarjetas y comercios) van al Lakehouse como tablas Delta. Es lo que usarán la ontología, el grafo y la Fabric App.

## Pasos

1. En el área de trabajo, **Nuevo elemento › Lakehouse**, con el nombre `LH_Bretema`. Deja los esquemas activados: las tablas se crearán en `dbo`.
2. En el Lakehouse, sobre **Files**, **… › Nueva subcarpeta** → `datos`.
3. Sobre `datos`, **… › Cargar › Cargar archivos** y sube estos seis CSV de la carpeta `datos/` del repositorio:
   `oficinas.csv`, `gestores.csv`, `clientes.csv`, `cuentas.csv`, `tarjetas.csv` y `comercios.csv`.
4. Para cada CSV: **… › Cargar en tablas › Nueva tabla**. Deja el nombre propuesto (el del archivo), marca **Usar encabezado para los nombres de columna** y el separador **coma**. Pulsa **Cargar**.
5. Al terminar, en **Tables › dbo** tienen que aparecer las seis tablas.

### Alternativa con notebook

Si prefieres no cargar los CSV a mano, importa `notebooks/01_cargar_lakehouse.ipynb` y ejecútalo con `LH_Bretema` como Lakehouse predeterminado. Descarga los ocho CSV desde GitHub, fija los tipos de cada columna y crea además las tablas de transacciones y alertas y las dos tablas que usa la Fabric App. En una F2 tarda unos minutos.

## Comprobación

En el Lakehouse, cambia a **Punto de conexión de análisis SQL** y ejecuta:

```sql
SELECT 'oficinas' AS tabla, COUNT(*) AS filas FROM dbo.oficinas UNION ALL
SELECT 'gestores', COUNT(*) FROM dbo.gestores UNION ALL
SELECT 'clientes', COUNT(*) FROM dbo.clientes UNION ALL
SELECT 'cuentas', COUNT(*) FROM dbo.cuentas UNION ALL
SELECT 'tarjetas', COUNT(*) FROM dbo.tarjetas UNION ALL
SELECT 'comercios', COUNT(*) FROM dbo.comercios;
```

| Tabla | Filas |
| --- | ---: |
| oficinas | 24 |
| gestores | 48 |
| clientes | 2.400 |
| cuentas | 3.194 |
| tarjetas | 3.236 |
| comercios | 294 |

Comprueba también los tipos: `tarjeta_enmascarada` debe ser texto (`**** 0120`), `latitud` y `longitud` números decimales, y `fecha_alta` una fecha.

## Qué apuntar en la bitácora

- Si **Cargar en tablas** infirió algún tipo distinto del esperado.
- Una captura de las seis tablas en el explorador, para la presentación.

Siguiente: [Fase 2 · Histórico en el Eventhouse](02-eventhouse.md)
