import streamlit as st

st.set_page_config(
    page_title="Cadernos Pagu Analytics",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

artigos = st.Page("pages/artigos.py",               title="Cadernos Pagu Analytics",    icon="📖")
refs    = st.Page("pages/Referencias.py",           title="Referências Bibliográficas", icon="📚")
analise = st.Page("pages/Analise_Bibliometrica.py", title="Análise Bibliométrica",      icon="📊")

pg = st.navigation([artigos, refs, analise])
pg.run()
