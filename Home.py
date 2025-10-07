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

geselecteerdMerk, geselecteerdModel = st.columns(2, vertical_alignment="bottom")

merken = qeury_db()
geselecteerdMerk = geselecteerdMerk.selectbox("Kies een merk", merken, index=None, placeholder="Kies een merk")

if geselecteerdMerk:
    c.execute("SELECT Cars_Names FROM cars WHERE Company_Names = ? ORDER BY Cars_Names", (geselecteerdMerk,))
    modellen = [row[0] for row in c.fetchall()]
else:
    modellen = []

geselecteerdModel = geselecteerdModel.selectbox("Kies een model", modellen, index=None, placeholder="Kies een model")

#merken, modelen = qeury_db()
#merk, model = st.columns(2, vertical_alignment="bottom")
#merk.selectbox("Selecteer een merk", options=merken, index=None, placeholder="Kies een merk")
#model.selectbox("Selecteer een model", options=modelen, index=None, placeholder="Kies een model")
