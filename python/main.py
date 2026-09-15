from db_conf import AutoDB

# Exemple 1 : Connexion automatique basée uniquement sur le .env
db = AutoDB()

# Exemple 2 : Connexion en surchargeant le port ou l'utilisateur
# db = AutoDB(db_name="prod_db", db_addr="192.168.1.50")

print(f"Base retenue : {db.db_type} sur le port {db.db_port} avec l'user '{db.db_user}'")

incidents = db.execute_query("SELECT * FROM incident ORDER BY id DESC LIMIT 10")
#print("Résultat incidents : ", incidents)
for item in incidents:
    print("==== incident N° "+str(item["id"])+"====")
    print("Date : "+str(item["date"]))
    print()
