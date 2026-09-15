import os
from dotenv import load_dotenv

class AutoDB:
    def __init__(
        self,
        db_name: str = None,
        db_addr: str = None,
        db_port: int = None,
        db_user: str = None,
        db_passwd: str = None,
        db_type: str = None,
        env_path: str = ".env"
    ):
        self._load_env(env_path)

        # Les arguments explicites remplacent le .env
        self.db_name = db_name or os.getenv("DB_NAME")
        if not self.db_name:
            raise ValueError("Le paramètre DB_NAME est obligatoire (soit dans le .env, soit dans le constructeur).")

        self.db_addr = db_addr or os.getenv("DB_ADDR") or "localhost"
        self.db_user = db_user or os.getenv("DB_USER") or self.db_name
        self.db_passwd = db_passwd if db_passwd is not None else os.getenv("DB_PASSWD", "")

        raw_port = db_port or os.getenv("DB_PORT")
        self.db_port = int(raw_port) if raw_port else None

        raw_type = db_type or os.getenv("DB_TYPE")
        self.db_type = raw_type.lower() if raw_type else None

        self.connection = None
        self._auto_connect()

    def _load_env(self, env_path: str):
        load_dotenv(dotenv_path=env_path)

    def _determine_candidate_types(self) -> list[tuple[str, int]]:
        if self.db_type:
            port = self.db_port or (5432 if self.db_type == "postgres" else 3306)
            return [(self.db_type, port)]

        if self.db_port == 3306:
            return [("mysql", 3306), ("postgres", 5432)]
        if self.db_port == 5432:
            return [("postgres", 5432), ("mysql", 3306)]

        return [("postgres", 5432), ("mysql", 3306)]

    def _try_postgres(self, port: int, password: str) -> bool:
        try:
            import psycopg2
            self.connection = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=password,
                host=self.db_addr,
                port=port,
                connect_timeout=3
            )
            return True
        except Exception:
            return False

    def _try_mysql(self, port: int, password: str) -> bool:
        try:
            import pymysql
            self.connection = pymysql.connect(
                database=self.db_name,
                user=self.db_user,
                password=password,
                host=self.db_addr,
                port=port,
                connect_timeout=3
            )
            return True
        except Exception:
            return False

    def _auto_connect(self):
        candidates = self._determine_candidate_types()

        for db_t, port in candidates:
            passwords_to_test = [self.db_passwd]
            if self.db_passwd:
                passwords_to_test.append("")

            for pwd in passwords_to_test:
                success = False
                if db_t in ("postgres", "postgresql"):
                    success = self._try_postgres(port, pwd)
                elif db_t in ("mysql", "mariadb"):
                    success = self._try_mysql(port, pwd)

                if success:
                    self.db_type = db_t
                    self.db_port = port
                    self.db_passwd = pwd
                    print(f"[+] Connecté avec succès ({self.db_type.upper()}) sur {self.db_addr}:{self.db_port}")
                    return

        raise ConnectionError(
            f"Impossible de se connecter à '{self.db_name}' sur {self.db_addr} avec les identifiants testés."
        )

    def execute_query(self, query: str, params: tuple | dict = None):
        """
        Exécute une requête SQL transmise sous forme de chaîne.
        - Si c'est une lecture (SELECT), renvoie une liste de dictionnaires.
        - Si c'est une écriture (INSERT, UPDATE, DELETE, etc.), commit et renvoie le nombre de lignes affectées.
        """
        if not self.connection:
            raise ConnectionError("Pas de connexion active à la base de données.")

        with self.connection.cursor() as cursor:
            cursor.execute(query, params or ())

            # Si cursor.description n'est pas None, la requête renvoie des données (ex: SELECT)
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            else:
                # Modifiante : validation des changements (commit)
                self.connection.commit()
                return cursor.rowcount

    def execute_file(self, file_path: str):
        """
        Lit un fichier .sql et exécute toutes les requêtes qu'il contient.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Le fichier SQL '{file_path}' n'existe pas.")

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Découpage par point-virgule en ignorant les blocs vides
        statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]

        results = []
        for statement in statements:
            res = self.execute_query(statement)
            results.append(res)

        return results

    def close(self):
        """Ferme proprement la connexion."""
        if self.connection:
            self.connection.close()
            print("[*] Connexion fermée.")
