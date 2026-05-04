# Tutoriel de reglage des 4 PID de la base roulante

Ce document donne une methode pratique pour trouver de bonnes valeurs de PID
sur la base roulante avec la page `PID Live`.

Les 4 PID ne corrigent pas tous la meme chose :

- `left_wheel_position` : asservit la position de la roue gauche. Entree en cm,
  sortie en PWM.
- `right_wheel_position` : asservit la position de la roue droite. Entree en cm,
  sortie en PWM.
- `linear_position` : transforme l'erreur de position avant/arriere du robot en
  consigne de deplacement pour les roues. Entree en cm, sortie en cm par cycle.
- `angular_position` : transforme l'erreur d'angle du robot en consigne
  differentielle pour les roues. Entree en rad, sortie en cm par cycle.

La chaine de controle est donc en cascade :

```text
erreur position robot
    -> PID linear_position / angular_position
    -> consigne de position roue gauche/droite
    -> PID left_wheel_position / right_wheel_position
    -> PWM moteurs
```

Il faut regler les PID de roues avant les PID de position. Sinon, le PID de
position va essayer de compenser un mauvais comportement moteur, ce qui donne
des valeurs instables et difficiles a reproduire.

## Avant de commencer

1. Poser le robot sur un support stable ou les roues peuvent tourner librement
   pour le premier test.
2. Verifier que les encodeurs ont le bon signe : quand le robot avance, la
   position mesuree des deux roues doit avancer dans le meme sens.
3. Verifier que le bouton d'arret d'urgence est accessible.
4. Ouvrir la page `PID Live`.
5. Commencer avec `ki = 0` et `kd = 0` sur les 4 PID.
6. Ne modifier qu'un seul coefficient a la fois.
7. Faire des essais courts : 20 cm en ligne droite ou 20 a 45 degres en
   rotation.

Dans le firmware actuel, les sorties sont limitees :

- PWM moteur : environ `[-240, 240]`.
- sortie `linear_position` : environ `[-0.8 cm/cycle, 0.8 cm/cycle]`.
- sortie `angular_position` : environ `[-0.8 cm/cycle, 0.8 cm/cycle]`.
- seuil mini moteur : si une PWM non nulle est trop faible, elle est remontee
  vers `MIN_PWM_WHEEL`.

Si une courbe de sortie reste collee a une limite, le PID est en saturation. Il
faut alors reduire le gain, reduire la consigne de test, ou verifier la mecanique
avant d'ajouter du `ki`.

## Comment lire les courbes

Sur chaque carte :

- `Consigne` : ce que le controleur demande.
- `Mesure` : ce qui est reellement mesure.
- `Erreur` : `consigne - mesure`.
- `Sortie` : correction envoyee par le PID.

Interpretation rapide :

| Comportement observe                   | Cause probable                                | Action                                           |
| -------------------------------------- | --------------------------------------------- | ------------------------------------------------ |
| La mesure monte trop lentement         | `kp` trop faible ou PWM mini trop haute/basse | Augmenter `kp`                                   |
| La mesure depasse puis revient         | `kp` trop fort ou pas assez de freinage       | Baisser `kp` ou ajouter un peu de `kd`           |
| Oscillations qui ne s'arretent pas     | `kp` trop fort, `ki` trop fort, frottements   | Baisser `kp`, remettre `ki = 0`, ajouter `kd`    |
| Erreur finale constante                | `kp` insuffisant, frottement, jeu mecanique   | Ajouter un petit `ki` apres avoir stabilise `kp` |
| Sortie collee a la limite              | Saturation                                    | Reduire la consigne ou le gain                   |
| Gauche et droite ne suivent pas pareil | Moteurs/roues asymetriques                    | Regler les PID gauche et droite separement       |

## Methode generale de reglage

La methode conseillee est :

1. `ki = 0`, `kd = 0`.
2. Augmenter `kp` jusqu'a ce que la reponse soit rapide mais pas oscillante.
3. Ajouter un peu de `kd` si la courbe depasse trop ou oscille.
4. Ajouter un tres petit `ki` uniquement s'il reste une erreur statique.
5. Refaire le meme test plusieurs fois et garder la valeur qui marche de facon
   repetable.

