import logging

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger

# Adresse radio du Crazyflie
URI21p = "radio://0/80/2M/E7E7E7E701"
#URI21b = "radio://0/80/2M/E7E7E7E702"

logging.basicConfig(level=logging.ERROR)


def main():

    # Initialisation des pilotes radio
    cflib.crtp.init_drivers()

    # Configuration de la télémétrie
    log_config = LogConfig(
        name="Telemetry",
        period_in_ms=100
    )

    log_config.add_variable("stabilizer.roll", "float")
    log_config.add_variable("stabilizer.pitch", "float")
    log_config.add_variable("stabilizer.yaw", "float")
    log_config.add_variable("pm.vbat", "float")

    print("Connexion au Crazyflie...")

    # Connexion radio
    with SyncCrazyflie(
        URI21p,
        cf=Crazyflie(rw_cache="./cache")
    ) as scf:

        print("Crazyflie connecté !")

        # Lecture des données
        with SyncLogger(scf, log_config) as logger:

            for i, (_, data, _) in enumerate(logger):

                roll = data["stabilizer.roll"]
                pitch = data["stabilizer.pitch"]
                yaw = data["stabilizer.yaw"]
                battery = data["pm.vbat"]

                print(
                    f"Roll: {roll:.2f}° | "
                    f"Pitch: {pitch:.2f}° | "
                    f"Yaw: {yaw:.2f}° | "
                    f"Batterie: {battery:.2f} V"
                )

                # Arrêt après 50 mesures (environ 5 secondes)
                if i >= 49:
                    break

    print("Crazyflie déconnecté.")


if __name__ == "__main__":
    main()
