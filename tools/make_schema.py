"""Writes supabase_schema.sql from the single SCHEMA definition in nasmo/store.py."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nasmo.store import postgres_ddl

out = Path(__file__).resolve().parent.parent / "supabase_schema.sql"
out.write_text(postgres_ddl(), encoding="utf-8")
print("wrote", out)
