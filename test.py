import json
import imagehash
import requests
from PIL import Image
from io import BytesIO

FICHIER_JSON = r"C:\Users\Chabot\Desktop\NSI\Trophee NSI\crawler.json"

def charger_hashes():
    """Charge la base de données des hashes depuis le fichier JSON."""
    try:
        with open(FICHIER_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def phash_image(image):
    """Calcule le hash perceptuel de l'image."""
    return str(imagehash.average_hash(image))

def rechercher_image(image_path):
    """Recherche une image locale dans la base de données et retourne ses informations si elle est trouvée."""
    base_hashes = charger_hashes()
    if not base_hashes:
        print("🚨 Aucune base de données d'images d'art trouvée.")
        return None

    img = Image.open(image_path).convert("RGB")
    new_hash = phash_image(img)

    for h in base_hashes:
        hash_image = imagehash.hex_to_hash(h["hash"])
        if hash_image == imagehash.hex_to_hash(new_hash):
            print(f"✅ Image trouvée pour le hash : {new_hash}")
            return h

    print("❌ Aucune correspondance trouvée.")
    return None

def rechercher_image_url(image_url):
    """Télécharge l'image depuis une URL, calcule son hash et la recherche dans la base de données."""
    try:
        response = requests.get(image_url, timeout=5)
        if response.status_code != 200:
            print("❌ Impossible de récupérer l'image depuis l'URL.")
            return None

        img = Image.open(BytesIO(response.content)).convert("RGB")
        return rechercher_image_pil(img)

    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'image : {e}")
        return None

def rechercher_image_pil(image):
    """Recherche une image PIL dans la base de données et retourne ses informations si elle est trouvée."""
    base_hashes = charger_hashes()
    if not base_hashes:
        print("🚨 Aucune base de données d'images d'art trouvée.")
        return None

    new_hash = phash_image(image)

    for h in base_hashes:
        hash_image = imagehash.hex_to_hash(h["hash"])
        if hash_image == imagehash.hex_to_hash(new_hash):
            print(f"✅ Image trouvée pour le hash : {new_hash}")
            return h

    print("❌ Aucune correspondance trouvée.")
    return None

image_test = r"C:\Users\Chabot\Desktop\NSI\Trophee NSI\c.jpg"
resultat = rechercher_image(image_test)
if resultat:
    print(f"🖼️ Infos de l'œuvre trouvée : {resultat}")

image_test_url = ""
# resultat_url = rechercher_image_url(image_test_url)
# if resultat_url:
#    print(f"🖼️ Infos de l'œuvre trouvée depuis l'URL : {resultat_url}")
