"""Convert HTML file to gzipped C array format."""

from __future__ import annotations

import gzip
from pathlib import Path

from loggerplusplus import Logger

logger = Logger(
    identifier=__name__,
    follow_logger_manager_rules=True,
)

INPUT_FILE = Path("ui.html")
COMPRESSED_FILE = Path("tmp_ui.gz")  # Fichier compressé
OUTPUT_FILE = Path("html_as_const.txt")  # Tableau C

# Étape 1 : Compression gzip
with INPUT_FILE.open("rb") as f_in, gzip.open(COMPRESSED_FILE, "wb") as f_out:
    f_out.writelines(f_in)

# Étape 2 : Lecture du fichier gzip et conversion en tableau C
compressed_data = COMPRESSED_FILE.read_bytes()

# Création du tableau en C
BYTE_ARRAY = ", ".join(f"{b}" for b in compressed_data)
CONST_ARRAY = (
    f"const uint8_t ELEGANT_HTML[{len(compressed_data)}] PROGMEM = {{ {BYTE_ARRAY} }};"
)

# Sauvegarde dans un fichier
OUTPUT_FILE.write_text(CONST_ARRAY, encoding="utf-8")

# Étape 3 : Nettoyage
COMPRESSED_FILE.unlink()

logger.info(f"Conversion terminée. Tableau sauvegardé dans {OUTPUT_FILE}.")
