# Changer de WiFi avec le robot : cadrage

## Besoin
Gaëlle part de chez elle ce week-end et veut continuer à travailler sur le PiCrawler. Le Pi ne connaît que le WiFi de la maison, il faut donc lui apprendre d'autres réseaux et savoir quand PC et robot ne sont pas sur le même.

## Options

| Option | Principe | Simplicité | Sécurité | Remarque |
|---|---|---|---|---|
| A. Script PC (`picrawler-robot/tools/wifi/wifi_check.py`) | Compare le WiFi du PC et celui du Pi (via SSH + `nmcli`), propose la commande d'ajout | Très simple | Bonne : lecture seule, pas de mot de passe stocké | Marche seulement si le Pi est déjà joignable |
| B. Page web locale | Petit formulaire sur le PC | Moyen | Risque de manipuler des mots de passe dans une appli | Pas utile pour un projet étudiant, pour l'instant |
| C. Point d'accès de secours sur le Pi | Si aucun WiFi connu n'est trouvé, le Pi crée son propre WiFi | Moyen, à tester | Bonne, et c'est le seul filet si le réseau est perdu | À préparer à la maison, pas en dernière minute |
| D. Hotspot du téléphone | Le téléphone partage sa 4G/5G, PC et Pi s'y connectent | Très simple | Bonne | Réseau le plus fiable en déplacement : on l'ajoute au Pi avant de partir |

## Recommandation
1. **Avant de partir** : ajouter au Pi le hotspot du téléphone (option D) et, si possible, le WiFi du lieu où tu seras. Vérifier avec le script (option A).
2. Utiliser le script A au lancement des sessions pour détecter la différence de réseaux.
3. Option C en second temps, comme filet de sécurité.
4. La fenêtre (widget) est construite par-dessus le script A (même logique) : elle est maintenant dans `picrawler-robot`.

## Risques et parades
- **Se verrouiller hors du robot** : ne jamais supprimer l'ancien réseau, ne jamais lancer une commande qui bascule de réseau pendant la session SSH (on utilise `nmcli connection add`, qui enregistre sans basculer). Garder un accès de secours (câble, écran/clavier, ou point d'accès C).
- **Mots de passe WiFi** : jamais dans le dépôt, jamais dans le chat. Saisie en direct sur le Pi (`read -s`).
- **Portail captif / isolation client** (hôtel, Ynov, WiFi public) : le Pi ne peut pas valider un portail dans un navigateur, et ces réseaux empêchent souvent PC et Pi de se parler. Préférer le hotspot du téléphone.
- **Adresse IP** : elle change d'un réseau à l'autre. Prévoir de la retrouver (nom `raspberrypi.local`, ou liste des appareils du hotspot).
- **Toute modification sur le Pi** se fait avec Gaëlle présente, pour reprendre la main si ça tourne mal.

## État
Au 6 novembre 2026 : la lecture (fenêtre `wifi_widget.py`) a été testée sur le vrai robot depuis un PC Windows, et l'ajout du hotspot du téléphone a été fait et vérifié à la main avec `nmcli`. Le bouton d'ajout de la fenêtre et `picrawler_ssh.py` n'ont pas encore été testés en vrai.
