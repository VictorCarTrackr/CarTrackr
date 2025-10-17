from fastapi import FastAPI
from pathlib import Path
import sqlite3

app = FastAPI()


#Pad instellingen
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
db_path = current_dir / "Database" / "carMakeModels.db"


#API endpoint om merken op te halen
@app.get("/merken")
def get_merken():
    #Connectie met database
    connection = sqlite3.connect(db_path)
    c = connection.cursor()
    c.execute("SELECT DISTINCT Company_Names FROM cars ORDER BY Company_Names")
    merken = [row[0] for row in c.fetchall()]
    connection.close()
    return {"merken": merken}


@app.get("/modellen/{merk}")
def get_modellen(merk: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "SELECT Cars_Names FROM cars WHERE Company_Names = ? ORDER BY Cars_Names",(merk,))
    modellen = [row[0] for row in c.fetchall()]
    conn.close()
    return {"modellen": modellen}


@app.get("/brandstoftype/{model}")
def get_brandstoftype(model: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "SELECT DISTINCT Fuel_Types FROM cars WHERE Cars_Names = ? ORDER BY Fuel_Types",(model,))
    brandstoftype = c.fetchone()
    conn.close()
    if brandstoftype:
        return {"brandstoftype": brandstoftype[0]}
    else:
        return {"brandstoftype": None}