Ne cherchez pas la valeur qui marche une seule fois. Cherchez la valeur qui
marche avec batterie un peu plus faible, robot pose legerement differemment, et
sur plusieurs distances.

## Etape 1 - Regler les PID de roues

PID concernes :

- `left_wheel_position`
- `right_wheel_position`

Objectif : quand une roue recoit une consigne de position, sa mesure doit suivre
rapidement, sans gros depassement et sans oscillation.

Configuration de depart :

```json
"left_wheel_position":  { "kp": 20.0, "ki": 0.0, "kd": 0.0 },
"right_wheel_position": { "kp": 20.0, "ki": 0.0, "kd": 0.0 }
```

Si vos valeurs actuelles sont deja autour de `45`, vous pouvez repartir de
`45`, mais gardez `ki = 0` et `kd = 0` pour commencer.

Procedure :

1. Mettre `linear_position.kp` a une valeur faible a moyenne, par exemple
   `0.3` a `0.8`, juste pour generer des consignes de roues.
2. Mettre `angular_position.kp = 0` pour un test en ligne droite.
3. Commander une avance courte, par exemple 20 cm.
4. Observer `PID roue gauche` et `PID roue droite`.
5. Augmenter `kp` des roues tant que la mesure est trop lente.
6. Si la mesure depasse beaucoup ou oscille, reduire `kp` de 20 a 30 %.
7. Ajouter `kd` par petits pas si le depassement reste trop fort.
8. Ajouter `ki` seulement si la roue reste bloquee avec une erreur finale
   visible.

Ordres de grandeur utiles :

- `kp` roue trop bas : la roue suit lentement et le robot parait mou.
- `kp` roue trop haut : la roue vibre, oscille, ou alterne brutalement les PWM.
- `kd` roue utile : amortit le depassement.
- `ki` roue dangereux : il peut accumuler de l'erreur et provoquer un depart
  brutal apres blocage.

Critere d'acceptation :

- la courbe mesuree rejoint la consigne rapidement ;
- le depassement reste faible ;
- la sortie PWM ne tape pas constamment a `MAX_PWM` ;
- gauche et droite ont une reponse proche.

## Etape 2 - Regler le PID de position lineaire

PID concerne :

- `linear_position`

Objectif : le robot doit atteindre une distance cible sans osciller autour du
point final.

Avant cette etape, les PID de roues doivent deja etre corrects.

Configuration de depart :

```json
"linear_position": { "kp": 0.2, "ki": 0.0, "kd": 0.0 }
```

Procedure :

1. Garder `angular_position.kp = 0` ou tres faible pour isoler l'avance.
2. Commander une avance courte : 20 cm.
3. Observer `PID position lineaire`.
4. Augmenter `kp` jusqu'a ce que la mesure rejoigne la consigne assez vite.
5. Si le robot depasse la distance puis revient, reduire `kp` ou ajouter un peu
   de `kd`.
6. Tester ensuite 50 cm, puis 100 cm.
7. Ajouter un petit `ki` seulement si le robot s'arrete toujours trop court avec
   une erreur finale stable.

Signes typiques :

- Trop lent : augmenter `kp`.
- Depassement important : diminuer `kp` ou ajouter `kd`.
- Tremble autour de la consigne : `kp` trop haut, `kd` trop bas, ou deadband
  mecanique.
- Erreur finale stable : petit `ki`, puis verifier que le robot ne part pas en
  oscillation.

Critere d'acceptation :

- sur 20 cm, 50 cm et 100 cm, le robot s'arrete sans aller-retour visible ;
- la courbe rejoint la consigne avec peu de depassement ;
- la sortie `linear_position` ne reste pas saturee toute la trajectoire.

## Etape 3 - Regler le PID de position angulaire

PID concerne :

- `angular_position`

Objectif : le robot doit atteindre un angle cible sans osciller autour de
l'orientation finale.

Configuration de depart :

```json
"angular_position": { "kp": 0.5, "ki": 0.0, "kd": 0.0 }
```

Procedure :

