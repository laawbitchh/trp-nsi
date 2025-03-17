import requests
from bs4 import BeautifulSoup
import imagehash
import json
import os
import threading
from queue import Queue
from PIL import Image
from io import BytesIO
import re

MOTS_CLES_ART = ["art", "artiste", "peinture", "sculpture", "musée", "galerie", "design", "architecture"]
FICHIER_HASHES = r"C:\Users\Chabot\Desktop\NSI\Trophee NSI\crawler.json"
MAX_THREADS = 5
urls_visitees = set()
file_urls = Queue()
verrou = threading.Lock()

def sauvegarder_hashes(nouveaux_hashes):
    """Ajoute les nouveaux hashes au fichier JSON s'ils ne sont pas déjà enregistrés."""
    with verrou:
        if os.path.exists(FICHIER_HASHES):
            try:
                with open(FICHIER_HASHES, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = []
        else:
            data = []

        for h in nouveaux_hashes:
            if not any(d["hash"] == h["hash"] for d in data):
                data.append(h)

        with open(FICHIER_HASHES, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def extraire_infos(url):
    """Tente d'extraire le nom de l'artiste et de l'œuvre à partir de l'URL de l'image."""
    try:
        parts = url.split("/")
        artiste = parts[-2].replace("-", " ").title()
        nom_fichier = parts[-1].split(".jpg")[0].split("!")[0]
        nom_oeuvre = re.sub(r"[- ]?\d{4}.*$", "", nom_fichier).replace("-", " ").title()
        return artiste, nom_oeuvre
    except Exception:
        return "Inconnu", "Inconnu"

def hacher_images(urls_images):
    """Télécharge et hache les images en utilisant la méthode average_hash."""
    hashes = []
    for url in urls_images:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content)).convert("RGB")
                if min(img.size) < 100:
                    continue  
                hash_image = str(imagehash.average_hash(img))
                artiste, oeuvre = extraire_infos(url)
                hashes.append({"hash": hash_image, "artiste": artiste, "oeuvre": oeuvre})
                sauvegarder_hashes(hashes)
        except Exception as e:
            print(f"❌ Impossible de traiter l'image {url} :", e)

def contient_mot_cle(texte):
    """Vérifie si un texte contient l'un des mots-clés liés à l'art."""
    return any(mot in texte.lower() for mot in MOTS_CLES_ART)

def explorer(url):
    """Explore une page web et récupère les images et les liens pertinents."""
    if url in urls_visitees:
        return
    
    with verrou:
        urls_visitees.add(url)
    
    print(f"🌍 Exploration : {url}")

    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return

        soup = BeautifulSoup(r.content, "html.parser")

        if contient_mot_cle(soup.get_text()):
            images = [
                img["src"] if img["src"].startswith("http") else "https:" + img["src"]
                for img in soup.find_all("img") if "src" in img.attrs
            ]
            hacher_images(images)

        for lien in soup.find_all("a", href=True):
            href = lien["href"]
            if href.startswith("/fr/") and ":" not in href:
                url_complet = "https://www.wikiart.org" + href
                if url_complet not in urls_visitees:
                    file_urls.put(url_complet)

    except Exception as e:
        print(f"❌ Erreur lors de l'exploration de {url} :", e)

def worker():
    """Thread qui récupère une URL de la file et lance son exploration."""
    while True:
        url = file_urls.get()
        if url is None:
            break
        explorer(url)
        file_urls.task_done()

def crawler_art(url_depart):
    """Démarre l'exploration à partir d'une URL donnée."""
    print("🚀 Démarrage du crawler...")

    r = requests.get(url_depart, timeout=5)
    if r.status_code != 200:
        print("❌ Échec de la récupération de la page de départ.")
        return

    soup = BeautifulSoup(r.content, "html.parser")

    for lien in soup.find_all("a", href=True):
        href = lien["href"]
        if href.startswith("/fr/") and ":" not in href:
            file_urls.put("https://www.wikiart.org" + href)

    print("⚡ Lancement des threads...")
    threads = [threading.Thread(target=worker, daemon=True) for _ in range(MAX_THREADS)]
    
    for t in threads:
        t.start()

    file_urls.join()

    for _ in threads:
        file_urls.put(None)
    for t in threads:
        t.join()

crawler_art('https://www.wikiart.org/')
