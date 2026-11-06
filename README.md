# picrawler-control

Dépôt racine du projet PiCrawler : pilotage et maintenance du robot SunFounder PiCrawler.
Il regroupe les composants en sous-modules Git et contient la documentation du projet.

| Dossier | Contenu |
|---|---|
| `picrawler-robot/` | Programmes liés au robot et outils côté PC (dont le widget WiFi) |
| `picrawler-backend/` | API et services (à définir selon le scénario retenu) |
| `picrawler-frontend/` | Application web (à définir) |
| `picrawler-infra/` | Infrastructure et déploiement (à définir) |
| `local-env/` | Environnement local reproductible |
| `docs/` | Documentation et livrables datés (ex. `wifi-cadrage.md`) |

## Cloner

```
git clone https://github.com/GagaYaba/picrawler-control.git --recurse-submodules
```

Les sous-modules étant des dépôts privés, il faut être connecté à GitHub (clé SSH ou identifiants).
Mise à jour : `git submodule update --remote`.

## Règles de travail

Branches `feat/…`, `fix/…`, `docs/…` créées depuis `develop`, commits en anglais (Conventional Commits),
fusion par pull request. Aucun mot de passe, clé ou fichier `.env` dans les dépôts.
