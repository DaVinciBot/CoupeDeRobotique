## Brain

L'utilisation de Brain est essentielle au fonctionnement global du robot, car elle gère l'exécution de toutes les tâches. Ce module s'appuie largement sur la bibliothèque Asyncio de Python, ce qui permet de gérer l'exécution de code asynchrone ainsi que le multiprocessing.

Avantages :

- Gestion des erreurs
- Isolation des exécutions
- Journaux détaillés des exécutions des tâches
- Toutes les méthodes partagent les attributs de la classe via le self, assurant ainsi une intercommunication transparente

## Task

Pour transformer une méthode du Brain en tâche et ainsi pouvoir contrôler son exécution comme on veut, il suffit d’utiliser le décorateur `Brain.task()`.

```python
@Brain.task(...)
async def ma_methode(self):
	pass
```

Ce décorateur comprend 2 paramètres obligatoires à compléter : `process` et `run_on_start`. Ils ont été rendus obligatoires afin d’améliorer la clarté du code ; cela permet de bien voir quelle méthode s’exécute dans un processus secondaire et quelles méthodes démarrent au lancement du Brain.

Nous allons à présent voir toutes les configurations possibles de ce décorateur et les possibilités qu’il offre.

### One-Shot

Pour toutes les tâches qui n’ont besoin d’être exécutées qu’une seule fois, on va décorer la méthode de sorte à créer ce qu’on appelle une “one_shot_task”.

```python
@Brain.task(process=[True / False], run_on_start=[True / False])
async def methode_one_shot(self):
  pass
```

### Routine

Pour toutes les tâches qui s’exécutent à l’infini, il est possible de préciser à notre tâche, via le décorateur, un `refresh_rate`. Ce paramètre correspond à la fréquence d’exécution de la méthode. Elle sera alors appelée à l’infini (même si elle plante) avec une pause de la durée du `refresh_rate`renseigné.

```python
@Brain.task(process=[True / False], run_on_start=[True / False], refresh_rate=0.5)
async def methode_routine(self):
  pass
```

Ici, cette méthode sera donc exécutée à l’infini avec une pause de 0.5s entre chaque exécution.

### Timout et Task

Il est possible d’ajouter à notre task (routine ou one_shot) un timeout au bout duquel la tâche sera interrompue. Cela est utile notamment lorsqu’on définit des phases de jeu, par exemple. Cela permet d’associer une phase de jeu à une durée maximale précise et, en cas de dépassement de cette durée, la phase est interrompue, laissant ainsi la suite de la stratégie de jeu prendre le relais.

Cette fonctionnalité est applicable aux routines et aux one_shot !

```python
# Routine timée
@Brain.task(process=[True / False], run_on_start=[True / False], refresh_rate=[durée en seconde], timeout=10)
async def methode_timed_routine(self):
  pass
  
# One_shot timée
@Brain.task(process=[True / False], run_on_start=[True / False], timeout=10)
async def methode_timed_one_shot(self):
  pass
```

Ici, ces deux méthodes s’interrompront quoi qu’il arrive au bout de 10 secondes. 

> Gestion des outputs
> 

Les méthodes, une fois exécutées, retournent un code d’exécution afin d’indiquer comment la tâche s’est terminée. Voici les états possibles :

```python
class ExecutionStates(IntEnum):
    CORRECTLY = 0 # Exécution normale: pas de timeoutni de crash
    TIMEOUT = 1 # La task s'est interrompue car elle a dépassé le timeout
    ERROR_OCCURRED = 2 # La task s'est interrompue car une erreur est survenue (crash de la fonction)
```

### Multiprocessing

l est possible d'exécuter une task (routine ou one_shot) dans un autre processus afin de mieux répartir la charge CPU. Cette fonctionnalité est particulièrement utile pour les tâches gourmandes en ressources, qui pourraient autrement bloquer excessivement le temps CPU du processus principal. La principale difficulté du multiprocessing réside dans la communication d'objets Python entre processus. Dans le cadre du Brain, cette communication est entièrement transparente. Lorsqu'un processus est lancé, une copie des attributs du Brain est créée et partagée entre tous les processus. Lorsque l'un de ses attributs est modifié (que ce soit main_process → second_process ou second_process → main_process), le Brain se charge automatiquement de synchroniser cette modification de la copie vers l'instance initiale. Cette copie partagée est un dictionnaire proxy, un type issu de la classe Manager de la librairie multiprocessing.

