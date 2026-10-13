import os
import tempfile

# Keep every test away from the real data/ folder (must run before nasmo.config is imported).
os.environ.setdefault("NASMO_DATA_DIR", tempfile.mkdtemp(prefix="nasmo_tests_"))
