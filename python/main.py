# Import de la classe depuis db_conf.py
from db_conf import DatabaseConfig

def main():
    try:
        # 1. Chargement de la configuration
        config = DatabaseConfig.from_env()

        # 2. Utilisation de l'objet config
        print("--- Configuration chargée avec succès ---")
        print(f"Hôte     : {config.host}")
        print(f"Port     : {config.port}")
        print(f"Base     : {config.name}")
        print(f"Utilisateur : {config.user}")

    except ValueError as e:
        print(f"Erreur de configuration : {e}")

if __name__ == "__main__":
    main()
