import streamlit as st
import pandas as pd
import pydeck as pdk
from PIL import Image # Nuova importazione per gestire le immagini
import os # Utile per verificare se il file esiste

ICON_URL = "https://img.icons8.com/color/48/000000/parking--v1.png" #cambia ad icona locale
IMAGE_PATH = "img/" # Cartella dove tieni le foto E i topos PNG
TOPO_PATH = "topos/" # Cartella dove tieni i topos PNG
GRADES = ['3', '4', '5A', '5B', '5C', '6A', '6A+', '6B', '6B+', '6C', '6C+', '7A', '7A+', '7B', '7B+', '7C', '7C+', '8A', '8A+', '8B', '8B+', '8C', '8C+', '9A']
PALETTE = [
    [0, 255, 0, 160],
    [255, 0, 0, 160],
    [0, 0, 255, 160],
    [255, 255, 0, 160],
    [255, 0, 255, 160],
    [0, 255, 255, 160],
    [255, 128, 0, 160],
]

st.title("Sugano Boulder")

col1, col2 = st.columns(2)
with col1:
    show_parks = st.checkbox("Mostra parcheggi", value=True)
with col2:
    show_blocks = st.checkbox("Mostra blocchi", value=True)

parcheggi = pd.read_csv("parcheggi.csv")
boulder_data = pd.read_csv("blocchi.csv")
settori = boulder_data["settore"].unique()

boulder_data['color'] = boulder_data['settore'].map({settore: color for i, (settore, color) in enumerate(zip(settori, PALETTE))})

icon_data = {
    "url": ICON_URL,
    "width": 128,
    "height": 128,
    "anchorY": 128,
}

# Aggiungiamo la colonna "icon_data"
parcheggi["icon_data"] = [icon_data for _ in range(len(parcheggi))]

# Configurazione del layer delle icone
icon_layer = pdk.Layer(
    type="IconLayer",
    data=parcheggi,
    get_icon="icon_data",
    get_size=4,
    size_scale=5,
    get_position=["lon", "lat"],
    pickable=True, #Aggiungi link maps on click
)

block_layer = pdk.Layer(
    type="ScatterplotLayer",
    data=boulder_data,
    get_radius=10,
    get_fill_color="color",
    get_position=["lon", "lat"],
)

# Vista iniziale della mappa
if not parcheggi.empty:
    view_state = pdk.ViewState(
        latitude=parcheggi["lat"].mean(),
        longitude=parcheggi["lon"].mean(),
        zoom=15,
        pitch=0,
    )
else:
    view_state = pdk.ViewState(latitude=0, longitude=0, zoom=1)

layer_list = []
if show_parks:
    layer_list.append(icon_layer)
if show_blocks:
    layer_list.append(block_layer)

# Rendering della mappa
st.pydeck_chart(pdk.Deck(
    layers=layer_list,
    initial_view_state=view_state,
))


# --- SEZIONE TOPOS E FILTRI ---
st.header("Topos")

# Interfaccia filtri
col1, col2 = st.columns([1, 3]) # Organizziamo i filtri su due colonne
with col1:
    filtraggio = st.checkbox("Abilita filtri di difficoltà/tag")

if filtraggio:
    with col2:
        range_gradi = st.select_slider(
            "Seleziona range difficoltà",
            options=GRADES,
            value=('3', '9A')
        )
        boulder_tags = st.multiselect(
            "Seleziona tag",
            options=['sosta', 'strapiombo', 'tetto', 'placca', 'fessura', 'liscio', 'appigli piccoli', 'appigli grandi']
        )
else:
    # Valori di default se il filtro è disattivato
    range_gradi = ('3', '9A')
    boulder_tags = []

# Selezione Settore
selected_sector = st.selectbox("Scegli un settore", options=settori)

st.subheader(f"Lista dei blocchi - {selected_sector}")

# --- LOGICA DI FILTRAGGIO AVANZATA ---
mask = (boulder_data['settore'] == selected_sector)

if filtraggio:
    # Filtro Grado (confronto stringhe basato sull'ordine nella lista GRADES)
    idx_min = GRADES.index(range_gradi[0])
    idx_max = GRADES.index(range_gradi[1])
    # Questa logica di confronto stringhe >= <= è fragile se GRADES non è ordinato perfettamente.
    # Funziona solo se il CSV usa ESATTAMENTE le stesse stringhe di GRADES.
    mask &= boulder_data['grado'].apply(lambda x: x in GRADES and idx_min <= GRADES.index(x) <= idx_max)

    # Filtro Tag (mostra il blocco se ha ALMENO UNO dei tag selezionati)
    if boulder_tags:
        # Assumiamo che nel CSV i tag siano separati da virgola, es: "placca,liscio"
        mask &= boulder_data['tag'].apply(lambda x: any(tag in str(x).split(',') for tag in boulder_tags))


# --- VISUALIZZAZIONE BLOCCHI CON SOVRAPPOSIZIONE TOPOS ---
blocchi_da_mostrare = boulder_data[mask]

if blocchi_da_mostrare.empty:
    st.info("Nessun blocco corrisponde ai filtri selezionati in questo settore.")
else:
    for index, row in blocchi_da_mostrare.iterrows():
        with st.container():
            st.markdown(f"### {row['nome']}")
            st.markdown(f"**Grado:** {row['grado']} | **Tag:** {row['tag']}")
            
            # 1. Recupero foto base (stringa sicura)
            img_foto_path = os.path.join(IMAGE_PATH, str(row['immagine']))

            st.image(img_foto_path)
            
            st.markdown("---")