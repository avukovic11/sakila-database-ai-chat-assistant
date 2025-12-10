from typing import Annotated
import psycopg2
import psycopg2.extras
import sqlparse

DB_CONFIG = {
    "dbname": "sakila",
    "user": "sakila",
    "password": "p_ssW0rd",
    "host": "localhost",
    "port": 5432
}

def is_valid_sql(sql_query: str) -> bool:
    parsed = sqlparse.parse(sql_query)
    for statement in parsed:
        if statement.get_type() != 'SELECT':
            return False
    return True

def execute_sql(sql_query: Annotated[str, "A valid SQL query to execute on the Sakila PostgreSQL database"], 
                limit: Annotated[int, "Limit how many rows are shown (max 100)"]=30) -> str:
    
    if not is_valid_sql(sql_query):
        return "User is not allowed to modify the database"
    MAX_QUERIES_PER_REQUEST = 10
    if len(sql_query.split(';')) > MAX_QUERIES_PER_REQUEST:
        return f"Too many queries in the request. Please limit to {MAX_QUERIES_PER_REQUEST} queries at once."

    result = ""
    if limit <= 0:
        limit = 30
        result += "Limit must be positive. Defaulting to 30.\n"
    if limit > 100:
        limit = 100
        result += "Limit exceeds maximum of 100. Capping to 100.\n"

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SET statement_timeout = 10000;")  # 10 seconds
        cur.execute(sql_query)
        try:
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]
            if not rows:
                result += "Query executed successfully but returned no rows."
            else:
                result += f"Columns: {', '.join(cols)}\n\nResults:\n"
                for row in rows[:limit]:
                    result += str(row) + "\n"
                if len(rows) > limit:
                    result += f"\n...and {len(rows)-limit} more rows"
        except psycopg2.ProgrammingError:
            result = f"Query executed successfully. Rows affected: {cur.rowcount}"
        conn.commit()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        return f"Error executing query: {str(e)}"

def get_full_database_profile() -> str:
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        output = []

        # TABLE SCHEMA
        cur.execute("""
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)
        rows = cur.fetchall()

        schema_info = {}
        for row in rows:
            schema_info.setdefault(row["table_name"], []).append(
                f"  - {row['column_name']}: {row['data_type']} "
                f"({'NULL' if row['is_nullable']=='YES' else 'NOT NULL'})"
            )

        output.append("=== TABLE SCHEMA ===\n")
        for table, columns in sorted(schema_info.items()):
            output.append(f"Table: {table}\n" + "\n".join(columns) + "\n")

        # 2) SAMPLE ROWS
        output.append("\n=== SAMPLE ROWS (LIMIT 1 PER TABLE) ===\n")
        for table in sorted(schema_info.keys()):
            try:
                cur.execute(f"SELECT * FROM {table} LIMIT 1;")
                sample = cur.fetchone()
                if sample:
                    output.append(f"Sample from {table}:\n  {dict(sample)}\n")
                else:
                    output.append(f"Sample from {table}: <empty table>\n")
            except Exception:
                output.append(f"Sample from {table}: <could not fetch>\n")

        # 3) PRIMARY KEYS
        cur.execute("""
            SELECT
                tc.table_name,
                kc.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kc
                ON tc.constraint_name = kc.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = 'public'
            ORDER BY tc.table_name;
        """)
        pk_rows = cur.fetchall()

        output.append("\n=== PRIMARY KEYS ===\n")
        for row in pk_rows:
            output.append(f"{row['table_name']}: {row['column_name']}")

        # 4) FOREIGN KEYS
        cur.execute("""
            SELECT
                tc.table_name AS foreign_table,
                kcu.column_name AS foreign_column,
                ccu.table_name AS primary_table,
                ccu.column_name AS primary_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public';
        """)
        fk_rows = cur.fetchall()

        output.append("\n\n=== FOREIGN KEYS ===\n")
        for row in fk_rows:
            output.append(
                f"{row['foreign_table']}.{row['foreign_column']} "
                f"→ {row['primary_table']}.{row['primary_column']}"
            )

        # 5) FUNCTIONS
        cur.execute("""
            SELECT
                p.proname AS function_name,
                pg_catalog.pg_get_functiondef(p.oid) AS definition
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'public'
            AND p.prokind = 'f'
            ORDER BY p.proname;
        """)
        func_rows = cur.fetchall()

        output.append("\n\n=== FUNCTIONS (User-defined) ===\n")
        if func_rows:
            for row in func_rows:
                output.append(f"Function: {row['function_name']}\n{row['definition']}\n")
        else:
            output.append("<No custom functions>\n")

        # 6) DATA TYPES
        cur.execute("""
            SELECT t.typname AS type_name, t.typcategory, t.typtype
            FROM pg_type t
            JOIN pg_namespace n ON t.typnamespace = n.oid
            WHERE n.nspname = 'public'
              AND t.typtype IN ('e', 'd', 'c')  -- enum, domain, composite
            ORDER BY t.typname;
        """)
        type_rows = cur.fetchall()

        output.append("\n\n=== CUSTOM DATA TYPES ===\n")
        if type_rows:
            for row in type_rows:
                type_kind = {
                    "e": "ENUM",
                    "d": "DOMAIN",
                    "c": "COMPOSITE"
                }.get(row["typtype"], "UNKNOWN")
                output.append(f"{row['type_name']} ({type_kind})")
        else:
            output.append("<No custom types>\n")

        # 7) VIEWS
        cur.execute("""
            SELECT table_name, view_definition
            FROM information_schema.views
            WHERE table_schema='public'
            ORDER BY table_name;
        """)
        view_rows = cur.fetchall()

        output.append("\n\n=== VIEWS ===\n")
        for row in view_rows:
            output.append(f"View: {row['table_name']}\n{row['view_definition']}\n")

        cur.close()
        conn.close()

        return "\n".join(output)

    except Exception as e:
        return f"Error generating database profile: {e}"
    
FULL_DATABASE_PROFILE = get_full_database_profile()