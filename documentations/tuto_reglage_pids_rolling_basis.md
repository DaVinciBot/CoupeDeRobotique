# Tutoriel de reglage des PID de la base roulante

Ce tutoriel decrit le reglage des 4 PID utilises par la Teensy moteur. Il est
base sur le fonctionnement actuel de
`robot1/teensy_moteur/lib/rolling_basis/src/rolling_basis.cpp`.

## Architecture actuelle

La base roulante utilise deux couches d'asservissement en cascade.

```text
position cible robot
    -> erreur lineaire et erreur angulaire
    -> PID linear_position et angular_position
    -> pas de consigne roue gauche/droite, en cm par cycle
    -> PID left_wheel_position et right_wheel_position
    -> PWM moteurs
```

Les 4 PID n'ont pas le meme role :

- `linear_position` : convertit l'erreur avant/arriere du robot en pas de
  consigne commun aux deux roues. Entree en cm, sortie en cm par cycle.
- `angular_position` : convertit l'erreur d'angle en pas differentiel.
  Entree en rad, sortie en cm par cycle.
- `left_wheel_position` : asservit la position de la roue gauche.
  Entree en cm, sortie en PWM.
- `right_wheel_position` : asservit la position de la roue droite.
  Entree en cm, sortie en PWM.

Dans `handle()`, la Teensy fait exactement ceci :

```text
linear_error  = projection de l'erreur cible sur l'axe avant du robot
angular_error = target_theta - theta, normalise entre -pi et pi

linear_step  = PID(linear_position).compute(linear_error)
angular_step = PID(angular_position).compute(angular_error)

left_wheel_target_cm  += linear_step - angular_step
right_wheel_target_cm += linear_step + angular_step

left_pwm  = PID(left_wheel_position).compute(left_target - left_position)
right_pwm = PID(right_wheel_position).compute(right_target - right_position)
```

Point important : `linear_position` et `angular_position` ne commandent pas
directement les moteurs. Ils font seulement avancer les consignes de roues.
Les PID de roues sont la couche interne qui transforme ces consignes en PWM.

## Limites du firmware

Les limites actuelles sont codees dans `rolling_basis.cpp` :

- PWM moteur : `[-240, 240]`.
- `linear_step` : `[-0.8 cm/cycle, 0.8 cm/cycle]`.
- `angular_step` : `[-0.8 cm/cycle, 0.8 cm/cycle]`.
- Ecart max entre consigne roue et position roue mesuree :
  `WHEEL_TARGET_MAX_ERROR_CM = 10.0`.

Si une sortie reste collee a une limite, le PID est en saturation. Dans ce cas,
il faut reduire le gain ou la consigne de test avant d'ajouter du `ki`.

## Ce que le mode direct_pwm teste

`direct_pwm` ne passe pas par les 4 PID. Il active `manual_pwm_active`, envoie
directement les PWM aux moteurs pendant la duree demandee, puis remet les
consignes de roues sur la position courante et reset les PID.

Utilisez `direct_pwm` uniquement pour verifier :

- le sens des moteurs ;
- le sens des encodeurs ;
- l'equilibre mecanique gauche/droite ;
- les frottements, roues encodeuses et drivers.

Ne reglez pas les PID tant que `direct_pwm` identique gauche/droite ne donne pas
un comportement mecanique sain. Si une roue va beaucoup plus vite en PWM direct,
c'est un probleme mecanique, electrique ou de configuration encodeur, pas un
probleme de PID.

## Avant de regler

1. Poser le robot sur un support stable pour les premiers essais.
2. Verifier avec `direct_pwm` que les deux roues tournent dans le bon sens.
3. Verifier que les ticks gauche et droit augmentent quand le robot avance.
4. Verifier que `dt=LEFT/RIGHT` est du meme ordre avec PWM identiques.
5. Ouvrir la page `PID Live`.
6. Modifier un seul coefficient a la fois.
7. Faire des tests courts : 10 a 20 cm ou 20 a 45 degres.

La Teensy envoie aussi une ligne de debug utile :

```text
RB e=lin/ang step=lin/ang ew=left/right pwm=left/right dt=left/right ticks=left/right
```

Champs utiles :

- `e` : erreurs robot lineaire et angulaire, multipliees par 100.
- `step` : sorties `linear_position` et `angular_position`, multipliees par 100.
- `ew` : erreurs de position roues, multipliees par 100.
- `pwm` : PWM gauche/droite envoyees aux moteurs.
- `dt` : delta ticks gauche/droite sur le dernier cycle d'odometrie.
- `ticks` : ticks cumules gauche/droite.

## Lire les courbes PID Live

Sur chaque carte :

