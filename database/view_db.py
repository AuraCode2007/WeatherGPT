"""
database/view_db.py — Database Inspector Utility
Inspect and display tables, schemas, and live records from WeatherGPT's database.

Usage:
    python database/view_db.py
    python database/view_db.py --table weather_snapshots
    python database/view_db.py --table chat_logs
    python database/view_db.py --table alert_logs
"""
import sys
import os
import argparse
from sqlalchemy import create_engine, inspect, text
from tabulate import tabulate

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config import DATABASE_URL


def view_database(target_table: str | None = None):
    print("\n" + "=" * 70)
    print("    WeatherGPT Database Inspector")
    print("=" * 70)
    print(f"Target Database URI: {DATABASE_URL}\n")

    connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    inspector = inspect(engine)

    table_names = inspector.get_table_names()
    if not table_names:
        print("[WARNING] No tables found in database. Run `python -m backend.db.init_db` to create tables.")
        return

    print(f"Active Tables ({len(table_names)}): {', '.join(table_names)}\n")

    with engine.connect() as conn:
        tables_to_show = [target_table] if target_table and target_table in table_names else table_names

        for table in tables_to_show:
            print(f"\n[TABLE: {table.upper()}]")
            print("-" * 70)

            # Columns
            columns = inspector.get_columns(table)
            col_headers = [col["name"] for col in columns]

            # Fetch rows
            res = conn.execute(text(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 15"))
            rows = res.fetchall()

            if not rows:
                print("   (Table is empty — no records stored yet)\n")
            else:
                table_data = []
                for row in rows:
                    formatted_row = []
                    for item in row:
                        val_str = str(item)
                        if len(val_str) > 50:
                            val_str = val_str[:47] + "..."
                        formatted_row.append(val_str)
                    table_data.append(formatted_row)

                print(tabulate(table_data, headers=col_headers, tablefmt="grid"))
                print(f"   (Showing top {len(rows)} recent records)\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect WeatherGPT database tables")
    parser.add_argument("--table", type=str, help="Specific table to inspect (chat_logs, weather_snapshots, alert_logs)")
    args = parser.parse_args()
    view_database(args.table)
