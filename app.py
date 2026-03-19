import streamlit as st
import pandas as pd
import pydeck as pdk
from PIL import Image

st.set_page_config(layout="wide")

st.title("🧗‍♂️ Guida Boulder Interattiva")
st.write("Venite a fare sassi a Sugano!!!")

# ----------------------
# CARICAMENTO DATI
# ----------------------
@st.cache_data
def load_data():
    return pd.read_csv("blocchi.csv")

df = load_data()

# ----------------------
# FILTRO
# ----------------------
st.sidebar.header("Filtri")

gradi = sorted(df["grado"].unique())
grado_sel = st.sidebar.selectbox("Seleziona grado", gradi)

filtered = df[df["grado"] == grado_sel]

# ----------------------
# LAYOUT
# ----------------------
col1, col2 = st.columns([1, 1])

# ----------------------
# MAPPA
# ----------------------
with col1:
    st.subheader("📍 Mappa blocchi")

    if not filtered.empty:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=30,
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=filtered["lat"].mean(),
            longitude=filtered["lon"].mean(),
            zoom=15
        )

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{nome} ({grado}) - {settore}"}
        ))
    else:
        st.warning("Nessun blocco trovato")

# ----------------------
# SELEZIONE BLOCCO
# ----------------------
with col2:
    st.subheader("🪨 Dettaglio blocco")

    if not filtered.empty:
        blocco_nome = st.selectbox("Scegli blocco", filtered["nome"])

        b = filtered[filtered["nome"] == blocco_nome].iloc[0]

        # Immagine con overlay
        try:
            base = Image.open(b["immagine"])
            overlay = Image.open(b["topo"])

            base = base.convert("RGBA")
            overlay = overlay.convert("RGBA")

            base.paste(overlay, (0, 0), overlay)

            st.image(base, caption=blocco_nome)

        except:
            st.image(b["immagine"], caption=blocco_nome)

        st.write(f"**Grado:** {b['grado']}")
        st.write(f"**Settore:** {b['settore']}")
        st.write(b["descrizione"])
    else:
        st.info("Seleziona un grado per vedere i blocchi")