- `Consigne` : ce que la couche superieure demande.
- `Mesure` : ce qui est mesure.
- `Erreur` : `consigne - mesure`.
- `Sortie` : sortie du PID.

Interpretation rapide :

| Observation                         | Cause probable                           | Action                                           |
| ----------------------------------- | ---------------------------------------- | ------------------------------------------------ |
| Mesure trop lente                   | `kp` trop faible ou mecanique dure       | Augmenter `kp` doucement                         |
| Depassement puis retour             | `kp` trop fort ou manque d'amortissement | Baisser `kp` ou ajouter un peu de `kd`           |
| Oscillation continue                | `kp`/`ki` trop fort ou jeu mecanique     | Remettre `ki = 0`, baisser `kp`, tester `kd`     |
| Erreur finale stable                | Frottement ou `kp` insuffisant           | Stabiliser `kp`, puis ajouter tres peu de `ki`   |
| Sortie saturee                      | Consigne ou gain trop fort               | Reduire la consigne ou le gain                   |
| Roue gauche/droite tres differentes | Mecanique ou PID roue asymetrique        | Valider en `direct_pwm`, puis regler chaque roue |

## Ordre de reglage recommande

L'ordre important est :

1. Mecanique et encodeurs avec `direct_pwm`.
2. PID de roues : `left_wheel_position`, `right_wheel_position`.
3. PID de position lineaire : `linear_position`.
4. PID de position angulaire : `angular_position`.
5. Test combine.

Si les PID de roues sont mauvais, les PID de position vont accumuler des
consignes de roues que la mecanique ne suit pas. Le resultat devient difficile a
interpreter.

## Etape 1 - Verifier la mecanique

Faire roues levees :

1. Envoyer `direct_pwm` avec `left_pwm = 80`, `right_pwm = 80`,
   `duration_ms = 1000`.
2. Regarder `dt=LEFT/RIGHT` et `ticks=LEFT/RIGHT`.
3. Refaire avec `left_pwm = -80`, `right_pwm = -80`.

Resultat attendu :

- les deux roues tournent dans le meme sens logique ;
- les deux compteurs avancent dans le bon sens ;
- les deltas ticks sont proches ;
- aucune roue encodeuse ne glisse.

Si ce test echoue, corriger avant de toucher aux PID.

## Etape 2 - Regler les PID de roues

PID concernes :

- `left_wheel_position`
- `right_wheel_position`

Objectif : les positions de roues doivent suivre leurs consignes vite, sans
oscillation et sans PWM constamment saturee.

Configuration de depart prudente :

```json
"left_wheel_position":  { "kp": 20.0, "ki": 0.0, "kd": 0.0 },
"right_wheel_position": { "kp": 20.0, "ki": 0.0, "kd": 0.0 }
```

Pour generer des consignes de roues, il faut un petit PID de position :

```json
"linear_position":  { "kp": 0.2, "ki": 0.0, "kd": 0.0 },
"angular_position": { "kp": 0.0, "ki": 0.0, "kd": 0.0 }
```

Procedure :

1. Commander une avance courte, par exemple 10 ou 20 cm.
2. Observer les courbes `left_wheel_position` et `right_wheel_position`.
3. Augmenter `kp` roue par roue tant que la mesure suit trop lentement.
4. Si la roue depasse ou oscille, reduire `kp` de 20 a 30 %.
5. Ajouter un peu de `kd` si le depassement reste trop fort.
6. Ajouter `ki` seulement si l'erreur finale reste visible et stable.

Critere d'acceptation :

- la mesure rejoint la consigne sans oscillation durable ;
- les PWM ne tapent pas constamment `240` ;
- les deux roues ont des reponses proches ;
- un test repete donne le meme resultat.

## Etape 3 - Regler `linear_position`

PID concerne :

- `linear_position`

Objectif : pour une consigne de deplacement droit, le robot atteint la distance
sans aller-retour visible autour du point final.

Avant cette etape, garder les PID de roues valides. Mettre temporairement :

```json
"angular_position": { "kp": 0.0, "ki": 0.0, "kd": 0.0 }
```

Configuration de depart :

```json
"linear_position": { "kp": 0.2, "ki": 0.0, "kd": 0.0 }
```

Procedure :

1. Commander 20 cm.
2. Observer `linear_position` et les deux PID de roues.
3. Augmenter `kp` si le robot avance trop mollement.
4. Reduire `kp` si `step` reste souvent a `0.8` ou si le robot depasse.
5. Ajouter un peu de `kd` si l'approche finale oscille.
6. Ajouter `ki` seulement si le robot finit toujours trop court, de facon
   repetable.
7. Refaire sur 50 cm puis 100 cm.

