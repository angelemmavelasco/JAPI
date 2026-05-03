from pathlib import Path
import sys


# Configuracion de ruta base y rutas adicionales

BASE_DIR = Path(__file__).resolve().parent.parent


if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
UTILS_DIR = BASE_DIR / "src" / "utils"
SRC_DIR = BASE_DIR / "src"
CORE_DIR = BASE_DIR / "core"