1. Commander une petite rotation : 20 degres.
2. Observer `PID position angulaire`.
3. Augmenter `kp` jusqu'a obtenir une rotation franche.
4. Si le robot depasse l'angle puis revient, reduire `kp` ou ajouter `kd`.
5. Tester ensuite 45 degres, 90 degres, puis 180 degres.
6. Ajouter `ki` seulement si l'angle final reste systematiquement decale.

Signes typiques :

- Rotation molle : `kp` trop faible.
- Depassement angulaire : `kp` trop fort ou manque de `kd`.
- Oscillation droite/gauche autour de l'angle : `kp` ou `ki` trop haut.
- Le robot avance pendant la rotation : asymetrie roue gauche/droite ou erreur
  mecanique a corriger avant d'augmenter les gains.

Critere d'acceptation :

- le robot atteint 20, 45 et 90 degres proprement ;
- pas d'oscillation visible autour de l'angle final ;
- la position XY derive peu pendant une rotation pure.

## Etape 4 - Tester les 4 PID ensemble

Une fois les PID individuels acceptables :

1. Commander 50 cm en ligne droite.
2. Commander 90 degres.
3. Commander un point combine : avance + angle final.
4. Observer les 4 cartes `PID Live`.

Ce qu'il faut verifier :

- les roues suivent bien leurs consignes ;
- le PID lineaire ne cree pas d'oscillation longue ;
- le PID angulaire ne corrige pas en permanence pendant une ligne droite ;
- les sorties PWM ne restent pas saturees.

Si le comportement devient mauvais seulement quand tout est actif, reduisez
d'abord les PID de position, pas les PID de roues. Les PID de roues doivent
rester les plus rapides et les plus propres possible ; les PID de position
doivent piloter doucement cette couche interne.

## Comment choisir les increments

Pour aller vite sans perdre le controle :

- Si la reponse est beaucoup trop lente : multiplier `kp` par 2.
- Si la reponse est presque bonne : augmenter `kp` de 10 a 20 %.
- Si ca oscille : reduire `kp` de 20 a 30 %.
- Pour `kd` : commencer tres petit et augmenter progressivement.
- Pour `ki` : commencer 10 a 100 fois plus petit que `kp` selon l'unite et
  augmenter lentement.

Regle simple : si ajouter `ki` empire le comportement transitoire, remettez
`ki = 0` et corrigez d'abord `kp`/`kd`.

## Exemple de feuille de mesures

Copier ce tableau a chaque session de reglage.

| Date | PID         |   kp |   ki |   kd | Test   | Resultat | Decision |
| ---- | ----------- | ---: | ---: | ---: | ------ | -------- | -------- |
|      | roue gauche |      |      |      | 20 cm  |          |          |
|      | roue droite |      |      |      | 20 cm  |          |          |
|      | lineaire    |      |      |      | 50 cm  |          |          |
|      | angulaire   |      |      |      | 90 deg |          |          |

## Ou sauvegarder les valeurs

La page WebUI envoie les valeurs au robot en direct. Pour les conserver au
redemarrage, reporter les valeurs validees dans `config.json`, section :

```json
"rolling_basis": {
  "pids": {
    "linear_position": { "kp": 0.0, "ki": 0.0, "kd": 0.0 },
    "angular_position": { "kp": 0.0, "ki": 0.0, "kd": 0.0 },
    "left_wheel_position": { "kp": 45.0, "ki": 0.0, "kd": 0.0 },
    "right_wheel_position": { "kp": 45.0, "ki": 0.0, "kd": 0.0 }
  }
}
```

Si le firmware Teensy contient aussi des valeurs par defaut dans
`robot1/teensy_moteur/include/config.h`, gardez-les coherentes avec la
configuration Raspberry pour eviter un comportement different apres reset.

## Regles de securite

- Ne jamais tester une nouvelle valeur forte directement sur une grande
  distance.
- Ne pas ajouter `ki` pour regler un robot qui oscille deja.
- Ne pas compenser une roue qui glisse ou un encodeur inverse avec le PID.
- Si la sortie PWM est saturee mais la mesure ne bouge pas, arreter le test :
  c'est probablement mecanique ou electrique.
- Toujours valider sur plusieurs repetitions avant de garder une valeur.
