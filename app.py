import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from models.data_manager import DataManager

st.set_page_config(
    page_title="Cadernos Pagu Analytics",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── TEMA / CSS ────────────────────────────────────────────────────────────────
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
  .kpi-card {
    background: linear-gradient(145deg, #2D1B69 0%, #4A2C9E 100%);
    border-radius: 14px;
    padding: 22px 18px;
    color: white;
    text-align: center;
    box-shadow: 0 3px 12px rgba(45,27,105,0.22);
    margin-bottom: 8px;
  }
  .kpi-value { font-size: 2rem; font-weight: 700; line-height: 1.1; margin: 0; }
  .kpi-label { font-size: 0.78rem; opacity: 0.78; margin: 6px 0 0 0;
               letter-spacing: 0.03em; text-transform: uppercase; }
  .hero {
    background: linear-gradient(135deg, #1E1240 0%, #5B38C2 60%, #9B6EEF 100%);
    border-radius: 18px; padding: 32px 40px; margin-bottom: 28px;
  }
  .hero h1 { color: #FFFFFF !important; font-size: 2rem; margin: 0; }
  .hero p  { color: rgba(255,255,255,0.75); margin: 8px 0 0 0; font-size: 0.95rem; }
  .stTabs [data-baseweb="tab"] { font-size: 0.95rem; padding: 10px 22px; }
  .stTabs [aria-selected="true"] { color: #4A2C9E !important; font-weight: 600; }
  hr { border-color: #D8D3F0; }
  .footer { text-align: center; color: #999; font-size: 0.78rem; padding: 16px 0 4px; }
</style>
""", unsafe_allow_html=True)

# ── CARGA DE DADOS ─────────────────────────────────────────────────────────────
# CORREÇÃO: cache_data não serializa objetos Python corretamente;
# usamos cache_resource para o manager e cache_data só para o DataFrame.
@st.cache_resource
def get_manager():
    return DataManager()

@st.cache_data(show_spinner="Carregando e processando dados…")
def carregar_dados():
    mgr = get_manager()
    df, n_desc = mgr.load_and_clean()
    return df, n_desc

manager = get_manager()
df, n_descartados = carregar_dados()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧭 Filtros")
    st.markdown("---")

    anos_validos = df[df["Ano"] > 0]["Ano"]
    if len(anos_validos) == 0:
        st.warning("Nenhum dado de ano encontrado.")
        st.stop()

    ano_min = int(anos_validos.min())
    ano_max = int(anos_validos.max())

    ano_range = st.slider(
        "Período de publicação",
        min_value=ano_min, max_value=ano_max,
        value=(ano_min, ano_max)
    )

    paises_opcoes = sorted(df["Pais_Base"].dropna().unique())
    paises_sel = st.multiselect(
        "Filtrar por país",
        options=paises_opcoes,
        placeholder="Todos os países…"
    )

    st.markdown("---")
    df_f = df[(df["Ano"] >= ano_range[0]) & (df["Ano"] <= ano_range[1])]
    if paises_sel:
        df_f = df_f[df_f["Pais_Base"].isin(paises_sel)]

    st.markdown(f"**{len(df_f):,}** registros selecionados")

    with st.expander("🗑️ Auditoria de dados"):
        st.write(f"**{n_descartados}** linhas em quarentena por dados incompletos.")
        st.caption("Arquivo: `data/processed/dados_descartados.csv`")

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>📖 Cadernos Pagu Analytics</h1>
  <p>Plataforma de Análise Bibliométrica e Geográfica · Pesquisa de Doutorado</p>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
total    = len(df_f)
paises_n = df_f["Pais_Base"].nunique()
perc_int = (df_f["Eh_Internacional"].sum() / total * 100) if total > 0 else 0
periodo  = f"{df_f['Ano'].min()}–{df_f['Ano'].max()}" if total > 0 else "—"

c1, c2, c3, c4 = st.columns(4)
for col, val, lbl in [
    (c1, str(total),         "Registros"),
    (c2, str(paises_n),      "Países representados"),
    (c3, f"{perc_int:.1f}%", "Autoria internacional"),
    (c4, periodo,            "Período analisado"),
]:
    with col:
        st.markdown(f"""<div class="kpi-card">
          <p class="kpi-value">{val}</p>
          <p class="kpi-label">{lbl}</p>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── GUARDA-CHUVA: sem dados após filtro ───────────────────────────────────────
if total == 0:
    st.warning("Nenhum registro encontrado com os filtros selecionados. Ajuste o período ou os países.")
    st.stop()

# ── ABAS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🌍  Distribuição Geográfica",
    "📈  Linha do Tempo",
    "🔍  Explorador de Dados",
])

# ── TAB 1: MAPA + PIZZA ───────────────────────────────────────────────────────
with tab1:
    col_mapa, col_pie = st.columns([2, 1])

    with col_mapa:
        st.subheader("Mapa de calor de publicações")
        url_geo = (
            "https://raw.githubusercontent.com/python-visualization/folium/"
            "master/examples/data/world-countries.json"
        )
        contagem = df_f["Pais_Geo"].value_counts().reset_index()
        contagem.columns = ["Pais", "Quantidade"]

        m = folium.Map(location=[15, 0], zoom_start=1.5, tiles="CartoDB positron")
        folium.Choropleth(
            geo_data=url_geo,
            data=contagem,
            columns=["Pais", "Quantidade"],
            key_on="feature.properties.name",
            fill_color="PuRd",
            fill_opacity=0.75,
            line_opacity=0.2,
            legend_name="Número de publicações por país",
            nan_fill_color="white",          # países sem dados ficam brancos
            nan_fill_opacity=0.4,
        ).add_to(m)

        # Tooltip com nome e contagem ao passar o mouse
        folium.LayerControl().add_to(m)
        st_folium(m, width="100%", height=420)

    with col_pie:
        st.subheader("Top 10 países")
        top10 = df_f["Pais_Base"].value_counts().head(10).reset_index()
        top10.columns = ["Pais_Base", "count"]

        fig_pie = px.pie(
            top10, values="count", names="Pais_Base",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Purples_r,
        )
        fig_pie.update_traces(
            hovertemplate="<b>%{label}</b><br>Artigos: %{value}<br>%{percent}",
            textposition="outside",
            textinfo="label+percent",
        )
        fig_pie.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ── TAB 2: LINHA DO TEMPO ─────────────────────────────────────────────────────
with tab2:
    stats = manager.get_timeline_data(df_f)

    if stats.empty or len(stats) < 2:
        st.info("Dados insuficientes para exibir a linha do tempo com o filtro atual.")
    else:
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=stats["Ano"], y=stats["% Internacional"],
            mode="lines+markers",
            name="% Internacional",
            line=dict(color="#7B4FBF", width=3),
            marker=dict(size=7, color="#2D1B69"),
            fill="tozeroy",
            fillcolor="rgba(123,79,191,0.12)",
            hovertemplate="<b>%{x}</b><br>Internacional: %{y:.1f}%<extra></extra>",
        ))
        fig_area.update_layout(
            title="Evolução da autoria estrangeira ao longo dos anos",
            xaxis_title="Ano",
            yaxis_title="% de autores internacionais",
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(245,243,240,0.6)",
            xaxis=dict(showgrid=True, gridcolor="#E0D8F0", dtick=2),
            yaxis=dict(showgrid=True, gridcolor="#E0D8F0", range=[0, 105]),
        )
        st.plotly_chart(fig_area, use_container_width=True)

    col_bar, col_tab = st.columns([1, 1])

    with col_bar:
        fig_bar = px.bar(
            stats, x="Ano", y="Total",
            title="Total de publicações por ano",
            color="% Internacional",
            color_continuous_scale="Purples",
            labels={"Total": "Publicações", "% Internacional": "% Internacional"},
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(245,243,240,0.6)",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_tab:
        st.write("**Detalhamento por ano**")
        tbl = stats.rename(columns={
            "Ano": "Ano",
            "Total": "Total",
            "Internacionais": "Internac.",
            "% Internacional": "% Internac.",
        })
        st.dataframe(tbl, use_container_width=True, height=320)

# ── TAB 3: EXPLORADOR ─────────────────────────────────────────────────────────
with tab3:
    st.subheader("Base consolidada de dados")
    busca = st.text_input("🔎 Buscar por título ou autoria…", "")

    # Verifica se as colunas esperadas existem
    colunas_necessarias = ["Ano", "TÍTULO", "AUTORIA", "Pais_Base", "Língua", "Tradução"]
    colunas_presentes = [c for c in colunas_necessarias if c in df_f.columns]
    colunas_faltando  = [c for c in colunas_necessarias if c not in df_f.columns]

    if colunas_faltando:
        st.warning(f"⚠️ Colunas não encontradas na planilha: {', '.join(colunas_faltando)}")

    df_tbl = df_f[colunas_presentes].rename(columns={
        "Ano":       "Ano",
        "TÍTULO":    "Título do artigo",
        "AUTORIA":   "Autoria",
        "Pais_Base": "País de publicação",
        "Língua":    "Língua original",
        "Tradução":  "Traduções / Tradutor",
    })

    if busca:
        cols_busca = [c for c in ["Título do artigo", "Autoria"] if c in df_tbl.columns]
        if cols_busca:
            mask = df_tbl[cols_busca[0]].str.contains(busca, case=False, na=False)
            for c in cols_busca[1:]:
                mask = mask | df_tbl[c].str.contains(busca, case=False, na=False)
            df_tbl = df_tbl[mask]

    st.caption(f"{len(df_tbl):,} registros exibidos")
    st.dataframe(df_tbl, use_container_width=True, height=460)

    # Botão de exportação
    csv_export = df_tbl.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="⬇️ Exportar tabela filtrada (.csv)",
        data=csv_export,
        file_name="cadernos_pagu_filtrado.csv",
        mime="text/csv",
    )

# ── RODAPÉ ─────────────────────────────────────────────────────────────────────
st.markdown("""<hr>
<div class="footer">
  Cadernos Pagu Analytics · Pesquisa de Doutorado · Plataforma desenvolvida com Streamlit
</div>""", unsafe_allow_html=True)
