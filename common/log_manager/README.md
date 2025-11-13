# Log Manager

Gestionnaire de logs pour le robot avec capacités de filtrage et d'indexation SQLite.

## Fonctionnalités

- 🔍 **Indexation SQLite** : Recherche rapide dans de gros fichiers de logs
- 🎯 **Filtrage multi-critères** : Par exécution, niveau, logger, catégorie, fichier source
- 📊 **Détection d'exécutions** : Sépare automatiquement les différentes exécutions dans un même fichier
- 🎨 **Sortie colorisée** : Logs colorés selon le niveau (ERROR en rouge, WARNING en jaune, etc.)
- 📤 **Export** : Exporte les logs filtrés vers un fichier

## Installation

Aucune installation requise, tout est inclus dans le projet.

## Utilisation

### 1. Indexer un fichier de logs

```bash
lgpp_manager index 2025-11-06.log
```

Cela crée un fichier `logs/2025-11-06.db` contenant l'index SQLite.

### 2. Lister les exécutions

```bash
lgpp_manager list-executions 2025-11-06.log
```

Affiche toutes les exécutions détectées dans le fichier.

### 3. Afficher des logs filtrés

#### Par niveau

```bash
# Voir toutes les erreurs
lgpp_manager show 2025-11-06.log --level ERROR

# Voir les warnings et erreurs
lgpp_manager show 2025-11-06.log --level WARNING,ERROR
```

#### Par exécution

```bash
# Lister d'abord les exécutions
lgpp_manager list-executions 2025-11-06.log

# Voir une exécution spécifique
lgpp_manager show 2025-11-06.log --execution 2025-11-06_exec002
```

#### Par catégorie (préfixes uniformisés)

```bash
# Tous les logs de navigation
lgpp_manager show 2025-11-06.log --category "NAV:"

# Logs du rolling basis
lgpp_manager show 2025-11-06.log --category "CTRL:RB"

# Logs du lidar
lgpp_manager show 2025-11-06.log --category "SENSOR:Lidar"
```

#### Par logger

```bash
# Logs du Navigator
lgpp_manager show 2025-11-06.log --logger Navigator

# Logs du WS_Server
lgpp_manager show 2025-11-06.log --logger WS_Server
```

#### Par fichier source

```bash
# Logs provenant de navigator.py
lgpp_manager show 2025-11-06.log --file navigator.py

# Logs provenant de tous les fichiers lidar
lgpp_manager show 2025-11-06.log --file lidar
```

#### Combinaison de filtres

```bash
# Erreurs du Navigator dans l'exécution 2
lgpp_manager show 2025-11-06.log \
    --execution 2025-11-06_exec002 \
    --logger Navigator \
    --level ERROR

# Logs de navigation WARNING ou ERROR limités à 50 entrées
lgpp_manager show 2025-11-06.log \
    --category "NAV:" \
    --level WARNING \
    --limit 50
```

### 4. Exporter des logs

```bash
# Exporter toutes les erreurs dans un fichier
lgpp_manager export 2025-11-06.log -o errors.txt --level ERROR

# Exporter les logs d'une exécution spécifique
lgpp_manager export 2025-11-06.log -o exec2.txt \
    --execution 2025-11-06_exec002

# Exporter les logs de rolling basis
lgpp_manager export 2025-11-06.log -o rolling_basis.txt \
    --category "CTRL:RB"
```

## Options disponibles

| Option        | Alias | Description                                                |
| ------------- | ----- | ---------------------------------------------------------- |
| `--execution` | `-e`  | Filtrer par ID d'exécution                                 |
| `--level`     | `-l`  | Filtrer par niveau (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `--logger`    | `-L`  | Filtrer par nom de logger                                  |
| `--category`  | `-c`  | Filtrer par catégorie (NAV:, CTRL:, SENSOR:, etc.)         |
| `--file`      | `-f`  | Filtrer par fichier source                                 |
| `--limit`     | `-n`  | Limiter le nombre de résultats                             |
| `--no-color`  |       | Désactiver la colorisation                                 |

## Architecture

```
logs/
├── 2025-11-06.log          # Fichier de logs texte original
├── 2025-11-06.db           # Index SQLite pour recherche
└── ...
```

### Base de données

Le schéma SQLite contient deux tables :

**`executions`** : Liste des exécutions détectées

- `execution_id` : Identifiant unique (ex: 2025-11-06_exec002)
- `start_time` : Heure de début
- `end_time` : Heure de fin (optionnel)
- `log_file` : Fichier de logs source
- `description` : Description

**`logs`** : Entrées de logs indexées

- `execution_id` : Lien vers l'exécution
- `timestamp` : Horodatage
- `level` : Niveau (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `logger_name` : Nom du logger
- `file_name` : Fichier source
- `line_number` : Numéro de ligne
- `category` : Catégorie extraite ([NAV:Task], [CTRL:RB], etc.)
- `message` : Message du log
- `raw_line` : Ligne brute originale
- `line_offset` : Position dans le fichier (pour récupération rapide)

## Détection d'exécutions

Le système détecte automatiquement les nouvelles exécutions en cherchant des marqueurs comme :

- `[INIT] Initializing all systems...`

Chaque nouvelle exécution reçoit un ID unique : `{date}_exec{numéro:03d}`

## Performance

- **Indexation** : ~30 secondes pour 4 Mo de logs (~27 000 entrées)
- **Recherche** : Quasi-instantanée grâce aux index SQLite
- **Stockage** : Le fichier .db fait environ 10-20% de la taille du fichier .log

## Exemples de cas d'usage

### Déboguer une exécution spécifique

```bash
# 1. Trouver l'exécution
lgpp_manager list-executions 2025-11-06.log

# 2. Voir toutes les erreurs de cette exécution
lgpp_manager show 2025-11-06.log \
    --execution 5 \
    --level ERROR
```

### Analyser les problèmes de navigation

```bash
# Voir tous les logs de navigation avec WARNING ou ERROR
lgpp_manager show 2025-11-06.log \
    --category "NAV:" \
    --level WARNING

# Exporter pour analyse
lgpp_manager export 2025-11-06.log -o nav_issues.txt \
    --category "NAV:" \
    --level "WARNING,ERROR"
```

### Déboguer un composant spécifique

```bash
# Voir tous les logs du rolling basis
lgpp_manager show 2025-11-06.log --category "CTRL:RB"

# Voir les logs du lidar seulement
lgpp_manager show 2025-11-06.log --category "SENSOR:Lidar"
```

## Prochaines améliorations possibles

- [ ] Hook en temps réel pour indexer pendant l'exécution (modifier loggerplusplus)
- [ ] Interface web pour visualiser les logs @clement ???
- [ ] Graphiques de distribution des niveaux de log
- [ ] Recherche en texte intégral dans les messages
- [ ] Export en JSON/CSV
- [ ] Recherche pour une ligne spécifique (numéro de ligne)
