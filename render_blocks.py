import streamlit as st
import pandas as pd
import os
from PIL import Image, ImageOps

GRADES = ['3', '4', '5A', '5B', '5C', '6A', '6A+', '6B', '6B+', '6C', '6C+', '7A', '7A+', '7B', '7B+', '7C', '7C+', '8A', '8A+', '8B', '8B+', '8C', '8C+', '9A']
IMAGE_PATH = "img/"

@st.fragment
def render_block_list(boulder_data, settori, grade_to_int, min_grade, max_grade, tags):

    st.subheader(f"Lista dei blocchi")
    selected_sector = st.selectbox("Scegli un settore", options=settori, index=0)

    if st.checkbox("Mostra statistiche per nerd"):
        if selected_sector == "Tutti":
            st.bar_chart(boulder_data['grado'].value_counts().sort_index())
        else:
            st.bar_chart(boulder_data[boulder_data['settore'] == selected_sector]['grado'].value_counts().sort_index())

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
                    image = Image.open(os.path.join(IMAGE_PATH, img_name))
                    image = ImageOps.exif_transpose(image) 
                    st.image(image, width="content")
                    
                    for _, blocco in vie_faccia.iterrows():
                        with st.expander(f'**{blocco["numero"]}** - {blocco["nome"]} - {blocco["grado"]} - {blocco['partenza']}'):
                            st.write(f"**Descrizione:** {blocco['descrizione']}")
                            st.caption(f"Tag: {blocco['tag']} | FA: {blocco['fa']}")
        
        st.divider()