# MESURE

Consulter consomme.
Transfert = détruire ici / naître là.
Version 0 : téléphone + gratuit.

Pas un fork. Pas un photon. Pas un node QUANTUM.

## Commandes

```bash
python3 mesure.py ouvrir --objet figure --lectures 1
python3 mesure.py ouvrir --objet figure --fichier ./preuve.bin --lectures 1
python3 mesure.py consulter carte.mesure.json
python3 mesure.py lire carte.mesure.json
```

`consulter` décrémente `lectures`. À zéro : `detruit` + refus.
Ne pas forker une mesure.
Sans `--fichier`, `sha256` porte sur le payload `{objet,lectures}` (`sha_sur: payload`).
Avec `--fichier`, `sha256` porte sur les octets (`sha_sur: fichier`).
`consulter` prend un verrou fichier (flock) pour éviter la double conso.

Carte citée : https://acorn-royal-dune-blend.grok.me  
Cadastre : https://github.com/carllaliberte/famille

© 2026 Carl Laliberté. MIT.
