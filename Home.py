from pathlib import Path
import streamlit as st
import pandas as pd
import requests



#Pad settings
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file = current_dir / "styles" / "main.css"


#CSS laden
with open(css_file) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


#Pagina settings en variabelen
paginaTitel = "CarTrackr"
favicon = ":red_car:"
benzinePrijs = 1.85  #Prijs per liter benzine
dieselPrijs = 1.75   #Prijs per liter diesel
electriciteitPrijs = 0.40  #Prijs per kWh elektriciteit
baseUrl = "http://127.0.0.1:8000" #API basis URL



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
    try:
        response = requests.get(f"{baseUrl}/merken")
        response.raise_for_status()
        return response.json().get("merken", [])
    except Exception as e:
        st.error(f"Fout bij ophalen van merken: {e}")
        return []
    

geselecteerdMerk, geselecteerdModel, verbruik, aantalKm = st.columns(4, vertical_alignment="bottom")

merken = queryMerken_db()

geselecteerdMerk = geselecteerdMerk.selectbox("Kies een merk", merken, index=None, placeholder="Kies een merk")


@st.cache_data
def queryModellen_db(geselecteerdMerk):
    r = requests.get(f"{baseUrl}/modellen/{geselecteerdMerk}")
    return r.json().get("modellen", []) if r.status_code == 200 else []


modellen = queryModellen_db(geselecteerdMerk)

geselecteerdModel = geselecteerdModel.selectbox("Kies een model", modellen, index=None, placeholder="Kies een model")

verbruik = verbruik.number_input("Geef een verbruik in (l/100km) of (kwh/100km)", min_value=0.00, step=1.00, placeholder=0.00, value = None) 

aantalKm = aantalKm.number_input("Geef het aantal kilometers van je auto in", min_value=0, step=1, placeholder=0, value = None)

@st.cache_data
def queryBrandstof_db(geselecteerdModel):
    r = requests.get(f"{baseUrl}/brandstoftype/{geselecteerdModel}")
    return r.json().get("brandstoftype", None) if r.status_code == 200 else None


brandstofType = queryBrandstof_db(geselecteerdModel)


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