"""Analytical correctness checks; independent revenue calculation in integer cents."""
import json
from decimal import Decimal
from pathlib import Path
import duckdb

db = duckdb.connect()
db.execute(Path('dist/model.sql').read_text(encoding='utf-8'))
assert db.sql('SELECT count(*) FROM fact_sales').fetchone()[0] == 100000
assert db.sql('SELECT count(*) FROM sales').fetchone()[0] == 100000
assert db.sql('SELECT count(DISTINCT sale_id) FROM sales').fetchone()[0] == 100000
assert db.sql('SELECT count(*) FROM dim_date').fetchone()[0] == 731
assert db.sql('SELECT min(sale_date),max(sale_date) FROM sales').fetchone() == (__import__('datetime').date(2024,1,1),__import__('datetime').date(2025,12,31))
expected = sum((1+(n//20)%5)*(1000+(n*37)%49000) for n in range(1,100001))
total = db.sql('SELECT sum(revenue) FROM sales').fetchone()[0]
assert total == Decimal(expected)/100
markets = db.sql('SELECT region,sum(revenue) FROM sales GROUP BY region').fetchall()
assert len(markets) == 5 and sum(r[1] for r in markets) == total
monthly = db.sql('SELECT year,month,sum(revenue) FROM sales GROUP BY year,month').fetchall()
assert len(monthly) == 24 and sum(r[2] for r in monthly) == total
assert db.sql("SELECT count(*) FROM sales WHERE region='Peru' AND year=2025").fetchone()[0] > 0
rollup = db.sql('SELECT region,sum(revenue) FROM sales GROUP BY ROLLUP(region)').fetchall()
assert len(rollup) == 6 and next(r[1] for r in rollup if r[0] is None) == total
pivot = db.sql('SELECT category,sum(CASE WHEN year=2024 THEN revenue ELSE 0 END),sum(CASE WHEN year=2025 THEN revenue ELSE 0 END) FROM sales GROUP BY category').fetchall()
assert len(pivot) == 4 and sum(r[1]+r[2] for r in pivot) == total
ranks = db.sql('SELECT category,dense_rank() OVER (ORDER BY sum(revenue) DESC) FROM sales GROUP BY category').fetchall()
assert len(ranks) == 4 and min(r[1] for r in ranks) == 1
result = {'status':'passed','duckdb_version':duckdb.__version__,'sales_rows':100000,'date_rows':731,'months':len(monthly),'markets':len(markets),'revenue_usd':str(total),'independent_expected_cents':expected,'checks':['grain','unique identifiers','join cardinality','calendar coverage','exact revenue','market reconciliation','monthly reconciliation','slice','rollup','pivot','ranking']}
Path('evidence').mkdir(exist_ok=True)
Path('evidence/validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
