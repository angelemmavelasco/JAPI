import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import src.utils.utils as utils
import config.settings as config




def main():

    for file in utils.list_files_in_directory(config.CORE_DIR):
        print(file)

    print(utils.get_current_timestamp())


if __name__ == "__main__":
    main()