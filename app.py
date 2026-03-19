import streamlit as st
import pandas as pd
import pydeck as pdk
import os

# --- CONFIGURAZIONE E COSTANTI ---
ICON_URL = "https://img.icons8.com/color/48/000000/parking--v1.png"
IMAGE_PATH = "img/" 
GRADES = ['3', '4', '5A', '5B', '5C', '6A', '6A+', '6B', '6B+', '6C', '6C+', '7A', '7A+', '7B', '7B+', '7C', '7C+', '8A', '8A+', '8B', '8B+', '8C', '8C+', '9A']
PALETTE = [
    [0, 255, 0, 160], [255, 0, 0, 160], [0, 0, 255, 160],
    [255, 255, 0, 160], [255, 0, 255, 160], [0, 255, 255, 160], [255, 128, 0, 160],
]

# --- CARICAMENTO DATI ---
@st.cache_data
def load_data():
    parks = pd.read_csv("parcheggi.csv")
    blocks = pd.read_csv("blocchi.csv")
    # Assegnazione colori ai settori
    settori_list = sorted(blocks["settore"].unique())
    settori_list = ["Tutti"] + settori_list # Aggiungiamo "Tutti" come prima opzione
    color_map = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(settori_list)}
    blocks['color'] = blocks['settore'].map(color_map)
    grade_to_int = {grade: i for i, grade in enumerate(GRADES)}
    blocks['grade_rank'] = blocks['grado'].map(grade_to_int)
    # Calco il grado minimo e massimo assoluto per i blocchi, così da poter impostare i valori di default dello slider
    min_grade = blocks['grade_rank'].min()
    max_grade = blocks['grade_rank'].max()
    return parks, blocks, settori_list, grade_to_int, min_grade, max_grade

parcheggi, boulder_data, settori, grade_to_int, min_grade, max_grade = load_data()

st.title("Sugano Boulder")

col1, col2 = st.columns(2)
with col1:
    show_parks = st.checkbox("Mostra parcheggi", value=True)
with col2:
    show_blocks = st.checkbox("Mostra blocchi", value=True)

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
    pickable=False, #Aggiungi link maps on click
)

block_layer = pdk.Layer(
    type="ScatterplotLayer",
    data=boulder_data,
    get_radius=10,
    get_fill_color="color",
    get_position=["lon", "lat"],
    pickable=True,
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
deck = pdk.Deck(
    layers=layer_list,
    initial_view_state=view_state,
    tooltip={
        "html": "<b>{sasso}</b><br>Settore: {settore}<br>",
        "style": {"color": "white"}
    }
)

st.pydeck_chart(deck)

# Selezione Settore
st.header(f"Lista dei blocchi")
selected_sector = st.selectbox("Scegli un settore", options=settori, index=0) # "Tutti" è l'opzione di default

# Interfaccia filtri
col1, col2 = st.columns([2, 3]) # Organizziamo i filtri su due colonne
with col1:
    filtraggio = st.checkbox("Attiva filtri avanzati")

if filtraggio:
    with col2:
        range_gradi = st.select_slider(
            "Seleziona range difficoltà",
            options=GRADES[min_grade:max_grade+1], # +1 perché l'endpoint è esclusivo
            value=(GRADES[min_grade], GRADES[max_grade])
        )
        boulder_tags = st.multiselect(
            "Seleziona tag",
            options=['sosta', 'strapiombo', 'tetto', 'placca', 'fessura', 'liscio', 'appigli piccoli', 'appigli grandi']
        )
else:
    # Valori di default se il filtro è disattivato
    range_gradi = (GRADES[min_grade], GRADES[max_grade])
    boulder_tags = []

# --- LOGICA DI FILTRAGGIO AVANZATA ---
mask = pd.Series([True] * len(boulder_data))  # Inizialmente tutti i blocchi sono selezionati
if selected_sector != "Tutti":
    mask = (boulder_data['settore'] == selected_sector)

if filtraggio:
    # Filtro Grado (confronto stringhe basato sull'ordine nella lista GRADES)
    idx_min = grade_to_int[range_gradi[0]]
    idx_max = grade_to_int[range_gradi[1]]
    mask &= boulder_data['grade_rank'].between(idx_min, idx_max)

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