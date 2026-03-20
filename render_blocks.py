import streamlit as st
import pandas as pd
import os

GRADES = ['3', '4', '5A', '5B', '5C', '6A', '6A+', '6B', '6B+', '6C', '6C+', '7A', '7A+', '7B', '7B+', '7C', '7C+', '8A', '8A+', '8B', '8B+', '8C', '8C+', '9A']
IMAGE_PATH = "img/"

@st.fragment
def render_block_list(boulder_data, settori, grade_to_int, min_grade, max_grade):
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
    mask = pd.Series([True] * len(boulder_data))
    if selected_sector != "Tutti":
        mask = (boulder_data['settore'] == selected_sector)

    if filtraggio:
        idx_min = grade_to_int[range_gradi[0]]
        idx_max = grade_to_int[range_gradi[1]]
        mask &= boulder_data['grade_rank'].between(idx_min, idx_max)

        if boulder_tags:
            mask &= boulder_data['tag'].apply(lambda x: any(tag in str(x).split(',') for tag in boulder_tags))


    # --- VISUALIZZAZIONE BLOCCHI CON SOVRAPPOSIZIONE TOPOS ---
    blocchi_da_mostrare = boulder_data[mask]

    if blocchi_da_mostrare.empty:
        st.info("Nessun blocco corrisponde ai filtri selezionati in questo settore.")
        return

    # Raggruppiamo per 'sasso'
    sassi = blocchi_da_mostrare['sasso'].unique()
    
    for sasso in sassi:
        st.subheader(f"{sasso}")
        
        # Prendiamo tutti i blocchi (vie) di questo sasso specifico
        df_sasso = blocchi_da_mostrare[blocchi_da_mostrare['sasso'] == sasso]
        
        # Identifichiamo le facce (gestendo i NaN)
        # Usiamo dropna() per le facce valide e gestiamo i nulli a parte se necessario
        facce = df_sasso['faccia'].unique()

        for faccia in facce:
            # Filtriamo le vie di questa specifica faccia
            # Nota: la comparazione con i nan in pandas richiede cautela
            if pd.isna(faccia):
                vie_faccia = df_sasso[df_sasso['faccia'].isna()]
            else:
                vie_faccia = df_sasso[df_sasso['faccia'] == faccia]

            if not vie_faccia.empty:
                # Mostra l'immagine della faccia (prendiamo la prima disponibile per quella faccia)
                img_name = vie_faccia.iloc[0]['immagine']
                if pd.notna(img_name):
                    if pd.notna(faccia):
                        st.write(f"Faccia: {int(faccia)}")
                    st.image(os.path.join(IMAGE_PATH, img_name))
                    
                    # Elenco delle vie sotto l'immagine
                    for _, blocco in vie_faccia.iterrows():
                        with st.expander(f'**{blocco["numero"]}** - {blocco["nome"]} - {blocco["grado"]} - {blocco['partenza']}'):
                            st.write(f"**Descrizione:** {blocco['descrizione']}")
                            st.caption(f"Tag: {blocco['tag']} | FA: {blocco['fa']}")
        
        # Il divider viene messo solo dopo aver finito tutte le facce di UN sasso
        st.divider()