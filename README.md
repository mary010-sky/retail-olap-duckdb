# Retail OLAP Lab — DuckDB in the browser

**Autora: Marymar Danytza Calloticona Chambilla**

[Public application](https://mary010-sky.github.io/retail-olap-duckdb/) · [Published DEV.to article](https://dev.to/marymar_danytzacallotico/construi-una-solucion-olap-con-duckdb-en-el-navegador-y-despliegue-automatico-5h20) · [Successful application deployment](https://github.com/mary010-sky/retail-olap-duckdb/actions/runs/43618617969)

Verified: 100,000 rows, 24 months and total revenue **USD 76,263,950.00**. Video recording/publication and Telegram delivery will be completed by Marymar. The final submission remains incomplete until the public video URL is added.

An interactive OLAP solution with 100,000 reproducible synthetic sales, a star schema, exact decimal revenue, market/year filters, monthly drill-down, market roll-up, category/year pivot, ranking and CSV export.

## Architecture

Browser → static assets on a public SaaS → DuckDB-Wasm Web Worker → in-memory star schema → analytical SQL → dashboard.

No AWS service is configured, provisioned or required. The public hosting workflow targets GitHub Pages. DuckDB runs in the visitor's browser; it is not a shared cloud database.

## Run locally

```sh
python -m http.server 8000 --directory dist
```

Open http://localhost:8000. Opening index.html via file:// is unsupported. Internet access to jsDelivr is required for DuckDB-Wasm. Fonts fall back to system fonts if Google Fonts is unavailable.

## Verify correctness

```sh
pip install -r requirements-test.txt
python test_model.py
node --check dist/app.js
```

Tests independently calculate revenue in integer cents, check fact grain and join cardinality, and reconcile market/monthly aggregations, roll-up and pivot totals. Python DuckDB checks analytical semantics; browser execution must also be verified because the Wasm and Python distributions use different engine releases.

## Automated public deployment

Create a public GitHub repository, upload this source with its directory structure intact, and select **Settings → Pages → Source → GitHub Actions**. The workflow `.github/workflows/pages.yml` validates the model and publishes only `dist/` on every push to `main`. It uses GitHub's short-lived workflow token and requires no cloud API key. The deploy job waits for successful validation.

The Actions run URL and published application URL are evidence of an executed deployment; a workflow file alone is not proof of execution. See `delivery/links.json` for verified delivery status.

## Data model

`fact_sales`: one synthetic sales line; sale ID, date, market/product keys, quantity and unit price. Dimensions: `dim_date` (731 dates), `dim_region` (five markets), `dim_product` (four categories). `sales` joins the star and calculates decimal revenue in USD. USD is a common demonstration unit, not a currency conversion.

The dates cover 2024–2025, including leap day. A deterministic arithmetic generator avoids random changes on reload. Data deliberately has artificial patterns and is unsuitable for business conclusions.

## Limitations

This educational solution uses browser memory and does not persist across refreshes. It provides no shared ingestion service, user accounts or access control. The first load downloads the runtime. A blocked CDN or insufficient device memory can prevent startup. Browser elapsed times include rendering/communication and are not benchmark claims.

## Delivery materials

- `docs/article-devto.md`: article for DEV.to.
- `docs/video-script.md`: suggested recording of 4 minutes 30 seconds; Marymar records and publishes it.
- `delivery/`: verified links and remaining publication status.
- `evidence/validation.json`: actual test results when generated.

## References

- [DuckDB-Wasm initialization](https://duckdb.org/docs/current/clients/wasm/instantiation)
- [DuckDB-Wasm source](https://github.com/duckdb/duckdb-wasm)
- [GitHub Pages with custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

## License

MIT. Synthetic dataset dedicated to the public domain under CC0.
