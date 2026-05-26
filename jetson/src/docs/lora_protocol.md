# Protocole LoRa - Communication Jetson / Robot / PAMI

## Vue d'ensemble

Le Jetson Nano est le serveur de vision central. Il communique avec les robots et PAMIs via un module LoRa DX LR01 en UART (115200 baud).

**Format des messages :** texte ASCII, champs separés par `|`, terminés par `\n`.

```
<num_commande>|<arg1>|<arg2>|...\n
```

## Table des commandes

| Cmd | Direction | Description |
|-----|-----------|-------------|
| 1 | PAMI -> Jetson | Demande d'attribution d'ID |
| 2 | Jetson -> PAMI | Réponse : ID attribué |
| 3 | Jetson -> PAMI | Attribution des zones de dépôt |
| 4 | Robot -> Jetson | Notification de démarrage du match |
| 5 | Jetson -> Robot/PAMI | Données de vision (positions, caisses) |

---

## Messages reçus par le Jetson

### Commande 1 : Demande d'ID (PAMI -> Jetson)

Un PAMI envoie cette commande au démarrage pour obtenir un identifiant unique.

**Format :**
```
1\n
```

Pas d'arguments. Le Jetson répond automatiquement avec la commande 2.

---

### Commande 4 : Démarrage du match (Robot -> Jetson)

Le robot principal envoie cette commande quand le match démarre.

**Format :**
```
4|<couleur_equipe>\n
```

| Champ | Type | Valeurs | Description |
|-------|------|---------|-------------|
| `couleur_equipe` | string | `"B"` ou `"Y"` | Couleur de l'équipe (Bleu / Jaune) |

**Exemple :**
```
4|B\n
```

---

## Messages envoyés par le Jetson

### Commande 2 : Attribution d'ID (Jetson -> PAMI)

Réponse à une demande d'ID (commande 1). Chaque PAMI reçoit un ID unique.

**Format :**
```
2|<pami_id>\n
```

| Champ | Type | Description |
|-------|------|-------------|
| `pami_id` | int | Identifiant unique attribué au PAMI |

**Exemple :**
```
2|3\n
```

---

### Commande 3 : Attribution des dépôts (Jetson -> PAMI)

Envoyée une seule fois à T+90s (10 secondes avant la fin du match). Indique à chaque PAMI dans quelle zone il doit se rendre pour déposer ses matériaux.

**Format :**
```
3|<id_1>|<x_1>|<y_1>|<id_2>|<x_2>|<y_2>|...\n
```

Les champs se répètent par groupes de 3 pour chaque PAMI enregistré :

| Champ | Type | Description |
|-------|------|-------------|
| `id_N` | int | ID du PAMI (attribué par la commande 2) |
| `x_N` | float | Coordonnée X du dépôt en mètres (3 décimales) |
| `y_N` | float | Coordonnée Y du dépôt en mètres (3 décimales) |

**Exemple** (2 PAMIs) :
```
3|1|0.750|0.325|2|2.250|0.325\n
```

---

### Commande 5 : Données de vision (Jetson -> Robot/PAMI)

Envoyée en continu (~15 FPS) pendant toute la durée du match. Contient l'état complet de l'arène : positions des robots, des caisses dans les zones, et des caisses isolées.

**Format général :**
```
5|<enregistrements_R>|<enregistrements_Z>|<enregistrements_U>\n
```

Le message contient 3 types d'enregistrements, chacun introduit par un token :

#### Token `R` : Robot détecté

```
R|<robot_id>|<x>|<y>|<deg>|<vitesse>
```

| Champ | Type | Description |
|-------|------|-------------|
| `robot_id` | int | ID du marqueur ArUco (6 = allié, 1 = ennemi) |
| `x` | float | Position X en mètres (3 décimales) |
| `y` | float | Position Y en mètres (3 décimales) |
| `deg` | float | Orientation en degrés (1 décimale) |
| `vitesse` | float | Vitesse linéaire en m/s (2 décimales) |

#### Token `Z` : Caisse dans une zone

```
Z|<id_zone>|<couleur>|<x>|<y>|<deg>
```

| Champ | Type | Description |
|-------|------|-------------|
| `id_zone` | int | Identifiant de la zone |
| `couleur` | string | `"B"` (bleu) ou `"Y"` (jaune) |
| `x` | float | Position X en mètres (3 décimales) |
| `y` | float | Position Y en mètres (3 décimales) |
| `deg` | float | Orientation en degrés (1 décimale) |

#### Token `U` : Caisse hors zone (unzoned)

```
U|<x>|<y>|<deg>
```

| Champ | Type | Description |
|-------|------|-------------|
| `x` | float | Position X en mètres (3 décimales) |
| `y` | float | Position Y en mètres (3 décimales) |
| `deg` | float | Orientation en degrés (1 décimale) |

