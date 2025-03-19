import json
import imagehash
from PIL import Image

FICHIER_JSON = r"C:\Users\Chabot\Desktop\NSI\Trophee NSI\crawler.json"

SEUIL_HAMMING = 18 

def charger_hashes():
    """Charge la base de données des hashes depuis le fichier JSON."""
    try:
        with open(FICHIER_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def phash_image(image):
    """Calcule le hash perceptuel (average hash) de l'image."""
    return imagehash.average_hash(image)

def rechercher_image_pil(image):
    """Recherche une image PIL dans la base en utilisant la distance de Hamming."""
    base_hashes = charger_hashes()
    if not base_hashes:
        print("🚨 Aucune base de données d'images trouvée.")
        return None

    new_hash = phash_image(image)
    meilleure_correspondance = None
    distance_minimale = SEUIL_HAMMING + 1

    for h in base_hashes:
        hash_image = imagehash.hex_to_hash(h["hash"])
        distance = new_hash - hash_image  

        print(f"🔍 Comparaison avec {h['oeuvre']} → Distance : {distance}")

        if distance < distance_minimale:
            distance_minimale = distance
            meilleure_correspondance = h

    if meilleure_correspondance and distance_minimale <= SEUIL_HAMMING:
        print(f"✅ Image trouvée ! ({meilleure_correspondance['oeuvre']})")
        return meilleure_correspondance

    print("❌ Aucune correspondance trouvée.")
    return None

image_test = Image.open(r"C:\Users\Chabot\Desktop\NSI\Trophee NSI\b.jpg")
resultat = rechercher_image_pil(image_test)
if resultat:
    print(f"🖼️ Infos de l'œuvre trouvée : {resultat}")