> Limitation de la communication inter-process
> 

La principale restriction quant à l’utilisation de cette fonctionnalité est le type des attributs de la classe pouvant être partagés au travers du dictionnaire proxy. En effet, il faut que l’attribut soit sérialisable ! Les types sérialisables supportés pour le moment sont :

```python
serialized_types = (
    Logger,
    int,
    float,
    str,
    list,
    set,
    dict,
    tuple,
    OrientedPoint,
    Point,
    type(None),
)
```

Il est donc compliqué de passer en attribut partagé un objet complexe à utiliser dans un autre processus. Pour contourner ce problème, il est possible d’instancier directement dans le processus l’objet en question. Prenons l’exemple de l’utilisation d’une caméra. Son utilisation est gourmande en ressources, donc idéale pour du multiprocessing. Le problème est que l’objet caméra n’est pas sérialisable ! On va donc récupérer les éléments de configuration de celle-ci via un attribut, puis l’instancier directement dans le processus.

```python
@Brain.task(process=True, run_on_start=[True / False])
def camera_in_other_process(self):
    camera = Camera(
        res_w=self.config.CAMERA_RESOLUTION[0],
        res_h=self.config.CAMERA_RESOLUTION[1],
        captures_path=self.config.CAMERA_SAVE_PATH,
        undistorted_coefficients_path=self.config.CAMERA_COEFFICIENTS_PATH,
    )
```

> Attention un process sera synchrone ! Pensez à mettre `def` et non`async def` !
> 

