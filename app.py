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

st.set_page_config(page_title="Sugano Boulder", layout="wide")
st.title("Sugano Boulder")

# --- CARICAMENTO DATI ---
@st.cache_data
def load_data():
    parks = pd.read_csv("parcheggi.csv")
    blocks = pd.read_csv("blocchi.csv")
    # Assegnazione colori ai settori
    settori_list = sorted(blocks["settore"].unique())
    color_map = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(settori_list)}
    blocks['color'] = blocks['settore'].map(color_map)
    return parks, blocks, settori_list

parcheggi, boulder_data, settori = load_data()

# --- LOGICA DI SELEZIONE ---
# Inizializziamo il settore nel session_state se non esiste
if 'selected_sector' not in st.session_state:
    st.session_state.selected_sector = settori[0]

# --- SIDEBAR / CONTROLLI MAPPA ---
col1, col2 = st.columns(2)
with col1:
    show_parks = st.checkbox("Mostra parcheggi", value=True)
with col2:
    show_blocks = st.checkbox("Mostra blocchi", value=True)

# --- PREPARAZIONE LAYER PYDECK ---
layer_list = []

if show_parks:
    icon_data = {"url": ICON_URL, "width": 128, "height": 128, "anchorY": 128}
    parcheggi["icon_data"] = [icon_data for _ in range(len(parcheggi))]
    
    icon_layer = pdk.Layer(
        "IconLayer",
        data=parcheggi,
        get_icon="icon_data",
        get_size=4,
        size_scale=5,
        get_position=["lon", "lat"],
        pickable=False, # <--- DISATTIVA HOVER/CLICK SUI PARCHEGGI
    )
    layer_list.append(icon_layer)

if show_blocks:
    block_layer = pdk.Layer(
        "ScatterplotLayer",
        data=boulder_data,
        get_radius=12,
        get_fill_color="color",
        get_position=["lon", "lat"],
        pickable=True, # <--- ATTIVO PER I BLOCCHI
    )
    layer_list.append(block_layer)

view_state = pdk.ViewState(
    latitude=boulder_data["lat"].mean(),
    longitude=boulder_data["lon"].mean(),
    zoom=15, pitch=0
)

# Rendering della mappa con selezione abilitata
# Il tooltip mostra dati solo se esiste la colonna 'sasso' (presente nei blocchi, non nei parcheggi)
# Sostituisci il vecchio blocco con questo:
deck_chart = st.pydeck_chart(
    pdk.Deck(
        layers=layer_list,
        initial_view_state=view_state,
        tooltip={
            "html": "<b>{nome}</b><br>Grado: {grado}", 
            "style": {"backgroundColor": "steelblue", "color": "white"}
        },
        map_style="mapbox://styles/mapbox/outdoors-v12",
    ),
    on_select="rerun"  # <--- Questo abilita la selezione automaticamente
)

# Verifica se il click funziona
if deck_chart and deck_chart.selection:
    selection = deck_chart.selection.get("objects", {})
    if "scatterplot" in selection and len(selection["scatterplot"]) > 0:
        st.session_state.selected_sector = selection["scatterplot"][0]["settore"]
        print(f"Settore selezionato: {st.session_state.selected_sector}")

# --- FILTRI E LISTA ---
st.divider()
st.header(f"Esplora i Blocchi")

# Il selectbox legge e scrive nel session_state
selected_sector = st.selectbox(
    "Scegli un settore", 
    options=settori, 
    key="selected_sector" 
)

col1, col2 = st.columns([1, 3])
with col1:
    filtraggio = st.checkbox("Attiva Filtri Avanzati")

if filtraggio:
    with col2:
        c1, c2 = st.columns(2)
        range_gradi = c1.select_slider("Difficoltà", options=GRADES, value=('3', '9A'))
        all_tags = set([t.strip() for sublist in boulder_data['tag'].dropna().str.split(',') for t in sublist])
        boulder_tags = c2.multiselect("Filtra per Tag", options=sorted(list(all_tags)))
else:
    range_gradi = ('3', '9A')
    boulder_tags = []

# --- FILTRAGGIO DATI ---
mask = (boulder_data['settore'] == selected_sector)

if filtraggio:
    idx_min, idx_max = GRADES.index(range_gradi[0]), GRADES.index(range_gradi[1])
    mask &= boulder_data['grado'].apply(lambda x: x in GRADES and idx_min <= GRADES.index(x) <= idx_max)
    if boulder_tags:
        mask &= boulder_data['tag'].apply(lambda x: any(tag in str(x) for tag in boulder_tags))

blocchi_da_mostrare = boulder_data[mask]

# --- VISUALIZZAZIONE ---
if blocchi_da_mostrare.empty:
    st.info("Nessun blocco trovato con questi criteri.")
else:
    for _, row in blocchi_da_mostrare.iterrows():
        with st.expander(f"{row['nome']} ({row['grado']})", expanded=True):
            col_txt, col_img = st.columns([1, 1])
            with col_txt:
                st.write(f"**Settore:** {row['settore']}")
                st.write(f"**Tag:** {row['tag']}")
                st.write(f"**Descrizione:** {row.get('descrizione', 'Nessuna descrizione')}")
            with col_img:
                img_path = os.path.join(IMAGE_PATH, str(row['immagine']))
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                else:
                    st.warning(f"Immagine non trovata: {row['immagine']}")