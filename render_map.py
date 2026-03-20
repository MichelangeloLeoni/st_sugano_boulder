import streamlit as st
import pydeck as pdk

ICON_URL = "https://img.icons8.com/color/48/000000/parking--v1.png"

@st.fragment
def render_map(parcheggi, boulder_data):
    col1, col2 = st.columns(2)
    with col1:
        show_parks = st.checkbox("Mostra parcheggi", value=True)
    with col2:
        show_blocks = st.checkbox("Mostra blocchi", value=True)

    # --- LOGICA UNICITÀ SASSI ---
    # 1. Contiamo quante vie ci sono per sasso per il tooltip
    vie_per_sasso = boulder_data.groupby('sasso')['nome'].count().reset_index(name='num_vie')
    
    # 2. Teniamo solo una riga per ogni sasso fisico
    unique_boulders = boulder_data.drop_duplicates(subset=['sasso', 'lat', 'lon']).copy()
    
    # 3. Uniamo il conteggio al dataframe unico
    unique_boulders = unique_boulders.merge(vie_per_sasso, on='sasso')

    # Configurazione Icone Parcheggi
    icon_data = {"url": ICON_URL, "width": 128, "height": 128, "anchorY": 128}
    parcheggi["icon_data"] = [icon_data for _ in range(len(parcheggi))]

    icon_layer = pdk.Layer(
        "IconLayer",
        data=parcheggi,
        get_icon="icon_data",
        get_size=4,
        size_scale=5,
        get_position=["lon", "lat"],
    )

    block_layer = pdk.Layer(
        "ScatterplotLayer",
        data=unique_boulders, # Usiamo i dati filtrati senza duplicati
        get_radius=12,
        get_fill_color="color", # Rosso acceso semi-trasparente
        get_position=["lon", "lat"],
        pickable=True,
    )

    # Centro mappa
    p_mean = parcheggi[["lat", "lon"]].mean() if not parcheggi.empty else {"lat": 0, "lon": 0}
    b_mean = unique_boulders[["lat", "lon"]].mean() if not unique_boulders.empty else {"lat": 0, "lon": 0}
    
    view_state = pdk.ViewState(
        latitude=(p_mean["lat"] + b_mean["lat"]) / 2,
        longitude=(p_mean["lon"] + b_mean["lon"]) / 2,
        zoom=15,
        pitch=0,
    )

    layers = []
    if show_parks: layers.append(icon_layer)
    if show_blocks: layers.append(block_layer)

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip={
            "html": "<b>Sasso:</b> {sasso}<br/>"
                    "<b>Settore:</b> {settore}<br/>"
                    "<b>Vie totali:</b> {num_vie}",
            "style": {"color": "white", "backgroundColor": "#262730"}
        }
    )

    st.pydeck_chart(deck)