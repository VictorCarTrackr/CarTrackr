from pathlib import Path
import streamlit as st
import sqlite3
import pandas as pd



#Pad settings
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file = current_dir / "styles" / "main.css"
db_path = current_dir / "Database" / "carMakeModels.db"


#Connectie met database
connection = sqlite3.connect(db_path)
c = connection.cursor()


#CSS laden
with open(css_file) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


#Pagina settings en variabelen
paginaTitel = "CarTrackr"
favicon = ":red_car:"
benzinePrijs = 1.85  #Prijs per liter benzine
dieselPrijs = 1.75   #Prijs per liter diesel
electriciteitPrijs = 0.40  #Prijs per kWh elektriciteit


st.set_page_config(page_title=paginaTitel, page_icon=favicon, layout="wide")

with st.sidebar:
    #Login met microsoft
    if not st.user.is_logged_in:
        st.button("Login met microsoft", on_click=lambda:st.login("microsoft"))
    else:
        st.write(f"Welkom {st.user.name}!")
        st.button("Log uit", on_click=lambda:st.logout())


st.title("Voeg je auto toe!")
st.markdown("Vul de gegevens van je auto in en start met het bijhouden van je auto statistieken.")


#* Input velden
#Functie om merken op te halen uit database
@st.cache_data
def queryMerken_db():
    c.execute("SELECT DISTINCT Company_Names FROM cars ORDER BY Company_Names")
    merken = [row[0] for row in c.fetchall()]
    return merken

geselecteerdMerk, geselecteerdModel, verbruik, aantalKm = st.columns(4, vertical_alignment="bottom")

merken = queryMerken_db()

geselecteerdMerk = geselecteerdMerk.selectbox("Kies een merk", merken, index=None, placeholder="Kies een merk")

if geselecteerdMerk:
    c.execute("SELECT Cars_Names FROM cars WHERE Company_Names = ? ORDER BY Cars_Names", (geselecteerdMerk,))
    modellen = [row[0] for row in c.fetchall()]
else:
    modellen = []

geselecteerdModel = geselecteerdModel.selectbox("Kies een model", modellen, index=None, placeholder="Kies een model")

verbruik = verbruik.number_input("Geef een verbruik in (l/100km) of (kwh/100km)", min_value=0.00, step=1.00, placeholder=0.00, value = None) 

aantalKm = aantalKm.number_input("Geef het aantal kilometers van je auto in", min_value=0, step=1, placeholder=0, value = None)

if modellen:
    brandstofType = c.execute("SELECT DISTINCT Fuel_Types FROM cars WHERE Cars_Names = ? ORDER BY Fuel_Types", (geselecteerdModel,)).fetchone()
    if brandstofType:
        brandstofType = brandstofType[0]
    else:
        brandstofType = None
else:
    brandstofType = None

#Functie om brandstofkosten te berekenen
def totaalKostenBerekenen(totaalVerbruik, brandstofType):
    if brandstofType == "Petrol" or brandstofType == "Plug-in Hybrid":
        totaalKosten = totaalVerbruik * benzinePrijs
        st.markdown(f"Je benzine kosten zijn ongeveer €{totaalKosten:,.2f}")
        brandstofType = "Benzine"
        st.markdown(f"Je hebt een {brandstofType} auto.")
    elif brandstofType == "Diesel":
        totaalKosten = totaalVerbruik * dieselPrijs
        st.markdown(f"Je diesel kosten zijn ongeveer €{totaalKosten:,.2f}")
        st.markdown("Je hebt een diesel auto.")
        brandstofType = "Diesel"
        st.markdown(f"Je hebt een {brandstofType} auto.")
    else:
        totaalKosten = totaalVerbruik * electriciteitPrijs
        st.markdown(f"Je elektriciteits kosten zijn ongeveer €{totaalKosten:,.2f}")
        st.markdown("Je hebt een elektrische of semi elektrische auto.")
        brandstofType = "Elektriciteit"
        st.markdown(f"Je hebt een {brandstofType} auto.")
    return totaalKosten, brandstofType

def submitButton(geselecteerdModel, verbruik, aantalKm, brandstofType):
    if geselecteerdMerk and geselecteerdModel and verbruik is not None and aantalKm is not None:
        #Statistieken berekenen
        totaalVerbruik = (verbruik / 100) * aantalKm
        if verbruik <= 0:
            st.error("Het verbruik moet groter zijn dan 0.")
        else:
            totaalKosten, brandstofType = totaalKostenBerekenen(totaalVerbruik, brandstofType)
            st.markdown(f"Je hebt al ongeveer {totaalVerbruik:,.2f} liter verbruikt voor {aantalKm:,.2f} kilometer.")
            tabel = {
                "Merk": geselecteerdMerk,
                "Model": geselecteerdModel,
                "Brandstof type": brandstofType,
                "Verbruik (l/100km) of (kwh/100km)": float(verbruik),
                "Aantal kilometers": int(aantalKm),
                "Totaal verbruik (l) of (kwh)": float(totaalVerbruik),
                "Totaal kosten (€)": float(totaalKosten)
            }
            df = pd.DataFrame([tabel], index=None)
            st.write(df)
            kostenGrafiek, kilometerGrafiek = st.columns(2, vertical_alignment="bottom", gap="large")
            with kilometerGrafiek:
                st.bar_chart(df.loc[:, ["Totaal verbruik (l) of (kwh)", "Model"]].set_index("Model"), height=400)
            with kostenGrafiek:
                st.bar_chart(df.loc[:, ["Totaal kosten (€)", "Model"]].set_index("Model"),  height=400)
    else:
        st.error("Vul alle velden in om de statistieken te berekenen.")


#Statistieken knop
if st.button("Bereken statistieken van je auto!"):
    submitButton(geselecteerdModel, verbruik, aantalKm, brandstofType)