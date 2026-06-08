import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from models.data_manager import DataManager

@st.cache_data(show_spinner=False)
def carregar_geojson():
    import requests
    url = (
        "https://raw.githubusercontent.com/python-visualization/folium/"
        "master/examples/data/world-countries.json"
    )
    return requests.get(url).json()

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
  .kpi-card {
    background: linear-gradient(145deg, #2D1B69 0%, #4A2C9E 100%);
    border-radius: 14px; padding: 22px 18px; color: white;
    text-align: center; box-shadow: 0 3px 12px rgba(45,27,105,0.22);
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
@st.cache_resource
def get_managers():
    return DataManager()

@st.cache_data(show_spinner="Carregando dados dos artigos…")
def carregar_artigos():
    mgr = get_managers()
    return mgr.load_and_clean()

art_mgr = get_managers()
df_art, n_desc = carregar_artigos()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧭 Filtros")
    st.markdown("---")

    anos_validos = df_art[df_art["Ano"] > 0]["Ano"]
    ano_min, ano_max = int(anos_validos.min()), int(anos_validos.max())
    ano_range = st.slider("Período de publicação", ano_min, ano_max, (ano_min, ano_max))

    paises_sel = st.multiselect(
        "Filtrar por país", options=sorted(df_art["Pais_Base"].dropna().unique()),
        placeholder="Todos os países…"
    )

    st.markdown("---")
    df_f = df_art[(df_art["Ano"] >= ano_range[0]) & (df_art["Ano"] <= ano_range[1])]
    if paises_sel:
        df_f = df_f[df_f["Pais_Base"].isin(paises_sel)]

    st.markdown(f"**{len(df_f):,}** artigos selecionados")

    with st.expander("🗑️ Auditoria de dados"):
        st.write(f"**{n_desc}** linhas em quarentena.")
        st.caption("`data/processed/dados_descartados.csv`")

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>📖 Cadernos Pagu Analytics</h1>
  <p>Plataforma de Análise Bibliométrica e Geográfica · Pesquisa de Doutorado</p>
</div>
""", unsafe_allow_html=True)

# ── KPI ───────────────────────────────────────────────────────────────────────
total    = len(df_f)
paises_n = df_f["Pais_Base"].nunique()
perc_int = (df_f["Eh_Internacional"].sum() / total * 100) if total > 0 else 0
periodo  = f"{df_f['Ano'].min()}–{df_f['Ano'].max()}" if total > 0 else "—"

c1, c2, c3, c4 = st.columns(4)
for col, val, lbl in [
    (c1, str(total),         "Artigos"),
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

if total == 0:
    st.warning("Nenhum registro com os filtros selecionados.")
    st.stop()

# ── ABAS PRINCIPAIS ───────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🌍  Distribuição Geográfica",
    "📈  Linha do Tempo",
    "🔍  Explorador de Dados",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MAPA + TOP 10
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_mapa, col_top = st.columns([2, 1])

    with col_mapa:
        st.subheader("Mapa de calor de publicações")
        contagem = df_f["Pais_Geo"].value_counts().reset_index()
        contagem.columns = ["Pais", "Quantidade"]

        if len(contagem) >= 2:
            vals = contagem["Quantidade"].values.astype(float)
            percentis = np.percentile(vals, [0, 25, 50, 75, 90, 100])
            bins_art = sorted(set(
                [max(0.0, float(percentis[0]) - 1)] +
                [float(x) for x in percentis[1:5]] +
                [float(percentis[5]) + 1]
            ))
            if len(bins_art) < 2:
                bins_art = 6
        else:
            bins_art = 6

        geo_data = carregar_geojson()

        count_dict = dict(zip(contagem["Pais"], contagem["Quantidade"]))
        for feature in geo_data["features"]:
            nome = feature["properties"]["name"]
            feature["properties"]["publicacoes"] = count_dict.get(nome, 0)

        m = folium.Map(location=[15, 0], zoom_start=1.5, tiles="CartoDB positron")

        choro_art = folium.Choropleth(
            geo_data=geo_data,
            data=contagem,
            columns=["Pais", "Quantidade"],
            key_on="feature.properties.name",
            fill_color="PuRd",
            fill_opacity=0.75,
            line_opacity=0.2,
            legend_name="Número de publicações por país",
            nan_fill_color="white",
            nan_fill_opacity=0.3,
            bins=bins_art,
        )
        choro_art.add_to(m)
        choro_art.color_scale.width = 600

        folium.GeoJson(
            geo_data,
            style_function=lambda x: {
                "fillColor": "transparent",
                "color": "transparent",
                "weight": 0,
                "fillOpacity": 0,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["name", "publicacoes"],
                aliases=["🌍 País", "📄 Publicações"],
                localize=True,
                sticky=True,
                labels=True,
                style=(
                    "background-color: #1E1240;"
                    "color: white;"
                    "border: none;"
                    "border-radius: 8px;"
                    "box-shadow: 2px 2px 8px rgba(0,0,0,0.4);"
                    "font-size: 13px;"
                    "padding: 8px 12px;"
                ),
            ),
        ).add_to(m)

        st_folium(m, width="100%", height=420)

    with col_top:
        st.subheader("Top 10 países")
        top10 = df_f["Pais_Base"].value_counts().head(10).reset_index()
        top10.columns = ["País", "Artigos"]

        fig_pie = px.pie(
            top10, values="Artigos", names="País",
            hole=0.45,
            color_discrete_sequence=[
                "#1A0A4A",  # Brasil
                "#C0392B",  # EUA
                "#2471A3",  # França
                "#1E8449",  # Argentina
                "#D68910",  # Reino Unido
                "#7D3C98",  # Marrocos
                "#117A65",  # Portugal
                "#BA4A00",  # Espanha
                "#1A5276",  # Canadá
                "#717D7E",  # México
            ],
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent",
            insidetextorientation="radial",
            hovertemplate="<b>%{label}</b><br>Artigos: %{value}<br>%{percent}",
        )
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle", y=0.5,
                xanchor="left", x=1.02,
                font=dict(size=11),
            ),
            margin=dict(t=10, b=10, l=10, r=140),
            paper_bgcolor="rgba(0,0,0,0)",
            height=420,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — LINHA DO TEMPO
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    stats = art_mgr.get_timeline_data(df_f)

    if len(stats) < 2:
        st.info("Dados insuficientes para a linha do tempo com o filtro atual.")
    else:
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=stats["Ano"], y=stats["% Internacional"],
            mode="lines+markers", name="% Internacional",
            line=dict(color="#7B4FBF", width=3),
            marker=dict(size=7, color="#2D1B69"),
            fill="tozeroy", fillcolor="rgba(123,79,191,0.12)",
            hovertemplate="<b>%{x}</b><br>Internacional: %{y:.1f}%<extra></extra>",
        ))
        fig_area.update_layout(
            title="Evolução da autoria estrangeira ao longo dos anos",
            xaxis_title="Ano", yaxis_title="% de autores internacionais",
            hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(245,243,240,0.6)",
            xaxis=dict(showgrid=True, gridcolor="#E0D8F0", dtick=2),
            yaxis=dict(showgrid=True, gridcolor="#E0D8F0", range=[0, 105]),
        )
        st.plotly_chart(fig_area, use_container_width=True)

    col_bar, col_tbl = st.columns([1, 1])
    with col_bar:
        fig_bar = px.bar(
            stats, x="Ano", y="Total",
            title="Total de publicações por ano",
            color="% Internacional", color_continuous_scale="Purples",
            labels={"Total": "Publicações"},
        )
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(245,243,240,0.6)")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_tbl:
        st.write("**Detalhamento por ano**")
        st.dataframe(
            stats.rename(columns={"Internacionais": "Internac.", "% Internacional": "% Internac."}),
            use_container_width=True, height=320,
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EXPLORADOR
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Base consolidada de dados")
    busca = st.text_input("🔎 Buscar por título ou autoria…", "")

    cols_needed = ["Ano", "TÍTULO", "AUTORIA", "Pais_Base", "Língua", "Tradução"]
    cols_ok = [c for c in cols_needed if c in df_f.columns]

    df_tbl = df_f[cols_ok].rename(columns={
        "TÍTULO": "Título do artigo", "AUTORIA": "Autoria",
        "Pais_Base": "País de publicação", "Língua": "Língua original",
        "Tradução": "Traduções / Tradutor",
    })

    if busca:
        mask = pd.Series([False] * len(df_tbl), index=df_tbl.index)
        for c in ["Título do artigo", "Autoria"]:
            if c in df_tbl.columns:
                mask |= df_tbl[c].str.contains(busca, case=False, na=False)
        df_tbl = df_tbl[mask]

    st.caption(f"{len(df_tbl):,} registros exibidos")
    st.dataframe(df_tbl, use_container_width=True, height=460)
    st.download_button(
        "⬇️ Exportar tabela filtrada (.csv)",
        data=df_tbl.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
        file_name="cadernos_pagu_filtrado.csv", mime="text/csv",
    )

# ── RODAPÉ ─────────────────────────────────────────────────────────────────────
st.markdown("""<hr>
<div class="footer">
  Cadernos Pagu Analytics · Pesquisa de Doutorado · Plataforma desenvolvida com Streamlit
</div>""", unsafe_allow_html=True)