On remarque que la configuration est directement accessible via`self`(qui accède en réalité à la copie partagée du Brain). Une fois instanciée, nous utiliserons notre caméra pour capturer des images et y appliquer un traitement. Cependant, cela pose un nouveau problème : le traitement doit s'exécuter en continu, nécessitant donc la création d'une routine. Or, il n'est pas possible de créer une routine à l'intérieur d'une tâche, surtout si celle-ci est exécutée dans un processus séparé. Pour répondre à ce besoin, une option appelée `define_loop_later` est disponible. Elle permet de définir une tâche en tant que routine, tout en ayant une partie qui s'exécute une seule fois (comme la création de l'objet caméra).

```python
@Brain.task(process=True, run_on_start=[True / False], refresh_rate=0.1, define_loop_later=True)
def camera_in_other_process(self):
    camera = Camera(
        res_w=self.config.CAMERA_RESOLUTION[0],
        res_h=self.config.CAMERA_RESOLUTION[1],
        captures_path=self.config.CAMERA_SAVE_PATH,
        undistorted_coefficients_path=self.config.CAMERA_COEFFICIENTS_PATH,
    )
    
    # ---Loop--- #
    camera.capture()
    # ... traitement d'image ... #
```

> Il faut penser à préciser notre `refresh_rate` car notre task est ici une routine ! (bien qu’elle ait une partie qui ne s’exécute qu’une seule fois)
→ On peut évidemment profiter de l’exécution hors du process principal pour diminuer fortement le `refresh_rate` afin d’avoir une routine qui s’exécute à haute fréquence.
> 

Ici, on instancie notre caméra, puis on l’utilise pour prendre des photos et leur appliquer un traitement. Ce qui sépare la partie one_shot de la routine est le commentaire `# ---Loop--- #`. Oui, oui, c’est bien ce simple commentaire qui va modifier l’exécution du code. (Vive la méta-programmation eheh !). En réalité, ce code très simple et léger d’utilisation revient à faire ceci :

```python
@Brain.task(process=False, run_on_start=False)
async def one_shot_part(self):
    return Camera(
        res_w=self.config.CAMERA_RESOLUTION[0],
        res_h=self.config.CAMERA_RESOLUTION[1],
        captures_path=self.config.CAMERA_SAVE_PATH,
        undistorted_coefficients_path=self.config.CAMERA_COEFFICIENTS_PATH,
    )
    
@Brain.task(process=False, run_on_start=False, refresh_rate=0.1)
async def routine_part(self, camera):
    camera.capture()
    # ... traitement d'image ... #
    
@Brain.task(process=True, run_on_start=[True / False])
def camera_in_other_process(self):
		# Initialisation des objets
    camera = asyncio.run(self.one_shot_part())
    # Exécution infini 
    asyncio.run(self.routine_part())
```

Il est également possible de définir le marker de la routine soit même :

```python
@Brain.task(process=True, run_on_start=[True / False], refresh_rate=0.1, define_loop_later=True, start_loop_marker="#- My Custom Loop Marker -#")
def camera_in_other_process(self):
    camera = Camera(
        res_w=self.config.CAMERA_RESOLUTION[0],
        res_h=self.config.CAMERA_RESOLUTION[1],
        captures_path=self.config.CAMERA_SAVE_PATH,
        undistorted_coefficients_path=self.config.CAMERA_COEFFICIENTS_PATH,
    )
    
    #- My Custom Loop Marker -#
    camera.capture()
    # ... traitement d'image ... #
```

## Points de vigilances, limitations et précisions

Bien que l’utilisation du Brain est bien pratique, certains points sont à surveiller et à bien comprendre pour en tirer son plein potentiel.

### Dynamic init

### Création automatique des attributs

Afin d’alléger le code de l’`__init__`qui consiste essentiellement à faire ça:

```python
def __init__(
        self,
        logger: Logger,
        obj1: type_obj1,
        obj2: type_obj2,
        obj3: type_obj3,
    ) -> None:
    self.logger = logger
    self.obj1 = obj1 
    self.obj2 = obj2
    self.obj3 = obj3 
    ...
```

L’`__init__` est rendu dynamique: il le fait automatiquement, il suffit donc d’écrire: 

```python
def __init__(
        self,
        logger: Logger,
        obj1: type_obj1,
        obj2: type_obj2,
        obj3: type_obj3,
    ) -> None:
    super().__init__(logger, self)
```

### Création d’attributs de classe

Si l’on veut créer des attributs de classe dans l’`__init__` et que l’on souhaite qu’ils soient partagé entre les process, il faut les définir AVANT `super().__init__(logger, self)` . Dans le cas contraire ils seront disponibles uniquement dans le main-porcess.

```python
def __init__(
        self,
        logger: Logger,
        obj1: type_obj1,
        obj2: type_obj2,
        obj3: type_obj3,
    ) -> None:
    # Attributs disponibles dans tous les process
    self.attr_multi_process = 0
    
    super().__init__(logger, self)
    
    # Attributs disponibles uniquement dans le main-process
    self.attr_main_process = 0
```

### Sérialisation des attributs

Lors de l’appel de l’`__init__,` le Brain se charge également de sérialiser automatiquement tous les attributs de classe. Cependant, comme nous l’avons vu, la majorité des objets que nous manipulons ne sont pas sérialisables. Un warning sera alors affiché par le logger pour tout attribut non sérialisable. Ce n’est pas une erreur, juste un avertissement. Tout attribut non sérialisé sera évidemment indisponible dans d’autres processus.
Exemple de warning :

```
14:49:30 -> [   brain    ]  WARNING   | [dynamic_init] cannot serialize attribute [ws_cmd].
14:49:30 -> [   brain    ]  WARNING   | [dynamic_init] cannot serialize attribute [ws_pami].
14:49:30 -> [   brain    ]  WARNING   | [dynamic_init] cannot serialize attribute [ws_lidar].
14:49:30 -> [   brain    ]  WARNING   | [dynamic_init] cannot serialize attribute [ws_odometer].
14:49:30 -> [   brain    ]  WARNING   | [dynamic_init] cannot serialize attribute [ws_camera].
```

### Refresh_Rate limitations

L'exécution des tâches repose sur de l'exécution asynchrone, ce qui signifie qu'il s'agit de pseudo-parallélisme. Il est crucial de garder à l'esprit qu'une routine avec un `refresh_rate` très faible va monopoliser le temps CPU disponible et, dans certains cas, ralentir l'exécution globale du Brain. Il est donc interdit de mettre un `refresh_rate` à 0 ! Ce paramètre doit être réglé avec attention !

### Communication inter-process limitations

Comme expliqué précédemment, la synchronisation entre le Brain partagé et son instance s'effectue via une routine qui s'exécute à très haute fréquence afin de minimiser la latence de communication. Par défaut, son `refresh_rate` est fixé à 0,01 seconde. Bien que la méthode soit optimisée pour réduire au maximum sa durée d'exécution, ce n'est pas instantané ! Il est donc important de prendre en compte ce facteur lorsqu'on décide de passer un traitement dans un autre processus.

## Exemple complet d’utilisation

…