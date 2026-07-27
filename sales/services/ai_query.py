from django.conf import settings
from django.db import connection
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SQLDatabase
from langchain_classic.chains import create_sql_query_chain
import os
import re
from typing import Dict, Any

class AIQueryService:
    """Natural Language → SQL + Business Insights for TrailGear"""

    def __init__(self):
        db = settings.DATABASES['default']
        self.connection_string = (
            f"postgresql+psycopg2://{db['USER']}:{db['PASSWORD']}@"
            f"{db.get('HOST', 'localhost')}:{db.get('PORT', 5432)}/{db['NAME']}"
        )
        
        self.db = SQLDatabase.from_uri(
            self.connection_string,
            include_tables=["sales_sale", "sales_customer", "sales_salesperson", "sales_product"],
            sample_rows_in_table_info=3,
        )

        self.db._schema = self._get_schema_context()

    def _get_schema_context(self) -> str:
        return """
You are an expert SQL analyst for TrailGear, an Australian hiking and outdoor gear retailer.
Always generate valid PostgreSQL. Always qualify every column with a table alias.

### Tables

sales_sale        — alias: s
  id, customer_id, salesperson_id, product_id,
  quantity        (integer, units sold),
  date            (DATE),
  status          (text: 'pending' | 'won' | 'lost' | 'cancelled'),
  notes           (text)

sales_salesperson — alias: sp
  id, first_name, last_name, gender ('M'|'F'), email, phone,
  region          (text: 'NSW'|'VIC'|'QLD'|'WA'|'SA'|'TAS'|'ACT'|'NT')

sales_customer    — alias: c
  id, first_name, last_name, gender ('M'|'F'),
  company, email, phone, address, city,
  state           (full state name, e.g. 'New South Wales'),
  postcode

sales_product     — alias: p
  id, name, sku,
  category        (text: 'hardware'|'software'|'services'|'consumables'),
  price           (decimal, unit price in AUD),
  description

### Joins
  s.customer_id    = c.id
  s.salesperson_id = sp.id
  s.product_id     = p.id

### Revenue
  Revenue for a sale row = s.quantity * p.price
  Total revenue          = SUM(s.quantity * p.price)
  Filter to won sales    = WHERE s.status = 'won'

### Date / time rules
  - "this year"  → current Australian financial year: Jul 1 to Jun 30
      WHERE s.date >= DATE_TRUNC('year', CURRENT_DATE - INTERVAL '6 months') + INTERVAL '6 months'
        AND s.date <  DATE_TRUNC('year', CURRENT_DATE - INTERVAL '6 months') + INTERVAL '18 months'
  - "last year"  → the financial year immediately before this one
  - "this month" → EXTRACT(MONTH FROM s.date) = EXTRACT(MONTH FROM CURRENT_DATE)
                   AND EXTRACT(YEAR  FROM s.date) = EXTRACT(YEAR  FROM CURRENT_DATE)
  - Always use s.date (not just "date") to avoid ambiguity

### Output rules
  - Return only the raw SQL statement — no markdown fences, no explanation, no trailing semicolon
  - Use LIMIT 10 unless the question specifies a different number
  - Concatenate first_name || ' ' || last_name AS name for people
  - Round monetary values: ROUND(SUM(s.quantity * p.price), 2)
"""

    def get_llm(self, provider: str = "openai", temperature: float = 0.0):
        if provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
            return ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=temperature)
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)

    def clean_sql(self, sql: str) -> str:
        if not sql:
            return ""
        sql = re.sub(r'^SQLQuery:\s*', '', sql, flags=re.IGNORECASE | re.MULTILINE)
        sql = re.sub(r'^```(?:sql)?\s*', '', sql, flags=re.IGNORECASE | re.MULTILINE)
        sql = re.sub(r'```\s*$', '', sql, flags=re.IGNORECASE | re.MULTILINE)
        return sql.strip().rstrip(';').strip()

    def execute_query(self, sql: str) -> Dict[str, Any]:
        with connection.cursor() as cursor:
            try:
                cursor.execute(sql)
                if cursor.description:  # SELECT
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    return {
                        "columns": columns,
                        "rows": rows,
                        "rowcount": len(rows)
                    }
                return {"status": f"{cursor.rowcount} rows affected"}
            except Exception as e:
                error_msg = str(e)
                print("=== SQL EXECUTION ERROR ===")
                print("SQL:", sql)
                print("Error:", error_msg)
                print("==========================")
                return {"error": error_msg}

    def query(self, question: str, provider: str = "openai") -> Dict[str, Any]:
        """Natural language to SQL with detailed error handling"""
        llm = self.get_llm(provider)
        chain = create_sql_query_chain(llm, self.db, k=10)

        try:
            response = chain.invoke({"question": question})

            if isinstance(response, dict):
                raw_sql = response.get("query", str(response))
            else:
                raw_sql = str(response)

            sql_query = self.clean_sql(raw_sql)

            # Debug: print to console what SQL was generated
            print("=== GENERATED SQL ===")
            print(sql_query)
            print("====================")

            result = self.execute_query(sql_query)

            return {
                "sql": sql_query,
                "result": result,
                "success": "error" not in result,
                "type": "query"
            }
        except Exception as e:
            error_msg = str(e)
            print("AI Query Error:", error_msg)   # Server console log

            return {
                "success": False,
                "error": error_msg,
                "sql": sql_query if 'sql_query' in locals() else None,
                "type": "query"
            }
        
    def insights(self, topic: str = "overall sales performance", provider: str = "openai") -> Dict[str, Any]:
        """Generate business insights"""
        llm = self.get_llm(provider, temperature=0.7)
        
        prompt = f"""You are a senior sales strategist for TrailGear.
Provide 4-6 concise, actionable insights and recommendations about: {topic}."""

        try:
            response = llm.invoke(prompt)
            return {
                "insights": response.content,
                "type": "insights",
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "insights"
            }