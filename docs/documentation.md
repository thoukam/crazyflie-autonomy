# Montage et premiers essais

Nous avons commencé avec deux drones : un **Crazyflie 2.1+** et un **Crazyflie 2.1 Brushless**. Cette page rassemble les étapes de montage, la connexion au client et nos premiers essais de pilotage.

Nous la complétons au fur et à mesure du projet. L'idée est de garder une trace de notre travail, avec les réglages utilisés et les limites rencontrées, pour que d'autres puissent s'en servir comme point de départ. Les vols manuels avec `cfclient` ont été réalisés ; les essais avec ROS 2 sont encore en cours.

## 1. Montage

Avant de monter ton drone, fais le test d'autodiagnostic décrit dans le guide du modèle. Pour les premiers branchements et contrôles, retire les hélices. Suis ensuite la procédure correspondant exactement au drone : les hélices et certaines pièces ne sont pas interchangeables entre modèles.

- [Crazyflie 2.0, 2.1 et 2.1+ : guide de démarrage et montage](https://www.bitcraze.io/documentation/tutorials/getting-started-with-crazyflie-2-x/)
- [Crazyflie 2.1 Brushless : guide de montage](https://www.bitcraze.io/documentation/tutorials/getting-started-with-crazyflie-brushless/)

Le guide général couvre aussi le Crazyflie 2.0. De notre côté, nous utilisons le 2.1+ et le 2.1 Brushless.

## 2. Préparer le client sous Linux

Commence par installer les dépendances système :

```bash
sudo apt update
sudo apt install git python3-pip libxcb-xinerama0 libxcb-cursor0
```

Sur les versions récentes d'Ubuntu/Debian, la mise à niveau globale de `pip` peut être bloquée par la protection PEP 668. Nous n'en avons pas besoin ici : l'installateur de `uv` suffit, sans forcer l'installation globale de `pip`.

Installe ensuite `uv` en suivant le [guide officiel d'installation](https://docs.astral.sh/uv/getting-started/installation/). Sous Linux, l'installateur autonome officiel est :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Ouvre un nouveau terminal si nécessaire, puis lance le client Crazyflie :

```bash
uvx cfclient
```

Au premier lancement, `uvx` télécharge le client et ses dépendances. Une fois l'interface ouverte, choisis l'une des méthodes de connexion ci-dessous.

## 3. Connexion directe par micro-USB

Cette méthode relie le port micro-USB du Crazyflie à l'ordinateur. Elle permet notamment de vérifier que le drone démarre et que le client reçoit ses données ; elle ne remplace pas la liaison radio pour les essais de vol.

1. Branche le Crazyflie en USB et repérer son identifiant avec `lsusb`. Le Crazyflie apparaît normalement avec l'identifiant `0483:5740`.
2. Dans la sortie de `lsusb`, relève les numéros `Bus` et `Device`, puis vérifie les permissions du périphérique. Par exemple, pour `Bus 001` et `Device 004` :

	```bash
	ls -l /dev/bus/usb/001/004
	```

3. Configure le groupe USB et les règles udev :

	```bash
	sudo groupadd -f plugdev
	sudo usermod -a -G plugdev "$USER"

	sudo tee /etc/udev/rules.d/99-bitcraze.rules > /dev/null <<'EOF'
	# Crazyradio (fonctionnement normal)
	SUBSYSTEM=="usb", ATTRS{idVendor}=="1915", ATTRS{idProduct}=="7777", MODE="0664", GROUP="plugdev"
	# Bootloader Crazyradio classique
	SUBSYSTEM=="usb", ATTRS{idVendor}=="1915", ATTRS{idProduct}=="0101", MODE="0664", GROUP="plugdev"
	# Crazyflie par USB
	SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0664", GROUP="plugdev"
	# Crazyradio 2.0
	SUBSYSTEM=="usb", ATTRS{idVendor}=="35f0", ATTRS{idProduct}=="bad2", MODE="0664", GROUP="plugdev"
	EOF

	sudo udevadm control --reload-rules
	sudo udevadm trigger
	```

4. Débranche puis rebranche le drone, et déconnecte-toi puis reconnecte-toi à ta session Linux pour que l'appartenance au groupe `plugdev` soit prise en compte.
5. Relance `uvx cfclient`, sélectionne la connexion USB si elle est proposée, puis vérifie les données de télémétrie avant tout essai de vol.

## 4. Connexion radio avec Crazyradio 2.0

Nous utilisons un **Crazyradio 2.0** pour communiquer avec les deux Crazyflie. Avant ton premier essai, suis le [guide officiel Crazyradio 2.0](https://www.bitcraze.io/documentation/tutorials/getting-started-with-crazyradio-2-0/) : assemblage de l'antenne, permissions USB sous Linux, puis installation du firmware.

Pour flasher le firmware, mets la radio en mode bootloader (maintenir son bouton pendant le branchement), télécharge le fichier `.uf2` depuis les [dernières versions du firmware Crazyradio 2.0](https://github.com/bitcraze/crazyradio2-firmware/releases/latest), puis copie ce fichier sur le lecteur `Crazyradio2` qui apparaît. La radio redémarre à la fin du flash.

Une fois la radio configurée, branche le Crazyradio 2.0, lance `uvx cfclient`, puis le scan, et sélectionne ton drone. Vérifie que la télémétrie remonte avant de passer au vol. Nous testons ici un drone à la fois dans `cfclient`. La radio peut communiquer avec plusieurs drones, mais nous documenterons les essais simultanés lorsque nous les aurons réalisés.

## 5. Adresses radio et communication multi-drone

Une URI radio a la forme `radio://radio/canal/débit/adresse`. L'adresse distingue les drones ; le numéro de la radio, le canal et le débit indiquent les paramètres de liaison. Les valeurs ci-dessous sont des **exemples à configurer**, pas les adresses déjà enregistrées :

| Drone | URI d'exemple |
| --- | --- |
| Crazyflie 2.1+ | `radio://0/80/2M/E7E7E7E701` |
| Crazyflie 2.1 Brushless | `radio://0/80/2M/E7E7E7E702` |

Configure les drones **un à la fois** : éteins l'autre drone, connecte-toi au premier dans `cfclient` (au besoin par USB), ouvre **Connect > Configure 2.x**, note l'adresse actuelle, saisis la nouvelle adresse et clique sur **Write**. Redémarre le drone et vérifie la connexion à cette nouvelle URI. Fais ensuite la même chose pour le deuxième drone. Garde le même canal et le même débit sur les deux, et vérifie les paramètres radio avant de reprendre les valeurs d'exemple.

Avec `cfclient`, recherche puis teste chaque URI séparément, moteurs arrêtés. Pour une communication réellement simultanée, il faut un programme Python avec `cflib` et sa classe [`Swarm`](https://www.bitcraze.io/documentation/repository/crazyflie-lib-python/master/user-guides/sbs_swarm_interface/), en fournissant les deux URI sur le même canal. Nous n'avons pas encore ajouté cette étape au projet. Le vol en essaim nécessite en plus une estimation de position fiable et des essais sécurisés ; une connexion radio simultanée seule ne suffit pas.

## 6. Nos premiers vols et essais

### Vol manuel avec manette Xbox et cfclient

Nous avons fait voler les deux Crazyflie sous Ubuntu avec une manette Xbox et le Crazyflie Client (`cfclient`). Voici les réglages et les étapes que nous avons utilisés.

Voici comment reprendre ces étapes :

1. **Connexion de la manette :** appaire la manette Xbox avec Ubuntu en Bluetooth, ou branche-la en USB selon ta préférence.

2. **Lancement du client :**
   ```bash
   uvx cfclient
   ```

3. **Connexion au drone :** sélectionne la liaison `radio://0/80/2M` via Crazyradio, avec l'adresse correspondant à ton drone.

4. **Configuration de la manette :**
   - Ouvre `Input device > Configure device mapping`
   - Sélectionne `Xbox Wireless Controller`
   - Configure les axes :
     - `Thrust` : joystick gauche vertical
     - `Yaw` : joystick gauche horizontal
     - `Pitch` : joystick droit vertical
     - `Roll` : joystick droit horizontal
   - Configure les boutons `Emergency stop`, `Arm/disarm` et `Assisted control`
   - Enregistre le profil

5. **Configuration du vol :**
   - `Flight mode` : Normal
   - `Assist mode` : Altitude hold (assistance activable via le bouton configuré)
   - `Supervisor` : Auto armed pour le 2.1+ et ARM pour le Brushless

6. **Validation :**
   - Vérifie les commandes dans `Gamepad Input`
   - Vérifie la télémétrie et l'état du drone
   - Une fois ces vérifications faites, nous sommes passés au décollage et au pilotage manuel

### Ce qui a fonctionné

Nous avons pu connecter les drones par radio, lire leur télémétrie et piloter chacun d'eux avec la manette Xbox sous Ubuntu. Après avoir vérifié le mapping des commandes, nous avons réalisé les premiers décollages et vols manuels.

### Les limites de ces essais

- **Positionnement :** aucun Deck détecté (`0 deck(s) found`). Le drone ne dispose pas de maintien automatique de position horizontale.
- **Altitude :** maintien d'altitude possible avec le baromètre intégré via `Altitude hold`, mais moins précis qu'avec un capteur de distance.
- **Multi-drones :** `cfclient` pilote un seul Crazyflie à la fois. Nous prévoyons d'utiliser `Crazyswarm2` sous ROS 2 pour piloter plusieurs drones en même temps.

### Commande Xbox via ROS 2 et Crazyswarm2 (premier essai)

Crazyswarm2 fournit déjà le nœud `teleop`. Pour ce premier essai, nous utilisons la chaîne suivante :

```text
Manette Xbox -> joy_node -> /joy -> teleop (cmd_rpy) -> /cf1/cmd_vel_legacy -> Crazyflie Server -> Crazyradio
```

Les fichiers [`config/crazyflies.yaml`](../config/crazyflies.yaml) et [`config/teleop.yaml`](../config/teleop.yaml) configurent un seul Crazyflie, nommé `cf1`, et le mode d'attitude `cmd_rpy`. L'URI configurée est celle du 2.1+ (`E7E7E7E701`) ; remplace-la si l'adresse radio réelle du drone est différente.

Après avoir compilé le workspace ROS 2, ouvre trois terminaux à la racine du dépôt. Dans chacun, charge ROS 2 et le workspace :

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

**Terminal 1 :** lance le serveur Crazyswarm2 sans son téléop intégré ni motion capture :

```bash
ros2 launch crazyflie launch.py \
	backend:=cpp \
	teleop:=False \
	mocap:=False \
	crazyflies_yaml_file:="$(pwd)/config/crazyflies.yaml"
```

**Terminal 2 :** lance la lecture de la manette. `device_id` vaut `0` pour la première manette détectée :

```bash
ros2 run joy joy_node --ros-args -p device_id:=0
```

**Terminal 3 :** lance le téléopérateur avec le mapping local et relier ses commandes au drone `cf1` :

```bash
ros2 run crazyflie teleop --ros-args \
	--params-file config/teleop.yaml \
	-r joy:=/joy \
	-r emergency:=/all/emergency \
	-r arm:=/all/arm \
	-r takeoff:=/all/takeoff \
	-r land:=/all/land \
	-r notify_setpoints_stop:=/cf1/notify_setpoints_stop \
	-r cmd_vel_legacy:=/cf1/cmd_vel_legacy
```

Avant tout vol, retire les hélices et vérifie la manette dans un quatrième terminal :

```bash
ros2 topic echo /joy
```

Bouge chaque axe et appuie sur les boutons pour relever leurs indices. Si les valeurs ne correspondent pas au profil Xbox, ajuste les indices ou inverser le signe de l'axe dans `config/teleop.yaml`. N'appuie pas sur les boutons d'armement ou de décollage pendant cette vérification.

**À garder en tête :** `cmd_rpy` commande directement roll, pitch, yaw-rate et poussée. Sans Flow deck ni autre localisation, le drone ne maintient pas sa position et ce mode ne fournit pas de maintien automatique d'altitude. La vérification des axes sans hélices permet de contrôler que les commandes passent bien par ROS. Nous n'avons pas encore validé le vol avec cette configuration. Pour passer au vol, il faudra remonter les hélices, prévoir une zone dégagée et rester prêt à utiliser l'arrêt d'urgence.

### Test Python de connexion et de télémétrie (réalisé)

Nous avons aussi testé la connexion en Python avec [`scripts/connect.py`](../scripts/connect.py). Ce script vérifie la liaison radio avec un Crazyflie et affiche sa télémétrie pendant environ 5 secondes : roll, pitch, yaw et tension de la batterie. Il se connecte actuellement au Crazyflie 2.1+ avec l'URI configurée dans le script.

Depuis la racine du dépôt :

```bash
source scripts/activate.sh
cd scripts
python connect.py
```

Pour tester le 2.1 Brushless, remplace l'URI active dans `connect.py` pour utiliser celle du Brushless.

Ce test nous a permis de vérifier la connexion et la lecture des données. Le script n'envoie aucune commande de vol : nos premiers vols ont été faits avec la manette Xbox et `cfclient`. Pour la suite, nous devrons tenir compte de l'absence de Flow deck dans les scripts de pilotage. Sans estimation fiable, nous ne pouvons pas compter sur un maintien de position ou d'altitude.

## Les ressources qui nous servent de référence

- [Montage et prise en main des Crazyflie 2.0/2.1/2.1+](https://www.bitcraze.io/documentation/tutorials/getting-started-with-crazyflie-2-x/)
- [Montage du Crazyflie 2.1 Brushless](https://www.bitcraze.io/documentation/tutorials/getting-started-with-crazyflie-brushless/)
- [Installation de uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Permissions USB Linux pour Crazyflie et Crazyradio](https://www.bitcraze.io/documentation/repository/crazyflie-lib-python/master/installation/usb_permissions/)
- [Mise en service et firmware du Crazyradio 2.0](https://www.bitcraze.io/documentation/tutorials/getting-started-with-crazyradio-2-0/)
- [Configuration de l'adresse radio dans cfclient](https://www.bitcraze.io/documentation/repository/crazyflie-clients-python/master/userguides/userguide_client/)
- [Manettes et configuration des commandes dans cfclient](https://www.bitcraze.io/documentation/repository/crazyflie-clients-python/master/userguides/inputdevices/)
- [Connexion et télémétrie depuis un script cflib](https://www.bitcraze.io/documentation/repository/crazyflie-lib-python/master/user-guides/sbs_connect_log_param/)
- [Tutoriel Motion Commander et prérequis de positionnement](https://www.bitcraze.io/documentation/repository/crazyflie-lib-python/master/user-guides/sbs_motion_commander/)
- [Gestion de plusieurs Crazyflie avec cflib](https://www.bitcraze.io/documentation/repository/crazyflie-lib-python/master/user-guides/sbs_swarm_interface/)
