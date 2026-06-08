import streamlit as st
import streamlit.components.v1 as components
import pathlib


FONTE_PADRAO_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  body, h1, h2, h3, h4, h5, h6, p, span, div, td, th,
  label, button, input, .stat-label, .bar-label, .section-note,
  .note, footer {
    font-family: 'Inter', 'IBM Plex Sans', Arial, sans-serif !important;
  }
</style>
"""


def _ler_html(nome: str) -> str:
    caminho = pathlib.Path(__file__).parent.parent / "assets" / nome
    conteudo = caminho.read_text(encoding="utf-8")
    if "<head>" in conteudo:
        return conteudo.replace("<head>", f"<head>{FONTE_PADRAO_CSS}", 1)
    return FONTE_PADRAO_CSS + conteudo


# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background-color: #F5F3F0; }
  [data-testid="stSidebar"] { background-color: #1E1240; }
  [data-testid="stSidebar"] .stMarkdown,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span { color: #EAE8F5 !important; }
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
  .hero {
    background: linear-gradient(135deg, #3B1F6E 0%, #6A3FA6 55%, #A87FD4 100%);
    border-radius: 18px; padding: 32px 40px; margin-bottom: 28px;
  }
  .hero h1 { color: #FFFFFF !important; font-size: 2rem; margin: 0; }
  .hero p  { color: rgba(255,255,255,0.75); margin: 8px 0 0 0; font-size: 0.95rem; }
  .stTabs [aria-selected="true"] { color: #6A3FA6 !important; font-weight: 600; }
  hr { border-color: #D8D3F0; }
  .footer { text-align: center; color: #999; font-size: 0.78rem; padding: 16px 0 4px; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>📊 Análise Bibliométrica</h1>
  <p>Evolução temática, palavras-chave e viagens teóricas internacionais · Cadernos Pagu 1993–2008</p>
</div>
""", unsafe_allow_html=True)

# ── Abas ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📈  Evolução Temática",
    "☁️  Palavras-chave",
    "🗺️  Painel Bibliométrico",
])

