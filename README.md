# Crazyflie Autonomy

![Crazyflie 2.1+](https://img.shields.io/badge/Crazyflie-2.1%2B-168AAD)
![Crazyflie 2.1 Brushless](https://img.shields.io/badge/Crazyflie-2.1_Brushless-168AAD)
![Linux](https://img.shields.io/badge/Linux-Ubuntu%2FDebian-E95420)
![cfclient](https://img.shields.io/badge/test-cfclient-555555)
[![ROS 2 Jazzy](https://img.shields.io/badge/ROS_2-Jazzy-22314E?logo=ros&logoColor=white)](https://docs.ros.org/en/jazzy/)
[![Gazebo](https://img.shields.io/badge/Simulation-Gazebo-orange)](https://gazebosim.org/)

Projet de dévellopement d'une stack autonome autour des Crazyflie 2.1+ et 2.1 Brushless, avec ROS 2. Il s'appuie sur [Crazyswarm2](https://github.com/IMRCLab/crazyswarm2) comme sous-module Git. Les fonctions de simulation, de contrôle et de navigation autonome seront développées progressivement.

## Environnement

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

Installe [ROS 2 Jazzy pour Ubuntu 24.04](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html) si ce n'est pas déjà fait, puis installe les outils de développement :

```bash
sudo apt update
sudo apt install -y \
	git \
	curl \
	python3.12 \
	python3.12-venv \
	python3-pip \
	python3-colcon-common-extensions \
	python3-rosdep \
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

Si `uv` n'est pas reconnu, ouvrir un nouveau terminal. Voir le [guide officiel d'installation de uv](https://docs.astral.sh/uv/getting-started/installation/).

## 3. Cloner le dépôt

```bash
git clone --recurse-submodules https://github.com/thoukam/crazyflie-autonomy.git
cd crazyflie-autonomy
```

L'option `--recurse-submodules` récupère Crazyswarm2 avec la version enregistrée par le dépôt. Si le dépôt a déjà été cloné sans ses sous-modules :

```bash
git submodule update --init --recursive
```

Le sous-module est déclaré dans `.gitmodules` à `src/src/crazyswarm2` :

```bash
ls src/src/crazyswarm2
```

## 4. Créer l'environnement Python

Depuis la racine du dépôt, créer un environnement avec Python 3.12. `--system-site-packages` permet d'accéder aux paquets Python de ROS 2 Jazzy :

```bash
uv venv --python /usr/bin/python3.12 --system-site-packages .venv
touch .venv/COLCON_IGNORE
source scripts/activate.sh
python --version
```

La version affichée doit être `Python 3.12.x`. Le fichier `.venv/COLCON_IGNORE` empêche `colcon` d'explorer l'environnement virtuel comme s'il contenait des packages ROS.

## 5. Installer les dépendances Python

Le fichier [`requirements.txt`](requirements.txt) liste les bibliothèques Python du projet. Installer les paquets dans l'environnement activé :

```bash
uv pip install -r requirements.txt
python -c "import cflib, rowan, numpy; print('Python OK')"
```

Il contient notamment `cflib` pour communiquer avec les drones, `cfclient` pour les essais, `numpy` et `scipy` pour le calcul, `pyusb` pour l'USB, `PyYAML` pour les configurations et `pytest` pour les tests. Mettre ce fichier à jour lorsqu'une dépendance Python est ajoutée.

## 6. Configurer ROS 2 et ses dépendances

Charger l'environnement ROS 2 dans le terminal :

```bash
source /opt/ros/jazzy/setup.bash
python -c "import rclpy; print('ROS 2 Jazzy OK')"
```

Installer les dépendances système utilisées par Crazyswarm2 :

```bash
sudo apt install -y \
	libboost-program-options-dev \
	libusb-1.0-0-dev \
	ros-jazzy-motion-capture-tracking \
	ros-jazzy-tf-transformations
```

Voir la [documentation d'installation de Crazyswarm2](https://raw.githubusercontent.com/IMRCLab/crazyswarm2/main/docs2/installation.rst). Installer ensuite les dépendances déclarées dans les fichiers `package.xml` :

```bash
rosdep update
rosdep install --from-paths src --ignore-src --rosdistro jazzy -r -y
```

Si `rosdep` n'a jamais été initialisé sur cette installation Ubuntu, l'initialiser une seule fois :

```bash
sudo rosdep init
rosdep update
```

`requirements.txt` gère les dépendances Python; `rosdep` lit les `package.xml` pour installer les dépendances système et ROS.

## 7. Compiler le workspace

Depuis la racine du dépôt, charger ROS et l'environnement Python, vérifier les packages détectés puis compiler :

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

Après une compilation réussie, charger le workspace et vérifier les packages

```bash
source install/setup.bash
ros2 pkg list | grep crazyflie
ros2 pkg prefix crazyflie
```

## Utilisation quotidienne

Dans chaque nouveau terminal, depuis la racine du dépôt

```bash
source /opt/ros/jazzy/setup.bash
source scripts/activate.sh
source install/setup.bash
```

Après une modification d'un package C++

```bash
colcon build --base-paths src --symlink-install
source install/setup.bash
```

Après l'ajout d'une dépendance Python dans `requirements.txt`

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

La mise à jour du sous-module récupère la révision enregistrée dans le dépôt. Ne pas mettre Crazyswarm2 à jour vers sa branche principale sans validation, afin d'éviter une incompatibilité.

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
	└── src/
		└── crazyswarm2/    # Sous-module Git
```

Les dossiers `.venv`, `build`, `install` et `log` sont des fichiers locaux ou des artefacts de compilation et ne doivent pas être ajoutés au dépôt.

## Documentation complémentaire

- [Montage, client et premiers essais des drones](docs/documentation.md)
- [Crazyswarm2](https://github.com/IMRCLab/crazyswarm2)
- [ROS 2 Jazzy](https://docs.ros.org/en/jazzy/)
- [Gazebo Sim](https://gazebosim.org/)
