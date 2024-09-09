# README - Coupe de France de Robotique - DAVINCI Bot (ESILV)

Bienvenue dans le repository GitHub de la **Coupe de France de Robotique**, un événement national où des équipes de passionnés conçoivent et construisent des robots autonomes. Ces derniers s’affrontent au cours de matchs d’un temps déterminé durant lequel ils ont pour mission d’accomplir un maximum de tâches. 

## Description du projet

Ce repository contient l'ensemble des codes et scripts nécessaires au développement du robot de DAVINCI Bot pour la **Coupe de France de Robotique**. Le robot est conçu pour être entièrement autonome et réaliser des actions spécifiques lors des épreuves, telles que la détection d'obstacles, la navigation précise et l'interaction avec des objets.

Notre architecture robotique repose principalement sur une **Raspberry Pi** qui sert de maître pour coordonner les différentes tâches, et des microcontrôleurs **Teensy** qui gèrent les sous-systèmes (moteurs, capteurs, actionneurs ).

## Architecture générale

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
- **C/C++** : Utilisé pour la programmation des Teensy (contrôle bas-niveau des moteurs et capteurs).
- **Lidar/roues** odomètres pour la perception de l’environnement.