with tab1:
    import plotly.graph_objects as go

    ANOS = [1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008]

    CLUSTERS = [
        {
            "label": "Gênero & Relações",
            "cor":   "#185FA5",
            "dados": [10.0,2.0,1.9,3.33,6.36,1.82,4.21,7.14,6.84,4.5,6.67,2.68,3.53],
            "insight": (
                "Tema dominante desde o início. Pico em 1996 (fundacional) e "
                "retomada forte em 2003–2006, consolidando gênero como categoria "
                "central da revista. A alta de 2003 coincide com debates sobre "
                "teoria queer e estudos interseccionais no Brasil."
            ),
        },
        {
            "label": "Sexualidade & Corpo",
            "cor":   "#993C1D",
            "dados": [1.11,0.0,1.9,1.11,4.55,0.91,1.05,4.29,1.58,2.5,3.33,2.2,0.59],
            "insight": (
                "Cresce visivelmente a partir de 2000, com picos em 2000 e 2003. "
                "Reflete a entrada de estudos sobre corporalidade, erotismo e "
                "homossexualidade — temas que ganham espaço acadêmico no contexto "
                "pós-AIDS e dos debates sobre identidade sexual nos anos 2000."
            ),
        },
        {
            "label": "Raça & Identidade",
            "cor":   "#0F6E56",
            "dados": [12.22,0.0,0.48,0.0,0.91,0.0,1.05,0.71,3.68,0.0,0.0,0.98,0.0],
            "insight": (
                "Pico extraordinário em 1996: naquele ano, um número temático focou "
                "especificamente em raça e gênero. Depois recua, com leve retomada "
                "em 2004 — possivelmente ligada às políticas de cotas e debates "
                "sobre identidade racial no Brasil."
            ),
        },
        {
            "label": "Feminismo & Política",
            "cor":   "#534AB7",
            "dados": [2.22,1.0,0.95,2.96,0.91,1.82,0.53,2.14,0.0,0.0,0.0,0.24,1.76],
            "insight": (
                "Presença constante mas moderada, com pico em 1999. "
                "Ausência entre 2004–2006, seguida de retorno em 2008 — "
                "pode indicar um ciclo de renovação teórica do feminismo "
                "na academia brasileira."
            ),
        },
        {
            "label": "Tráfico & Prostituição",
            "cor":   "#993556",
            "dados": [1.11,0.0,0.0,0.0,0.0,0.0,0.53,0.0,0.0,3.0,0.0,0.0,4.71],
            "insight": (
                "Quase ausente até 2005, depois sobe abruptamente em 2005 e "
                "especialmente em 2008. Espelha o crescimento do debate político "
                "sobre tráfico de pessoas — o Brasil ratificou o Protocolo de "
                "Palermo em 2004 e aprovou a Lei de Tráfico em 2006."
            ),
        },
        {
            "label": "Família & Maternidade",
            "cor":   "#3B6D11",
            "dados": [0.0,1.0,0.95,0.74,0.0,0.0,1.05,2.86,0.0,0.5,1.33,1.22,0.29],
            "insight": (
                "Tema intermitente, com pico em 2003. Articula-se com debates "
                "sobre novas configurações familiares, parentalidade e trabalho "
                "doméstico — presentes sobretudo em números temáticos sobre "
                "trabalho e vida privada."
            ),
        },
        {
            "label": "Mulheres & Trabalho",
            "cor":   "#854F0B",
            "dados": [1.11,2.0,0.95,0.37,0.0,0.0,2.63,0.71,0.53,0.5,1.33,0.49,1.47],
            "insight": (
                "Frequência relativamente estável ao longo do período. "
                "Destaque para 2002, provavelmente ligado a número temático "
                "sobre reestruturação produtiva e desigualdades de gênero no trabalho."
            ),
        },
        {
            "label": "Cultura & Mídia",
            "cor":   "#5C2C7C",
            "dados": [2.22,4.0,0.95,1.48,0.91,0.0,0.0,2.14,2.63,0.0,0.67,0.98,0.59],
            "insight": (
                "Pico em 1997, com boa presença nos anos iniciais. Depois se "
                "dispersa. Reflete a entrada de abordagens culturalistas "
                "(literatura, mídia, moda) na revista nos anos de consolidação "
                "da área de estudos feministas no Brasil."
            ),
        },
    ]

    st.subheader("Evolução temática dos artigos (1996–2008)")
    st.caption(
        "Frequência normalizada por 10 artigos publicados por ano. "
        "Selecione um tema para destacá-lo e ver observações."
    )

    opcoes = ["— Todos os temas —"] + [c["label"] for c in CLUSTERS]
    tema_sel = st.selectbox(
        "Destacar tema:",
        options=opcoes,
        index=0,
        label_visibility="collapsed",
    )

    def _cor_fade(hex_color: str) -> str:
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        return f"rgba({r},{g},{b},0.2)"

    fig = go.Figure()

    for c in CLUSTERS:
        destaque = (tema_sel == "— Todos os temas —") or (tema_sel == c["label"])
        fig.add_trace(go.Scatter(
            x=ANOS,
            y=c["dados"],
            mode="lines+markers",
            name=c["label"],
            line=dict(
                color=c["cor"] if destaque else _cor_fade(c["cor"]),
                width=3 if tema_sel == c["label"] else 1.5,
            ),
            marker=dict(
                size=7 if tema_sel == c["label"] else 4,
                color=c["cor"] if destaque else _cor_fade(c["cor"]),
            ),
            opacity=1.0 if destaque else 0.3,
            hovertemplate=(
                f"<b>{c['label']}</b><br>"
                "Ano: %{x}<br>"
                "Freq.: %{y:.2f} por 10 artigos"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        xaxis=dict(
            title="Ano",
            tickvals=ANOS,
            ticktext=[str(a) for a in ANOS],
            showgrid=True,
            gridcolor="#E0D8F0",
        ),
        yaxis=dict(
            title="Ocorrências por 10 artigos",
            showgrid=True,
            gridcolor="#E0D8F0",
            rangemode="tozero",
        ),
        hovermode="closest",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(245,243,240,0.6)",
        legend=dict(
            orientation="v",
            x=1.01, y=1,
            font=dict(size=11),
        ),
        margin=dict(t=20, b=20, l=60, r=180),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)

    if tema_sel != "— Todos os temas —":
        dados_tema = next(c for c in CLUSTERS if c["label"] == tema_sel)
        st.markdown(
            f"""<div style="
                background:#EEEDFE;
                border-left:4px solid {dados_tema['cor']};
                border-radius:0 8px 8px 0;
                padding:14px 18px;
                margin-top:8px;
            ">
            <p style="font-size:14px;font-weight:600;color:{dados_tema['cor']};
                       margin:0 0 6px;">{dados_tema['label']}</p>
            <p style="font-size:13px;color:#3C3489;margin:0;line-height:1.7;">
                {dados_tema['insight']}</p>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """<div style="background:#F5F3F0;border-radius:8px;padding:12px 16px;
                           margin-top:8px;">
            <p style="font-size:13px;color:#888;margin:0;">
                Selecione um tema no menu acima para ver observações
                sobre sua trajetória na revista.</p>
            </div>""",
            unsafe_allow_html=True,
        )

with tab2:
    st.subheader("Nuvem de palavras-chave e frequência nos títulos")
    st.caption(
        "Nuvem construída a partir das palavras-chave declaradas nos artigos. "
        "Barras mostram os termos mais recorrentes nos títulos (top 25)."
    )
    try:
        components.html(_ler_html("cadernos_pagu_visualizacoes.html"),
                        height=920, scrolling=True)
    except Exception as e:
        st.warning(f"Erro ao carregar: {e}")

with tab3:
    st.subheader("Viagens teóricas internacionais")
    st.caption(
        "Artigos traduzidos, idiomas de origem, tradutores, autores estrangeiros "
        "mais citados, dossiês temáticos e procedência das autorias (1993–2008)."
    )
    try:
        components.html(_ler_html("cadernos_pagu_graficos.html"),
                        height=2700, scrolling=True)
    except Exception as e:
        st.warning(f"Erro ao carregar: {e}")

# ── Rodapé ────────────────────────────────────────────────────────────────────
st.markdown("""<hr>
<div class="footer">
  Cadernos Pagu Analytics · Análise Bibliométrica · Plataforma desenvolvida com Streamlit
</div>""", unsafe_allow_html=True)
