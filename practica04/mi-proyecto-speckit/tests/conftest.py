import sys
from pathlib import Path

# Agregar src al sys.path para importación en desarrollo
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
