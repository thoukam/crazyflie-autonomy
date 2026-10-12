Documentation du montage et des premiers essais de nos deux drones : un **Crazyflie 2.1+** et un **Crazyflie 2.1 Brushless**. Les badges indiquent le matériel et les outils documentés à ce stade; ROS 2, Gazebo et les modèles précis de manette seront ajoutés lorsqu'ils seront intégrés et testés.

## 1. Montage

Avant l'assemblage, effectuer le test d'autodiagnostic décrit dans le guide du modèle. Pour les premiers branchements et contrôles, retirer les hélices. Respecter ensuite la procédure correspondant exactement au drone : les hélices et certaines pièces ne sont pas interchangeables entre modèles.

- [Crazyflie 2.0, 2.1 et 2.1+ : guide de démarrage et montage](https://www.bitcraze.io/documentation/tutorials/getting-started-with-crazyflie-2-x/)
- [Crazyflie 2.1 Brushless : guide de montage](https://www.bitcraze.io/documentation/tutorials/getting-started-with-crazyflie-brushless/)

Le Crazyflie 2.0 est couvert par le guide général, mais les deux appareils suivis dans ce projet sont le 2.1+ et le 2.1 Brushless.

## 2. Préparer le client sous Linux

Installer les dépendances système :

```bash
sudo apt update
sudo apt install git python3-pip libxcb-xinerama0 libxcb-cursor0
```

Sur les versions récentes d'Ubuntu/Debian, la mise à niveau globale de `pip` peut être bloquée par la protection PEP 668. Elle n'est pas nécessaire pour installer `uv` avec son installateur officiel; ne pas forcer une installation globale de `pip`.

Installer `uv` en suivant le [guide officiel d'installation](https://docs.astral.sh/uv/getting-started/installation/). Sous Linux, l'installateur autonome officiel est :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Ouvrir un nouveau terminal si nécessaire, puis lancer le client Crazyflie :

```bash
uvx cfclient
```

Au premier lancement, `uvx` télécharge le client et ses dépendances. Une fois l'interface ouverte, choisir l'une des méthodes de connexion ci-dessous.

## 3. Connexion directe par micro-USB

Cette méthode relie le port micro-USB du Crazyflie à l'ordinateur. Elle permet notamment de vérifier que le drone démarre et que le client reçoit ses données; elle ne remplace pas la liaison radio pour les essais de vol.

1. Brancher le Crazyflie en USB et repérer son identifiant avec `lsusb`. Le Crazyflie apparaît normalement avec l'identifiant `0483:5740`.
2. Dans la sortie de `lsusb`, relever les numéros `Bus` et `Device`, puis vérifier les permissions du périphérique. Par exemple, pour `Bus 001` et `Device 004` :

	```bash
	ls -l /dev/bus/usb/001/004
	```

3. Configurer le groupe USB et les règles udev :

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

4. Débrancher/rebrancher le drone et se déconnecter/reconnecter à la session Linux pour que l'appartenance au groupe `plugdev` soit prise en compte.
5. Relancer `uvx cfclient`, sélectionner la connexion USB si elle est proposée, puis vérifier les données de télémétrie avant tout essai de vol.

## 4. Connexion radio avec Crazyradio 2.0

Le projet utilise un **Crazyradio 2.0** pour communiquer avec les deux Crazyflie. Avant le premier essai, suivre le [guide officiel Crazyradio 2.0](https://www.bitcraze.io/documentation/tutorials/getting-started-with-crazyradio-2-0/) : assemblage de l'antenne, permissions USB sous Linux, puis installation du firmware.

Pour flasher le firmware, mettre le radio en mode bootloader (maintenir son bouton pendant le branchement), télécharger le fichier `.uf2` depuis les [dernières versions du firmware Crazyradio 2.0](https://github.com/bitcraze/crazyradio2-firmware/releases/latest), puis copier ce fichier sur le lecteur `Crazyradio2` qui apparaît. Le radio redémarre à la fin du flash.

Après configuration, brancher le Crazyradio 2.0, démarrer `uvx cfclient`, lancer le scan et sélectionner le Crazyflie détecté. Vérifier la télémétrie avant d'envisager un vol. Un même radio peut servir à communiquer avec plusieurs drones; les essais simultanés relèvent de la configuration multi-drone et seront documentés séparément. Le test rapide décrit ici valide une connexion à la fois dans cfclient.

## 5. Adresses radio et communication multi-drone

Une URI radio a la forme `radio://radio/canal/débit/adresse`. L'adresse distingue les drones; le numéro du radio, le canal et le débit indiquent les paramètres de liaison. Les valeurs ci-dessous sont des **exemples à configurer**, pas les adresses déjà enregistrées :

| Drone | URI d'exemple |
| --- | --- |
| Crazyflie 2.1+ | `radio://0/80/2M/E7E7E7E701` |
| Crazyflie 2.1 Brushless | `radio://0/80/2M/E7E7E7E702` |

Configurer les drones **un à la fois** : éteindre l'autre drone, se connecter au premier dans `cfclient` (au besoin par USB), ouvrir **Connect > Configure 2.x**, noter l'adresse actuelle, saisir la nouvelle adresse et cliquer sur **Write**. Redémarrer et vérifier la connexion à cette nouvelle URI. Répéter pour le deuxième drone. Garder le même canal et le même débit sur les deux; vérifier les paramètres radio avant de réutiliser les valeurs d'exemple.

Avec `cfclient`, rechercher puis tester chaque URI séparément, moteurs arrêtés. Pour une communication réellement simultanée, utiliser un programme Python avec `cflib` et sa classe [`Swarm`](https://www.bitcraze.io/documentation/repository/crazyflie-lib-python/master/user-guides/sbs_swarm_interface/), en fournissant les deux URI sur le même canal. Cette étape n'est pas encore implémentée dans le projet. Le vol en essaim nécessite en plus une estimation de position fiable et des essais sécurisés; une connexion radio simultanée seule ne suffit pas.

## 6. Prochaines étapes : premiers vols

Ces essais restent **à réaliser**. Tester un seul drone à la fois, après avoir vérifié sa connexion radio et sa télémétrie. Les moteurs ne doivent être commandés que dans une zone dégagée, avec les hélices correctement montées et sans personne à proximité.

### Vol manuel avec Xbox et cfclient

Connecter la manette à Ubuntu, lancer `uvx cfclient`, puis choisir l'URI du drone à tester. Dans **Input device**, sélectionner la manette et vérifier dans **Flight Data** que roll, pitch, yaw et thrust réagissent correctement, sans interaction entre les axes et avec la poussée au minimum avant connexion. Si la manette n'est pas reconnue ou mal mappée, la configurer dans **Input device > Configure device mapping**. Commencer par un vol bref et doux, prêt à couper les moteurs.

Sans Flow deck ni autre système de positionnement, le Crazyflie peut être piloté manuellement mais ne maintient pas sa position : une dérive est normale et le pilote doit corriger en continu. La manette Xbox est à valider sur notre installation Ubuntu; la documentation Bitcraze mentionne notamment les manettes Xbox 360.

### Vol commandé par script Python

Installer `cflib` si nécessaire (`uv pip install cflib` dans l'environnement Python utilisé), puis commencer par un script qui se connecte à **une seule URI** et vérifie la télémétrie. Pour un essai en vol sans deck de positionnement, utiliser les commandes directes d'attitude et de poussée de [`cflib` Commander](https://www.bitcraze.io/documentation/repository/crazyflie-lib-python/master/api/cflib/crazyflie/commander/) avec une séquence courte et des valeurs prudentes.

Ne pas utiliser `MotionCommander` ni des consignes de position/vitesse pour ce test sans Flow deck ou autre source de position fiable : ces commandes supposent une estimation de position. Sans ce retour, le script ne peut pas garantir le maintien de la hauteur ou de la position; cette limitation doit être prise en compte avant tout vol automatisé.

## Sources officielles

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
