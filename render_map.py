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

    parks_mean = parcheggi[["lat", "lon"]].mean()
    boulder_mean = boulder_data[["lat", "lon"]].mean()

    # Vista iniziale della mappa
    if not parcheggi.empty:
        view_state = pdk.ViewState(
            latitude=(parks_mean["lat"] + boulder_mean["lat"]) / 2,
            longitude=(parks_mean["lon"] + boulder_mean["lon"]) / 2,
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
