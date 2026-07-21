"""
EXAMPLE 5 - NATURAL LANGUAGE -> SQL

USE CASE: turn a plain-English question into a correct SQL query a program can
run. A classic spot where a few key constraints prevent broken or unsafe SQL.

Optimizations applied: provide the SCHEMA as context, constrain the SQL dialect,
demand a read-only query, give a few-shot example, force step-by-step mapping,
and require output as runnable SQL only (no markdown fences).

Run:  secrun python examples/05_text_to_sql.py
"""

# --- make the repo-root 'common' package importable when run directly ---
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import chat, header, rule

SCHEMA = """\
-- PostgreSQL schema
customers(id PK, name, country, created_at)
orders(id PK, customer_id FK->customers.id, total_cents, status, created_at)
order_items(id PK, order_id FK->orders.id, product, qty, unit_cents)
"""

QUESTION = "What are the top 5 countries by total completed-order revenue in 2025?"


# --------------------------------------------------------------------------
# BEFORE: no schema, no dialect, no constraints. The model invents table/column
# names and may emit prose or markdown fences that break a programmatic runner.
# --------------------------------------------------------------------------
def naive() -> str:
    return chat(
        [{"role": "user", "content": f"Write SQL for: {QUESTION}"}],
        temperature=0.3,
    )


# --------------------------------------------------------------------------
# AFTER: schema as grounding + dialect + safety + one example + output rules.
# --------------------------------------------------------------------------
OPTIMIZED_SYSTEM = f"""\
You are a PostgreSQL expert. Convert the user's question into ONE SQL query.

DATABASE SCHEMA (use ONLY these tables/columns):
{SCHEMA}

RULES:
- PostgreSQL dialect only.
- READ-ONLY: SELECT statements only. Never write INSERT/UPDATE/DELETE/DROP.
- 'revenue' = SUM(orders.total_cents) / 100.0, aliased as revenue.
- 'completed' orders means orders.status = 'completed'.
- If the question is ambiguous or needs a table not in the schema, return a
  single line: -- CANNOT ANSWER: <reason>
- Output ONLY the raw SQL (or the comment). No prose, no ``` fences.

EXAMPLE
Question: How many customers are in Germany?
SQL:
SELECT COUNT(*) FROM customers WHERE country = 'Germany';
"""


def optimized() -> str:
    return chat(
        [
            {"role": "system", "content": OPTIMIZED_SYSTEM},
            {"role": "user", "content": f"Question: {QUESTION}\nSQL:"},
        ],
        temperature=0,
    )


if __name__ == "__main__":
    header("EXAMPLE 5 - TEXT TO SQL")
    print("\nSchema:\n", SCHEMA)
    print("Question:", QUESTION)

    rule()
    print("\n[BEFORE - no schema, no rules] ->")
    print(naive())

    rule()
    print("\n[AFTER - schema + dialect + safety + example + format] ->")
    print(optimized())

    rule()
    print(
        "\nWHY IT'S BETTER:\n"
        "  - The schema grounds column/table names so the model can't invent them.\n"
        "  - 'READ-ONLY, SELECT only' is a critical safety guardrail.\n"
        "  - Defining 'revenue'/'completed' removes business-logic ambiguity.\n"
        "  - The 'CANNOT ANSWER' escape hatch beats a confidently wrong query.\n"
        "  - 'SQL only, no fences' makes the output directly runnable."
    )
