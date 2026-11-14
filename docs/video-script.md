# Guion de video — máximo 4 minutos 30 segundos

Autora y presentadora: Marymar Danytza Calloticona Chambilla.
Marymar grabará y publicará el video y enviará los enlaces al grupo de Telegram.

| Tiempo | Mostrar y explicar |
| --- | --- |
| 0:00–0:25 | Presentación con nombre completo. Objetivo: solución OLAP con DuckDB-Wasm, 100.000 ventas sintéticas y alojamiento público sin configurar AWS. |
| 0:25–1:05 | Repositorio público. Abrir dist/model.sql y explicar fact_sales, dim_date, dim_region y dim_product. Cada fila es una línea de venta; ingreso = cantidad × precio decimal. |
| 1:05–1:45 | Construcción: mostrar inicialización del Web Worker en app.js y ejecución del modelo SQL. Explicar que la base se crea en memoria dentro del navegador. |
| 1:45–2:35 | App pública: indicadores y gráfico. Filtrar Perú y 2025; pulsar Apply slice. Ejecutar monthly revenue y explicar drill-down del total a los meses. |
| 2:35–3:15 | Quitar filtros. Mostrar roll-up con ALL MARKETS, pivot por categoría/año y ranking. Exportar un CSV. |
| 3:15–4:05 | Abrir workflow y una ejecución realmente exitosa en Actions. Mostrar validación y deploy. Explicar que push a main inicia las pruebas y la publicación. Mostrar URL pública. |
| 4:05–4:30 | Abrir artículo publicado en DEV.to. Mencionar límites: datos sintéticos, memoria del navegador, dependencia del CDN y ausencia de persistencia compartida. Cerrar con enlaces en descripción. |

Grabar a 1080p si es posible. No mostrar claves, notificaciones privadas ni páginas de autenticación. Comprobar duración menor o igual a cinco minutos y visibilidad pública antes de entregar la URL. No presentar un workflow pendiente o fallido como exitoso.

Descripción sugerida: «Retail OLAP Lab con DuckDB-Wasm. Autora: Marymar Danytza Calloticona Chambilla. Enlaces al repositorio, aplicación y artículo: añadir las URL verificadas de delivery/links.json».
