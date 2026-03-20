import streamlit as st
import pandas as pd

from render_map import render_map
from render_blocks import render_block_list, GRADES

# --- CONFIGURAZIONE E COSTANTI ---
DATA_PATH = "data/"
PALETTE = [
    [0, 255, 0, 160], [255, 0, 0, 160], [0, 0, 255, 160],
    [255, 255, 0, 160], [255, 0, 255, 160], [0, 255, 255, 160], [255, 128, 0, 160],
]

# --- CARICAMENTO DATI ---
@st.cache_data
def load_data():
    parks = pd.read_csv(DATA_PATH + "parcheggi.csv")
    blocks = pd.read_csv(DATA_PATH + "blocchi.csv")
    settori_list = sorted(blocks["settore"].unique())
    color_map = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(settori_list)}
    settori_list = ["Tutti"] + settori_list
    blocks['color'] = blocks['settore'].map(color_map)
    grade_to_int = {grade: i for i, grade in enumerate(GRADES)}
    blocks['grade_rank'] = blocks['grado'].map(grade_to_int)
    min_grade = blocks['grade_rank'].min()
    max_grade = blocks['grade_rank'].max()
    tags = sorted(set(tag for sublist in blocks['tag'].dropna().apply(lambda x: str(x).split(',')).tolist() for tag in sublist))
    return parks, blocks, settori_list, grade_to_int, min_grade, max_grade, tags

parcheggi, boulder_data, settori, grade_to_int, min_grade, max_grade, tags = load_data()

st.set_page_config(page_title="Sugano Boulder", page_icon="img/ssm.png")

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.subheader("Sugano Boulder")

render_map(parcheggi=parcheggi, boulder_data=boulder_data)

render_block_list(boulder_data, settori, grade_to_int, min_grade, max_grade, tags)