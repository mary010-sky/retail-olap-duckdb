---
title: "Construí una solución OLAP con DuckDB en el navegador y despliegue automático"
published: false
description: "Un laboratorio reproducible con 100.000 ventas, esquema estrella y SQL analítico, sin configurar servicios AWS."
tags: duckdb, sql, analytics, webdev
---

**Autora: Marymar Danytza Calloticona Chambilla**

¿Cómo pasar de miles de registros a preguntas útiles, como qué mercado vende más o cómo cambian los ingresos mes a mes? En este proyecto construí Retail OLAP Lab: una aplicación que ejecuta consultas analíticas con DuckDB-Wasm dentro del navegador y que se puede publicar automáticamente mediante GitHub Actions y GitHub Pages.

La solución utiliza 100.000 ventas **sintéticas**, reproducibles y sin información personal. No configura ni requiere una cuenta o servicio AWS. El proveedor de alojamiento sirve los archivos públicos; el motor de consultas funciona en el dispositivo del visitante.

## 1. Qué aporta OLAP

Online Analytical Processing se orienta a explorar medidas desde diferentes dimensiones. Aquí la medida principal es el ingreso, calculado como cantidad por precio unitario. Las dimensiones permiten observarlo por fecha, mercado y categoría.

Una operación transaccional registraría una venta. Este laboratorio responde preguntas agregadas sobre muchas ventas: ingresos por mes, subtotales por mercado, comparación entre categorías y ranking de desempeño.