**Exemple complet :**
```
5|R|6|1.234|0.567|45.5|0.25|R|1|0.800|1.200|180.0|0.10|Z|3|B|2.300|0.400|0.0|Z|3|Y|2.350|0.450|12.5|U|1.500|1.800|90.0\n
```

Décomposition :
- Robot allié (ID 6) en (1.234, 0.567), cap 45.5 deg, vitesse 0.25 m/s
- Robot ennemi (ID 1) en (0.800, 1.200), cap 180.0 deg, vitesse 0.10 m/s
- Caisse bleue en zone 3 a (2.300, 0.400)
- Caisse jaune en zone 3 a (2.350, 0.450)
- Caisse isolée a (1.500, 1.800)

---

## Spécifications techniques

| Paramètre | Valeur |
|------------|--------|
| Encodage | UTF-8 ASCII |
| Séparateur de champs | `\|` (pipe) |
| Fin de message | `\n` (newline) |
| Débit UART | 115200 baud |
| Intervalle min d'envoi | 67 ms (1/15 s) |
| File d'envoi | Dernier message gagne (pas de queue FIFO) |

---

## Chronologie d'un match

```
T=0     PAMI envoie cmd 1 (demande ID)
        Jetson répond cmd 2 (attribution ID)
        ... (répété pour chaque PAMI)

        Robot envoie cmd 4 (démarrage match avec couleur)

T=0+    Jetson envoie cmd 5 en continu (~15 FPS)

T=90s   Jetson envoie cmd 3 (attribution dépôts, une seule fois)

T=100s  Fin du match, arrêt des envois
```

---

## Implémentation côté Robot / PAMI

### Réception d'un message

1. Lire les octets UART jusqu'à recevoir `\n`
2. Découper la ligne par `|`
3. Le premier élément est le numéro de commande (int)
4. Dispatcher vers le handler approprié selon le numéro

### Envoi d'un message

1. Construire la chaîne au format `<cmd>|<arg1>|<arg2>|...\n`
2. Encoder en UTF-8
3. Écrire sur le port UART

### Pseudo-code de réception (C/C++)

```cpp
// Buffer de réception
char rx_buffer[256];
int rx_pos = 0;

void on_uart_byte(uint8_t byte) {
    if (byte == '\n') {
        rx_buffer[rx_pos] = '\0';
        parse_message(rx_buffer);
        rx_pos = 0;
    } else if (rx_pos < sizeof(rx_buffer) - 1) {
        rx_buffer[rx_pos++] = byte;
    }
}

void parse_message(const char* msg) {
    // Découper par '|'
    // tokens[0] = numéro de commande
    int cmd = atoi(tokens[0]);

    switch (cmd) {
        case 2:  // Attribution ID
            my_pami_id = atoi(tokens[1]);
            break;
        case 3:  // Attribution dépôts
            // Parcourir par groupes de 3 : id, x, y
            for (int i = 1; i < nb_tokens; i += 3) {
                int id = atoi(tokens[i]);
                if (id == my_pami_id) {
                    depot_x = atof(tokens[i + 1]);
                    depot_y = atof(tokens[i + 2]);
                }
            }
            break;
        case 5:  // Données vision
            // Parcourir les tokens, dispatcher par R/Z/U
            for (int i = 1; i < nb_tokens; ) {
                if (strcmp(tokens[i], "R") == 0) {
                    int rid   = atoi(tokens[i + 1]);
                    float rx  = atof(tokens[i + 2]);
                    float ry  = atof(tokens[i + 3]);
                    float deg = atof(tokens[i + 4]);
                    float spd = atof(tokens[i + 5]);
                    // Traiter le robot...
                    i += 6;
                } else if (strcmp(tokens[i], "Z") == 0) {
                    int zone    = atoi(tokens[i + 1]);
                    char color  = tokens[i + 2][0];
                    float cx    = atof(tokens[i + 3]);
                    float cy    = atof(tokens[i + 4]);
                    float cdeg  = atof(tokens[i + 5]);
                    // Traiter la caisse zonée...
                    i += 6;
                } else if (strcmp(tokens[i], "U") == 0) {
                    float ux   = atof(tokens[i + 1]);
                    float uy   = atof(tokens[i + 2]);
                    float udeg = atof(tokens[i + 3]);
                    // Traiter la caisse isolée...
                    i += 4;
                } else {
                    i++;
                }
            }
            break;
    }
}
```

### Pseudo-code d'envoi (C/C++)

```cpp
// Demande d'ID (cmd 1)
void send_id_request() {
    uart_print("1\n");
}

// Démarrage match (cmd 4)
void send_match_start(const char* team_color) {
    char buf[16];
    snprintf(buf, sizeof(buf), "4|%s\n", team_color);
    uart_print(buf);
}
```
