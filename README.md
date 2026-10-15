# Crazyflie Autonomy

![Crazyflie 2.1+](https://img.shields.io/badge/Crazyflie-2.1%2B-168AAD)
![Crazyflie 2.1 Brushless](https://img.shields.io/badge/Crazyflie-2.1_Brushless-168AAD)
![Linux](https://img.shields.io/badge/Linux-Ubuntu%2FDebian-E95420)
![cfclient](https://img.shields.io/badge/test-cfclient-555555)
[![ROS 2 Jazzy](https://img.shields.io/badge/ROS_2-Jazzy-22314E?logo=ros&logoColor=white)](https://docs.ros.org/en/jazzy/)
[![Gazebo](https://img.shields.io/badge/Simulation-Gazebo-orange)](https://gazebosim.org/)

Nous développons ce projet pour faire voler nos Crazyflie 2.1+ et 2.1 Brushless de façon autonome avec ROS 2. Nous nous appuyons sur [Crazyswarm2](https://github.com/IMRCLab/crazyswarm2), intégré au dépôt comme sous-module Git.

Pour l'instant, nous avons réalisé les premiers vols manuels avec une manette Xbox et `cfclient`, ainsi qu'un test de connexion et de télémétrie en Python. Le pilotage avec ROS 2 est en cours d'essai. La simulation et la navigation autonome font partie de la suite du projet.

Ce README rassemble les étapes pour préparer l'environnement de travail. Nous partageons aussi nos essais dans la [documentation](docs/documentation.md), pour garder une trace de ce que nous avons fait et donner une base à ceux qui voudraient monter un projet similaire.

## Notre environnement de travail

| Composant | Version ou rôle |
| --- | --- |
| Système | Ubuntu 24.04 LTS |
| ROS 2 | Jazzy Jalisco |
| Python | 3.12 |
| Environnement Python | `uv` et `.venv` |
| Compilation ROS 2 | `colcon` |
| Dépendances ROS | `rosdep` |
| Simulation prévue | Gazebo Sim |
| Communication radio | Crazyradio 2.0 |

## 1. Prérequis système

### Pour commencer avec le drone

Tu peux monter le drone, te connecter avec `cfclient` et faire les premiers essais sans ROS 2. Ces étapes sont décrites dans la [documentation de prise en main](docs/documentation.md).

Si tu veux récupérer le dépôt sur ton ordinateur, installe Git :

```bash
sudo apt update
sudo apt install -y git
```

Tu peux ensuite passer à l'étape [Cloner le dépôt](#3-cloner-le-dépôt), même si ROS 2 n'est pas encore installé.

### Pour travailler avec ROS 2

La suite de l'installation prépare l'environnement ROS 2 du projet. Quand tu veux passer à cette partie, installe [ROS 2 Jazzy pour Ubuntu 24.04](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html) si ce n'est pas déjà fait, puis ajoute les outils de développement :

```bash
sudo apt update
sudo apt install -y \
	curl \
	python3.12 \
	python3.12-venv \
	python3-pip \
	python3-colcon-common-extensions \
	python3-rosdep \
	ros-jazzy-joy \
	python3-dev \
	build-essential \
	cmake
```

`colcon` compile les packages ROS 2, `rosdep` installe leurs dépendances et les outils de compilation fournissent l'environnement C/C++.

## 2. Installer uv

`uv` sert à créer l'environnement Python et à y installer les dépendances :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

Si ton terminal ne reconnaît pas `uv`, ouvre un nouveau terminal. Tu peux aussi consulter le [guide officiel d'installation de uv](https://docs.astral.sh/uv/getting-started/installation/).

## 3. Cloner le dépôt

```bash
git clone --recurse-submodules https://github.com/thoukam/crazyflie-autonomy.git
cd crazyflie-autonomy
```

L'option `--recurse-submodules` récupère Crazyswarm2 et `ros_gz_crazyflie` aux révisions enregistrées par le dépôt. Si tu as déjà cloné le dépôt sans les sous-modules :

```bash
git submodule update --init --recursive
```

Les deux sous-modules sont directement sous `src/` :

```bash
ls src/crazyswarm2
ls src/ros_gz_crazyflie
```

## 4. Créer l'environnement Python

Depuis la racine du dépôt, crée un environnement avec Python 3.12. `--system-site-packages` permet d'accéder aux paquets Python de ROS 2 Jazzy :

```bash
uv venv --python /usr/bin/python3.12 --system-site-packages .venv
touch .venv/COLCON_IGNORE
source scripts/activate.sh
python --version
```

La version affichée doit être `Python 3.12.x`. Le fichier `.venv/COLCON_IGNORE` empêche `colcon` d'explorer l'environnement virtuel comme s'il contenait des packages ROS.

## 5. Installer les dépendances Python

Le fichier [`requirements.txt`](requirements.txt) liste les bibliothèques Python du projet. Installe les paquets dans l'environnement activé :

```bash
uv pip install -r requirements.txt
python -c "import cflib, rowan, numpy; print('Python OK')"
```

Il contient notamment `cflib` pour communiquer avec les drones, `cfclient` pour les essais, `numpy` et `scipy` pour le calcul, `pyusb` pour l'USB, `PyYAML` pour les configurations et `pytest` pour les tests. Si tu ajoutes une bibliothèque Python au projet, pense à la noter dans ce fichier.

## 6. Configurer ROS 2 et ses dépendances

Charge l'environnement ROS 2 dans ton terminal :

```bash
source /opt/ros/jazzy/setup.bash
python -c "import rclpy; print('ROS 2 Jazzy OK')"
```

Installe les dépendances système utilisées par Crazyswarm2 :

```bash
sudo apt install -y \
	libboost-program-options-dev \
	libusb-1.0-0-dev \
	ros-jazzy-motion-capture-tracking \
	ros-jazzy-tf-transformations
```

Ces dépendances sont indiquées dans la [documentation d'installation de Crazyswarm2](https://raw.githubusercontent.com/IMRCLab/crazyswarm2/main/docs2/installation.rst). Installe ensuite les dépendances déclarées dans les fichiers `package.xml` :

```bash
rosdep update
rosdep install --from-paths src --ignore-src --rosdistro jazzy -r -y
```

Si `rosdep` n'a jamais été initialisé sur cette installation Ubuntu, initialise-le une seule fois :

```bash
sudo rosdep init
rosdep update
```

`requirements.txt` gère les dépendances Python ; `rosdep` lit les `package.xml` pour installer les dépendances système et ROS.

## 7. Compiler le workspace

Depuis la racine du dépôt, charge ROS et l'environnement Python, vérifie les packages détectés, puis lance la compilation :

```bash
source /opt/ros/jazzy/setup.bash
source scripts/activate.sh
colcon list --base-paths src
colcon build \
	--base-paths src \
	--symlink-install \
	--cmake-args -DCMAKE_BUILD_TYPE=Release
```

`--symlink-install` facilite le développement pour les fichiers Python et de configuration. Les changements de code C++ nécessitent une nouvelle compilation. La commande suit les indications du [guide d'installation Crazyswarm2](https://raw.githubusercontent.com/IMRCLab/crazyswarm2/main/docs2/installation.rst).

Une fois la compilation terminée, charge le workspace et vérifie que les packages sont bien disponibles :

```bash
source install/setup.bash
ros2 pkg list | grep crazyflie
ros2 pkg prefix crazyflie
```

## Utilisation quotidienne

Dans chaque nouveau terminal, place-toi à la racine du dépôt et charge les environnements :

```bash
source /opt/ros/jazzy/setup.bash
source scripts/activate.sh
source install/setup.bash
```

Si tu modifies un package C++, recompile-le puis recharge le workspace :

```bash
colcon build --base-paths src --symlink-install
source install/setup.bash
```

Si tu ajoutes une dépendance Python dans `requirements.txt`, installe-la dans ton environnement :

```bash
uv pip install -r requirements.txt
```

## Mettre à jour le dépôt

```bash
git pull
git submodule update --init --recursive
source /opt/ros/jazzy/setup.bash
source scripts/activate.sh
uv pip install -r requirements.txt
rosdep install --from-paths src --ignore-src --rosdistro jazzy -r -y
colcon build --base-paths src --symlink-install
source install/setup.bash
```

La mise à jour des sous-modules récupère les révisions enregistrées dans notre dépôt. Nous gardons ces versions pour travailler sur la même base. Si tu veux essayer une version plus récente de Crazyswarm2, vérifie qu'elle fonctionne avec le projet avant de changer la révision partagée.

## Organisation du dépôt

```text
crazyflie-autonomy/
├── .gitmodules
├── .gitignore
├── README.md
├── requirements.txt
├── .venv/                  # Environnement Python, non suivi par Git
├── scripts/                # Scripts d'aide
├── docs/                   # Documentation complémentaire
└── src/
	├── crazyswarm2/           # Sous-module Git
	└── ros_gz_crazyflie/      # Sous-module Git
```

Les dossiers `.venv`, `build`, `install` et `log` sont créés localement pendant l'installation et la compilation. Garde-les en dehors du suivi Git.

## Documentation complémentaire

- [Montage, client et premiers essais des drones](docs/documentation.md)
- [Crazyswarm2](https://github.com/IMRCLab/crazyswarm2)
- [ROS 2 Jazzy](https://docs.ros.org/en/jazzy/)
- [Gazebo Sim](https://gazebosim.org/)
