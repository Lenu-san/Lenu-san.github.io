# lenu-san.github.io

Portfolio de Lénusan Gunarajah — consultant & ingénieur cybersécurité junior,
orienté audit, sécurité des infrastructures et services managés.

En ligne : **https://lenu-san.github.io** (français) · **https://lenu-san.github.io/en/** (English)

## Principe

Site statique généré par un script Python (bibliothèque standard uniquement)
à partir de deux fichiers de traduction. Aucun framework, aucune police
externe, aucun traceur : deux fichiers HTML, une feuille de style, un script
de confort.

```
locales/fr.json      contenu français
locales/en.json      contenu anglais (même structure)
build.py             générateur : lit les locales, écrit les pages
assets/              style.css, script.js, favicon, vignettes de partage
index.html           page française (générée)
en/index.html        page anglaise (générée)
sitemap.xml          généré
robots.txt           généré
tools/make-images.py vignettes Open Graph et icône (optionnel, Pillow)
```

Les deux langues sont de vraies pages distinctes, indexables séparément et
reliées par `hreflang`. Le bouton FR / EN est un simple lien, toujours
visible dans l'en-tête, y compris sur mobile.

Le thème clair / sombre suit le réglage du système ; le bouton de l'en-tête
permet de forcer l'un ou l'autre (choix mémorisé dans le navigateur).

## Modifier le contenu

1. Éditer `locales/fr.json` et `locales/en.json` (les deux fichiers ont la même structure).
2. Régénérer :

```bash
python build.py
```

3. Vérifier en local (par exemple `python -m http.server 8000` puis
   http://localhost:8000/), puis committer les fichiers générés.

Les liens (LinkedIn, GitHub, Credly, e-mail) sont centralisés dans le
dictionnaire `SITE` en tête de `build.py`.

## Ajouter le CV

Déposer le fichier PDF dans `assets/cv.pdf` et relancer `python build.py` :
le bouton « Télécharger mon CV » apparaît automatiquement dans le hero et
dans la section Contact. Tant que le fichier est absent, la section Contact
indique que le CV est disponible sur demande.

## Vignettes de partage

`assets/og.png` et `assets/og-en.png` (1200 × 630) sont utilisées par LinkedIn
et les messageries lors d'un partage. Pour les régénérer après un changement
de titre :

```bash
python -m pip install pillow
python tools/make-images.py
```

## Licence

Code du site : MIT. Textes et contenus : tous droits réservés.