DuckDB dispone de una [distribución WebAssembly para aplicaciones web](https://github.com/duckdb/duckdb-wasm). Su ejecución en un Web Worker permite separar el motor de consultas del hilo que atiende la interfaz. Eso hace posible este pequeño laboratorio sin mantener un servidor de base de datos.

## 2. Arquitectura

```text
Repositorio público
       │ push a main
       ▼
GitHub Actions: validación → empaquetado → despliegue
       ▼
GitHub Pages: HTML + CSS + JavaScript + model.sql
       ▼
Navegador → DuckDB-Wasm (Web Worker)
                 │
                 ▼
      Esquema estrella en memoria
                 │
                 ▼
      SQL → indicadores, gráficos y CSV
```

El motor se descarga desde jsDelivr con una versión explícita del paquete. La primera carga necesita conexión a ese CDN. Cada navegador crea su propia base en memoria; no hay una base compartida entre visitantes.

## 3. Un esquema estrella pequeño y verificable

La tabla `fact_sales` tiene un registro por línea de venta. Contiene el identificador, la fecha, las claves de región y producto, la cantidad y el precio unitario.

Las dimensiones son:

| Tabla | Contenido |
| --- | --- |
| `dim_date` | 731 fechas, de enero de 2024 a diciembre de 2025 |
| `dim_region` | Perú, Chile, Colombia, México y Argentina |
| `dim_product` | Electronics, Home, Sports y Books |

La vista `sales` une las tablas y calcula `revenue` con un tipo decimal. Todos los importes se expresan en USD como unidad común del ejemplo: no se realiza conversión de monedas.

El generador SQL usa operaciones aritméticas sobre `generate_series(1,100000)`. Así produce los mismos datos al recargar. Esto facilita comparar resultados, aunque crea patrones artificiales que impiden interpretar los datos como evidencia de un mercado real.

```sql
CREATE VIEW sales AS
SELECT f.*, r.region, p.category, d.year, d.quarter, d.month,
       CAST(f.quantity * f.unit_price AS DECIMAL(14,2)) AS revenue
FROM fact_sales f
JOIN dim_region r USING(region_id)
JOIN dim_product p USING(product_id)
JOIN dim_date d USING(sale_date);
```

El año 2024 es bisiesto. Por eso el calendario de los dos años tiene 731 días y el generador utiliza módulo 731 para distribuir las fechas sin excluir el 29 de febrero.

## 4. Operaciones OLAP visibles en la aplicación

**Slice y dice.** Los selectores restringen el conjunto por mercado y año; por ejemplo, Perú en 2025. Los indicadores y las consultas respetan esa selección.

**Drill-down.** Partir del total del período y observar sus meses permite aumentar el detalle temporal:

```sql
SELECT year, month, round(sum(revenue), 2) AS revenue
FROM sales
WHERE region = 'Peru' AND year = 2025
GROUP BY year, month
ORDER BY year, month;
```

**Roll-up.** `ROLLUP` devuelve cada mercado y el total general del conjunto seleccionado:

```sql
SELECT coalesce(region, 'ALL MARKETS') AS market,
       round(sum(revenue), 2) AS revenue
FROM sales
GROUP BY ROLLUP(region)
ORDER BY revenue DESC;
```

**Pivot.** Una agregación condicional coloca los ingresos de 2024 y 2025 en columnas para comparar categorías. Si se filtra un solo año, la columna del otro queda en cero.

**Ranking.** `dense_rank()` ordena las categorías por la suma de ingresos y permite identificar las líderes del conjunto filtrado.

La interfaz muestra el SQL de la consulta y permite exportar sus resultados como CSV. Los indicadores distinguen líneas de venta de unidades vendidas: el contador corresponde a filas, no a una cantidad de clientes o pedidos únicos.

## 5. Inicializar DuckDB-Wasm

Seguí el patrón de la [documentación de inicialización](https://duckdb.org/docs/current/clients/wasm/instantiation): seleccionar un bundle compatible, crear un worker, instanciar el motor y abrir una conexión.

```javascript
const bundle = await duckdb.selectBundle(duckdb.getJsDelivrBundles());
const workerURL = URL.createObjectURL(new Blob(
  [`importScripts("${bundle.mainWorker}");`],
  {type: 'text/javascript'}
));
const db = new duckdb.AsyncDuckDB(
  new duckdb.ConsoleLogger(), new Worker(workerURL)
);
await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
URL.revokeObjectURL(workerURL);
const connection = await db.connect();
```

Después se carga `model.sql` y se crean las tablas. La aplicación deshabilita los controles mientras el motor inicia o procesa una operación, y muestra un mensaje si falla el acceso al runtime o al modelo.

## 6. Validar antes de publicar

El archivo `test_model.py` ejecuta el modelo en DuckDB para Python y verifica la granularidad, los identificadores únicos, la cobertura del calendario y que los joins no multipliquen registros. También calcula los ingresos de manera independiente con enteros en centavos y los compara con la suma decimal de SQL.

Las agregaciones mensuales y por mercado deben sumar lo mismo que el total general. El subtotal de `ROLLUP` y las columnas del pivot deben reconciliarse con ese mismo importe. El resultado se guarda en `evidence/validation.json`.

Estas pruebas verifican la semántica del modelo. Como Python y WebAssembly son distribuciones diferentes, también hace falta abrir la aplicación y comprobar que el motor carga y que los filtros y las consultas responden. El tiempo mostrado en pantalla incluye comunicación y trabajo del navegador; no representa un benchmark del motor.

## 7. Automatizar el despliegue público

El workflow `.github/workflows/pages.yml` se activa al hacer push a `main`. Instala DuckDB para las pruebas, valida el modelo y la sintaxis JavaScript, conserva la evidencia y publica solamente `dist/`.

El job de despliegue depende de la validación. Si una aserción falla, no se publica la nueva versión. Para habilitarlo, el repositorio debe ser público y la fuente de Pages debe estar configurada en **GitHub Actions**. El token temporal del workflow evita guardar una clave de un proveedor externo.

GitHub documenta el proceso y los permisos de Pages en su [guía de workflows personalizados](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## 8. Qué demuestra y qué queda fuera

El proyecto muestra un flujo completo de modelado dimensional, consultas OLAP e interfaz web reproducible. Su tamaño es deliberadamente educativo. La base vive en memoria y se reconstruye al recargar; no ofrece ingesta continua, persistencia compartida ni control de acceso.

Para un conjunto mayor o una aplicación compartida, evaluaría archivos columnares, un proceso de ingesta y un motor alojado acorde con los requisitos. Antes de optimizar, conservaría las comprobaciones que garantizan que los totales siguen siendo correctos.

**Autora: Marymar Danytza Calloticona Chambilla.**

El repositorio, la aplicación y las evidencias de despliegue se añadirán aquí una vez verificados sus enlaces públicos.
