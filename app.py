import streamlit as st
import pandas as pd
import pydeck as pdk

st.title("Sugano Boulder")
st.header("Mappa dei settori")

# Caricamento dati
# Assicurati che il CSV abbia le colonne 'lat' e 'lon'
parcheggi = pd.read_csv("parcheggi.csv")

# Definiamo l'icona (puoi usare un URL di un'immagine PNG)
# Ecco un esempio di icona standard per il parcheggio
ICON_URL = "https://img.icons8.com/color/48/000000/parking--v1.png"
IMAGE_PATH = "img/"
GRADES = ['3', '4', '5A', '5B', '5C', '6A', '6A+', '6B', '6B+', '6C', '6C+', '7A', '7A+', '7B', '7B+', '7C', '7C+', '8A', '8A+', '8B', '8B+', '8C', '8C+', '9A']

icon_data = {
    "url": ICON_URL,
    "width": 128,
    "height": 128,
    "anchorY": 128,
}

# Aggiungiamo la colonna "icon_data" al dataframe dei parcheggi
parcheggi["icon_data"] = [icon_data for _ in range(len(parcheggi))]

# Configurazione del layer delle icone
icon_layer = pdk.Layer(
    type="IconLayer",
    data=parcheggi,
    get_icon="icon_data",
    get_size=4,
    size_scale=10,
    get_position=["lon", "lat"],
    pickable=True,
)

# Vista iniziale della mappa
view_state = pdk.ViewState(
    latitude=parcheggi["lat"].mean(),
    longitude=parcheggi["lon"].mean(),
    zoom=14,
    pitch=0,
)

# Rendering della mappa
st.pydeck_chart(pdk.Deck(
    layers=[icon_layer],
    initial_view_state=view_state,
))

# Leggiamo il file PDF
with open("guida_sugano_boulder.pdf", "rb") as pdf_file:
    PDFbyte = pdf_file.read()

# Creiamo il bottone
st.download_button(
    label="📄 Scarica la Guida Boulder (PDF)",
    data=PDFbyte,
    file_name="Guida_Sugano_Boulder.pdf",
    mime="application/pdf"
)

st.header("Topos")

filtraggio = st.checkbox("Abilita filtri")
if filtraggio:
    range_gradi = st.select_slider(
        "Seleziona difficoltà",
        options=GRADES,
        value=('3', '9A') # Range di default
    )
    boulder_tags = st.multiselect(
        "Seleziona tag",
        options=['sosta', 'strapiombo', 'tetto', 'placca', 'fessura', 'liscio', 'appigli piccoli', 'appigli grandi']
    )

boulder_data = pd.read_csv("blocchi.csv")
settori = boulder_data["settore"].unique()
selected_sector = st.selectbox("Scegli un settore", options=settori)

st.subheader("Lista dei blocchi")

blocchi_filtrati = (boulder_data['settore'] == selected_sector )
if filtraggio:
    blocchi_filtrati &= (boulder_data['grado'] >= range_gradi[0]) & (boulder_data['grado'] <= range_gradi[1])

for index, row in boulder_data[blocchi_filtrati].iterrows():
    st.markdown(f"**{row['nome']}** - {row['grado']} - {row['tag']}")
    st.image(f"{IMAGE_PATH}{row['immagine']}")