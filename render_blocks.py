import streamlit as st
import pandas as pd
import os
from PIL import Image, ImageOps

GRADES = ['3', '4', '5A', '5B', '5C', '6A', '6A+', '6B', '6B+', '6C', '6C+', '7A', '7A+', '7B', '7B+', '7C', '7C+', '8A', '8A+', '8B', '8B+', '8C', '8C+', '9A']
IMAGE_PATH = "img/"

# Cache per le immagini
@st.cache_resource
def load_image_cached(image_path):
    """Carica e cache le immagini per evitare ricaricamenti multipli"""
    try:
        img = Image.open(image_path)
        return img
    except Exception as e:
        st.error(f"Errore nel caricamento dell'immagine {image_path}: {e}")
        return None

@st.fragment
def render_block_list(boulder_data, settori, grade_to_int, min_grade, max_grade, tags):

    st.subheader(f"Lista dei blocchi")
    selected_sector = st.selectbox("Scegli un settore", options=settori, index=0)

    @st.fragment
    def nerd_stats(selected_sector):
        if st.checkbox("Mostra statistiche per nerd"):
            @st.cache_data
            def histogram_by_sector(selected_sector):
                if selected_sector == "Tutti":
                    return boulder_data['grado'].value_counts().sort_index()
                else:
                    return boulder_data[boulder_data['settore'] == selected_sector]['grado'].value_counts().sort_index()
            if selected_sector == "Tutti":
                st.bar_chart(histogram_by_sector(selected_sector))
            else:
                st.bar_chart(histogram_by_sector(selected_sector))
    
    nerd_stats(selected_sector)

    col1, col2 = st.columns([2, 3])
    with col1:
        filtraggio = st.checkbox("Attiva filtri avanzati")

    if filtraggio:
        with col2:
            range_gradi = st.select_slider(
                "Seleziona range difficoltà",
                options=GRADES[min_grade:max_grade+1],
                value=(GRADES[min_grade], GRADES[max_grade])
            )
            boulder_tags = st.multiselect(
                "Seleziona tag",
                options=tags,
            )
    else:
        range_gradi = (GRADES[min_grade], GRADES[max_grade])
        boulder_tags = []

    # --- LOGICA DI FILTRAGGIO AVANZATA ---
    mask = pd.Series([True] * len(boulder_data))
    if selected_sector != "Tutti":
        mask = (boulder_data['settore'] == selected_sector)

    if filtraggio:
        idx_min = grade_to_int[range_gradi[0]]
        idx_max = grade_to_int[range_gradi[1]]
        mask &= boulder_data['grade_rank'].between(idx_min, idx_max)

        if boulder_tags:
            mask &= boulder_data['tag'].apply(lambda x: any(tag in str(x).split(',') for tag in boulder_tags))

    blocchi_da_mostrare = boulder_data[mask]

    if blocchi_da_mostrare.empty:
        st.info("Nessun blocco corrisponde ai filtri selezionati in questo settore.")
        return

    sassi = blocchi_da_mostrare['sasso'].unique()
    
    for sasso in sassi:
        st.subheader(f"{sasso}")
        
        df_sasso = blocchi_da_mostrare[blocchi_da_mostrare['sasso'] == sasso]

        facce = df_sasso['faccia'].unique()

        for faccia in facce:

            if pd.isna(faccia):
                vie_faccia = df_sasso[df_sasso['faccia'].isna()]
            else:
                vie_faccia = df_sasso[df_sasso['faccia'] == faccia]

            if not vie_faccia.empty:
                img_name = vie_faccia.iloc[0]['immagine']
                if pd.notna(img_name):
                    if pd.notna(faccia):
                        st.write(f"Faccia: {int(faccia)}")
                    image = load_image_cached(os.path.join(IMAGE_PATH, img_name))
                    if image:
                        st.image(image, width="content")
                    
                    for _, blocco in vie_faccia.iterrows():
                        with st.expander(f'**{blocco["numero"]}** - {blocco["nome"]} - {blocco["grado"]} - {blocco['partenza']}'):
                            st.write(f"**Descrizione:** {blocco['descrizione']}")
                            st.caption(f"Tag: {blocco['tag']} | FA: {blocco['fa']}")
        
        st.divider()