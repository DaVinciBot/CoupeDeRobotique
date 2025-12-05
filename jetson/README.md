N'installez surtout pas opencv avec pip ! la version build sur pip ne contient pas CUDA (esssentiel pour le bon fonctionnement sur jetson).

A la place il faut build et installer opencv depuis le code source directement sur la jetson avec le module cuda (y a plein de repo github qui le font) (et oui ça prend 4h à compiler).

Installez opencv 4.5.1 pour avoir la meilleur comptabilité avec le code !