Attention : `linear_error` est la projection de l'erreur cible sur l'axe avant
du robot. Une erreur laterale n'est pas directement corrigee par ce PID. Pour
une trajectoire propre, l'orientation et l'odometrie doivent deja etre bonnes.

Critere d'acceptation :

- le robot rejoint 20, 50 et 100 cm sans oscillation visible ;
- `linear_step` ne reste pas sature tout le mouvement ;
- les erreurs de roues restent bornees et propres.

## Etape 4 - Regler `angular_position`

PID concerne :

- `angular_position`

Objectif : le robot atteint l'angle cible sans osciller droite/gauche autour de
l'orientation finale.

Configuration de depart :

```json
"angular_position": { "kp": 0.2, "ki": 0.0, "kd": 0.0 }
```

Procedure :

1. Commander 20 degres.
2. Observer `angular_position`, puis les consignes de roues.
3. Augmenter `kp` jusqu'a obtenir une rotation franche.
4. Reduire `kp` si `angular_step` sature souvent a `0.8` ou si le robot depasse.
5. Ajouter un peu de `kd` si l'angle final oscille.
6. Ajouter `ki` seulement si l'angle final reste decale de facon repetable.
7. Tester 45 degres, 90 degres, puis 180 degres.

Pendant une rotation pure, le firmware fait :

```text
left_wheel_target_cm  += -angular_step
right_wheel_target_cm +=  angular_step
```

Si le robot avance pendant une rotation pure, verifier d'abord les roues,
l'entraxe, les diametres et l'equilibre des PID de roues.

Critere d'acceptation :

- 20, 45 et 90 degres sont atteints proprement ;
- peu ou pas d'oscillation finale ;
- la position XY derive peu pendant une rotation pure.

## Etape 5 - Tester les 4 PID ensemble

Une fois les couches individuelles reglees :

1. Commander 50 cm en ligne droite.
2. Commander 90 degres.
3. Commander une cible combinee : avance + angle final.
4. Observer les 4 cartes `PID Live` et la ligne `RB`.

Ce qu'il faut verifier :

- les roues suivent leurs consignes ;
- `linear_step` et `angular_step` ne restent pas bloques en saturation ;
- les PWM ne restent pas constamment a `240` ;
- le robot ne corrige pas l'angle en permanence pendant une ligne droite ;
- les essais sont repetables.

Si le comportement devient mauvais seulement quand tout est actif, reduire
d'abord `linear_position` et `angular_position`. Les PID de roues doivent rester
la couche rapide et propre ; les PID de position doivent leur envoyer des
consignes progressives.

## Increments pratiques

Regle simple :

- Reponse beaucoup trop lente : multiplier `kp` par 2.
- Reponse presque correcte : augmenter `kp` de 10 a 20 %.
- Oscillation : reduire `kp` de 20 a 30 %.
- Depassement : ajouter un peu de `kd` ou reduire `kp`.
- Erreur finale stable : ajouter un tres petit `ki`.

Toujours remettre `ki = 0` si le systeme commence a osciller ou a partir
brutalement apres un blocage.

## Sauvegarde des valeurs

La WebUI envoie les PID en direct a la Raspberry, qui les transmet a la Teensy.
Pour conserver les valeurs au redemarrage, les reporter dans `config.json` :

```json
"rolling_basis": {
  "pids": {
    "linear_position": { "kp": 0.0, "ki": 0.0, "kd": 0.0 },
    "angular_position": { "kp": 0.0, "ki": 0.0, "kd": 0.0 },
    "left_wheel_position": { "kp": 70.0, "ki": 9.0, "kd": 4.0 },
    "right_wheel_position": { "kp": 55.0, "ki": 3.0, "kd": 2.0 }
  }
}
```

Les valeurs dans `robot1/teensy_moteur/include/config.h` sont seulement les
valeurs par defaut au demarrage firmware. En fonctionnement normal, le brain
Raspberry appelle `initialize_pids()` et remplace ces valeurs avec celles de
`config.json`.

## Feuille de mesures

| Date | PID         |   kp |   ki |   kd | Test   | Resultat | Decision |
| ---- | ----------- | ---: | ---: | ---: | ------ | -------- | -------- |
|      | roue gauche |      |      |      | 20 cm  |          |          |
|      | roue droite |      |      |      | 20 cm  |          |          |
|      | lineaire    |      |      |      | 50 cm  |          |          |
|      | angulaire   |      |      |      | 90 deg |          |          |

## Regles de securite

- Ne jamais tester une grosse valeur directement sur une grande distance.
- Ne pas ajouter `ki` sur un systeme qui oscille deja.
- Ne pas compenser un probleme mecanique ou un encodeur mal configure avec le
  PID.
- Si la PWM sature mais la roue ne bouge pas, arreter le test.
- Toujours valider une valeur sur plusieurs repetitions.
