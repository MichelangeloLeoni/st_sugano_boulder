import streamlit as st
import pandas as pd
import pydeck as pdk
from PIL import Image

st.set_page_config(layout="wide")

st.title("🧗‍♂️ Guida Boulder Interattiva")

# ----------------------
# CARICAMENTO DATI
# ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("blocchi.csv")
    return df

df = load_data()

# ----------------------
# GESTIONE GRADI (ordine)
# ----------------------
grado_order = [
    "5A", "5B", "5C",
    "6A", "6A+",
    "6B", "6B+",
    "6C", "6C+",
    "7A", "7A+",
    "7B", "7B+",
    "7C", "7C+",
    "8A"
]

grado_to_num = {g: i for i, g in enumerate(grado_order)}
num_to_grado = {i: g for g, i in grado_to_num.items()}

# mappa i gradi nel dataframe
df = df[df["grado"].isin(grado_order)].copy()
df["grado_num"] = df["grado"].map(grado_to_num)

# ----------------------
# SIDEBAR - FILTRI
# ----------------------
st.sidebar.header("🎯 Filtri")

min_val = int(df["grado_num"].min())
max_val = int(df["grado_num"].max())

range_sel = st.sidebar.slider(
    "Seleziona range gradi",
    min_val,
    max_val,
    (min_val, max_val)
)

# mostra range leggibile
st.sidebar.write(
    f"Da **{num_to_grado[range_sel[0]]}** a **{num_to_grado[range_sel[1]]}**"
)

# filtro
filtered = df[
    (df["grado_num"] >= range_sel[0]) &
    (df["grado_num"] <= range_sel[1])
]

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

        # colore per settore (semplice hash)
        filtered["color"] = filtered["settore"].apply(
            lambda x: [hash(x) % 255, 100, 200]
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered,
            get_position='[lon, lat]',
            get_color='color',
            get_radius=40,
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
        st.warning("Nessun blocco nel range selezionato")

# ----------------------
# DETTAGLIO BLOCCO
# ----------------------
with col2:
    st.subheader("🪨 Dettaglio blocco")

    if not filtered.empty:

        blocco_nome = st.selectbox("Scegli blocco", filtered["nome"])

        b = filtered[filtered["nome"] == blocco_nome].iloc[0]

        # ----------------------
        # IMMAGINE CON OVERLAY
        # ----------------------
        try:
            base = Image.open(b["immagine"]).convert("RGBA")
            overlay = Image.open(b["topo"]).convert("RGBA")

            base.paste(overlay, (0, 0), overlay)

            st.image(base, caption=blocco_nome)

        except Exception as e:
            st.image(b["immagine"], caption=blocco_nome)
            st.warning("Topo non disponibile")

        # ----------------------
        # INFO BLOCCO
        # ----------------------
        st.markdown(f"**Grado:** {b['grado']}")
        st.markdown(f"**Settore:** {b['settore']}")
        st.write(b["descrizione"])

    else:
        st.info("Seleziona un range di gradi")