
![bannerDVB](https://github.com/user-attachments/assets/55c6bd16-f4f7-49e6-8cbc-06bbaf224000)

# Présentation

> Bienvenue sur le dépot de l'équipe DaVinciBot (ESILV)

La Coupe de robotique regroupe près de 200 équipes constituées de clubs d'amateurs, d'écoles d'ingénieurs, d'IUT, d'universités, de quelques lycées ou de toute autre structure voulant participer à ce concours.

Il s'agit d'un défi ludique, scientifique et technique où se rencontrent des robots autonomes réalisés par des équipes (de passionnés ou ayant des projets éducatifs vers les jeunes). Les robots des différentes équipes s'opposent dans de véritables matchs technologiques pendant 90 secondes. Les règles du jeu varient chaque année, ce qui impose la construction de nouveaux robots.

## Description du projet

Ce dépot contient l'ensemble des codes et scripts nécessaires au développement du robot de DaVinciBot pour la **Coupe de France de Robotique**. Le robot est conçu pour être entièrement autonome et réaliser des actions spécifiques lors des épreuves, telles que la détection d'obstacles, la navigation précise et l'interaction avec des objets.

L'architecture de notre robot repose principalement sur une **Raspberry Pi** qui sert de maître pour coordonner les différentes tâches, et des microcontrôleurs **Teensy** qui gèrent les sous-systèmes (moteurs, capteurs, actionneurs ).

## Architecture générale

![Untitled](https://github.com/user-attachments/assets/a51fdd88-af9e-40bd-830a-1d8a78f09035)


L'architecture du robot s'organise autour de deux niveaux principaux de contrôle :

1. **Raspberry Pi (Contrôleur principal)** :
    - Coordonne l'ensemble du robot, prend les décisions globales et gère la communication avec les capteurs et les actionneurs.
    - Communique avec les Teensy pour déléguer les tâches de bas niveau.
2. **Teensy (Contrôleur des sous-systèmes)** :
    - Gestion des actionneurs et des capteurs (moteurs, roues odomètres, LIDAR, etc.).
    - Exécution des algorithmes de contrôle en temps réel (PID, gestion des moteurs, etc.).

## Technologies et langages utilisés

Ce projet utilise plusieurs technologies et langages pour assurer le bon fonctionnement du robot :

- **Python** : Langage principal pour la programmation de la Raspberry Pi (contrôle global et prise de décision).
- **C/C++** : Utilisé pour la programmation des Teensy (asservissements des moteurs et contrôle des capteurs).
- **Lidar/roues odométriques** : Perception de l’environnement.
