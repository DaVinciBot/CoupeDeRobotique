# Diagnostic encodeurs et reset au boot (Rolling Basis)

## Objectif
- Repartir a chaque boot Teensy comme si le firmware venait d'etre flashe.
- Diagnostiquer les encodeurs pas a pas avec actions correctives.
- Eviter les cas ou les ticks restent toujours negatifs ou s'accumulent.

## A. Reset complet au demarrage
Objectif: ticks, odometrie et PID a zero des le boot.

Etapes:
1. Demarrer la Teensy sans commande moteur.
2. Verifier dans les logs serie:
   - ticks gauche = 0 et ticks droit = 0
   - odometrie = (0, 0, 0)
   - PWM = 0
3. Lancer une commande nulle, attendre 1 seconde, verifier que les ticks restent stables.

Si ca ne marche pas:
- Les ticks changent au boot:
  - Verifier que les interruptions encodeurs ne s'activent pas avant la fin de l'init.
  - Verifier l'etat logique des broches (pull-up / pull-down).
- Les ticks ne reviennent jamais a zero:
  - Ajouter un reset explicite des ticks et last_ticks a l'initialisation.
  - Ajouter un reset au message SET_ODOMETRIE si vous l'utilisez comme reinit.

## B. Verification electrique des encodeurs
Materiel: multimètre, ou oscilloscope si disponible.

Etapes:
1. Verifier l'alimentation encodeur (VCC et GND).
2. Mesurer le niveau logique sur ENC_A et ENC_B au repos.
3. Tourner la roue a la main et observer si ENC_A et ENC_B changent.

Si ca ne marche pas:
- Un canal reste toujours HIGH ou LOW:
  - Verifier cablage du canal.
  - Verifier la broche Teensy utilisee.
  - Verifier presence de pull-up/pull-down.
  - Tester un autre canal pour exclure un capteur HS.
- Aucun canal ne change:
  - Verifier l'alimentation encodeur.
  - Verifier la masse commune.
  - Verifier la connectique (coupure, inversion, faux contact).

## C. Sens de comptage des ticks
Objectif: roue en avant => ticks positifs, roue en arriere => ticks negatifs.

Etapes:
1. Couper PWM (ou commande 0).
2. Tourner la roue vers l'avant et noter le signe des ticks.
3. Tourner la roue vers l'arriere et verifier l'inversion du signe.

Si ca ne marche pas:
- Ticks toujours negatifs ou toujours positifs:
  - Inverser physiquement ENC_A et ENC_B.
  - Si pas possible, inverser la logique dans l'ISR (swap ++ et --).
- Ticks incoherents ou bruites:
  - Verifier la longueur des cables et l'absence de bruit.
  - Ajouter un filtrage ou verifier les fronts sur l'oscillo.

## D. Symptomes et actions rapides
- Ticks s'accumulent apres reboot:
  - Reset explicite des ticks au boot + reset odometrie.
- Ticks toujours negatifs quel que soit le sens:
  - ENC_B fige ou inversion A/B.
- Un seul cote bouge en tick:
  - Encoder de l'autre cote mal alimente ou mal branche.
- Rotation sur place a consigne lineaire:
  - Encoder inversé ou moteur inversé sur un cote.

## E. Checklist finale
- Ticks a zero au boot.
- ENC_A et ENC_B varient quand on tourne a la main.
- Roue en avant => ticks positifs sur les deux roues.
- Consigne nulle => PWM = 0 et ticks stables.
