import streamlit as st
import kagglehub as kh
import sqlite3
import os


#Connectie met database
db_path = os.path.join("Database", "carMakeModels.db")
connection = sqlite3.connect(db_path)
c = connection.cursor()


@st.cache_data
def qeury_db():
    c.execute("SELECT DISTINCT Company_Names FROM cars ORDER BY Company_Names")
    merken = [row[0] for row in c.fetchall()]
    return merken

geselecteerdMerk, geselecteerdModel, verbruik = st.columns(3, vertical_alignment="bottom")

merken = qeury_db()
geselecteerdMerk = geselecteerdMerk.selectbox("Kies een merk", merken, index=None, placeholder="Kies een merk")

if geselecteerdMerk:
    c.execute("SELECT Cars_Names FROM cars WHERE Company_Names = ? ORDER BY Cars_Names", (geselecteerdMerk,))
    modellen = [row[0] for row in c.fetchall()]
else:
    modellen = []

geselecteerdModel = geselecteerdModel.selectbox("Kies een model", modellen, index=None, placeholder="Kies een model")

verbruik = verbruik.number_input("Kies een verbruik (l/100km) of (kwh/100km)", min_value=0.0, step=1.0, placeholder=0.00) #TODO: als je er op klikt moeten de nullen weggaan
