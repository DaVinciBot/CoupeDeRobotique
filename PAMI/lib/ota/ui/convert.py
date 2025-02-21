import gzip
import os

# Noms des fichiers
input_file = "ui.html"  # Remplacez par votre fichier HTML
compressed_file = "tmp_ui.gz"  # Fichier compressé
output_file = "html_as_const.txt"  # Tableau C

# Étape 1 : Compression gzip
with open(input_file, "rb") as f_in, gzip.open(compressed_file, "wb") as f_out:
    f_out.writelines(f_in)

# Étape 2 : Lecture du fichier gzip et conversion en tableau C
with open(compressed_file, "rb") as f:
    compressed_data = f.read()

# Création du tableau en C
byte_array = ", ".join(f"{b}" for b in compressed_data)
const_array = f"const uint8_t ELEGANT_HTML[{len(compressed_data)}] PROGMEM = {{ {byte_array} }};"

# Sauvegarde dans un fichier
with open(output_file, "w") as f:
    f.write(const_array)

# Étape 3 : Nettoyage
os.remove(compressed_file)


print(f"Conversion terminée. Tableau sauvegardé dans {output_file}")
