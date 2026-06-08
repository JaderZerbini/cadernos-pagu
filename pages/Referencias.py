import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from models.references_manager import ReferencesManager, LANG_NAMES, GEO_PARA_PT
import numpy as np

@st.cache_data(show_spinner=False)
def carregar_geojson():
    import requests
    url = (
        "https://raw.githubusercontent.com/python-visualization/folium/"
        "master/examples/data/world-countries.json"
    )
    return requests.get(url).json()


# ── Cores por língua ─────────────────────────────────────────────────────────
LINGUA_CORES = {
    "Inglês":    "#2980B9",
    "Português": "#27AE60",
    "Francês":   "#E67E22",
    "Espanhol":  "#E74C3C",
    "Alemão":    "#8E44AD",
    "Italiano":  "#16A085",
}
LANG_CORES_SANKEY = {
    "EN": "rgba(41,128,185,0.45)",
    "FR": "rgba(230,126,34,0.45)",
    "DE": "rgba(142,68,173,0.45)",
    "ES": "rgba(231,76,60,0.45)",
    "IT": "rgba(22,160,133,0.45)",
    "PT": "rgba(39,174,96,0.45)",
}

CENTROIDES = {
    "Brazil":                    (-15.8,  -47.9),
    "United States of America":  ( 38.9,  -77.0),
    "France":                    ( 46.2,    2.2),
    "United Kingdom":            ( 51.5,   -0.1),
    "Germany":                   ( 52.5,   13.4),
    "Italy":                     ( 41.9,   12.5),
    "Spain":                     ( 40.4,   -3.7),
    "Argentina":                 (-34.6,  -58.4),
    "Portugal":                  ( 38.7,   -9.1),
    "Mexico":                    ( 19.4,  -99.1),
    "Australia":                 (-25.3,  133.8),
    "Canada":                    ( 56.1, -106.3),
    "Netherlands":               ( 52.1,    5.3),
    "Belgium":                   ( 50.5,    4.5),
    "Switzerland":               ( 46.8,    8.2),
    "Sweden":                    ( 60.1,   18.6),
    "Poland":                    ( 51.9,   19.1),
    "Russia":                    ( 61.5,  105.3),
}

PAIS_PARA_LINGUA = {
    "France":                    "FR",
    "United States of America":  "EN",
    "United Kingdom":            "EN",
    "Australia":                 "EN",
    "Canada":                    "EN",
    "Brazil":                    "PT",
    "Portugal":                  "PT",
    "Germany":                   "DE",
    "Switzerland":               "DE",
    "Austria":                   "DE",
    "Italy":                     "IT",
    "Spain":                     "ES",
    "Argentina":                 "ES",
    "Mexico":                    "ES",
    "Russia":                    "RU",
    "Poland":                    "PL",
    "Netherlands":               "NL",
    "Belgium":                   "FR",
}

LINGUA_PARA_PAISES = {
    "PT": ["Brazil", "Portugal"],
    "EN": ["United States of America", "United Kingdom", "Australia"],
    "FR": ["France", "Belgium", "Switzerland"],
    "ES": ["Spain", "Argentina", "Mexico"],
    "DE": ["Germany", "Austria", "Switzerland"],
    "IT": ["Italy"],
    "RU": ["Russia"],
    "PL": ["Poland"],
}

COR_LINGUA = {
    "FR": "#E67E22",
    "EN": "#2980B9",
    "DE": "#8E44AD",
    "ES": "#E74C3C",
    "IT": "#16A085",
    "PT": "#27AE60",
    "RU": "#C0392B",
    "PL": "#D35400",
}


@st.cache_data(show_spinner=False)
def identificar_pais_clicado(lat, lng, _geo_data):
    from shapely.geometry import Point, shape
    ponto = Point(lng, lat)
    for feature in _geo_data["features"]:
        try:
            poligono = shape(feature["geometry"])
            if poligono.contains(ponto):
                return feature["properties"]["name"]
        except Exception:
            continue
    return None


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
    background: linear-gradient(145deg, #0D5C4A 0%, #1A8A6E 100%);
    border-radius: 14px; padding: 22px 18px; color: white;
    text-align: center; box-shadow: 0 3px 12px rgba(13,92,74,0.25);
    margin-bottom: 8px;
  }
  .kpi-value { font-size: 2rem; font-weight: 700; line-height: 1.1; margin: 0; }
  .kpi-label { font-size: 0.78rem; opacity: 0.78; margin: 6px 0 0 0;
               letter-spacing: 0.03em; text-transform: uppercase; }
  .hero {
    background: linear-gradient(135deg, #0D5C4A 0%, #1A8A6E 55%, #52C99E 100%);
    border-radius: 18px; padding: 32px 40px; margin-bottom: 28px;
  }
  .hero h1 { color: #FFFFFF !important; font-size: 2rem; margin: 0; }
  .hero p  { color: rgba(255,255,255,0.75); margin: 8px 0 0 0; font-size: 0.95rem; }
  .stTabs [aria-selected="true"] { color: #1A8A6E !important; font-weight: 600; }
  hr { border-color: #C8E6DE; }
  .footer { text-align: center; color: #999; font-size: 0.78rem; padding: 16px 0 4px; }
</style>
""", unsafe_allow_html=True)

# ── DADOS ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_ref_manager():
    return ReferencesManager()

@st.cache_data(show_spinner="Carregando referências bibliográficas…")
def carregar_refs():
    return get_ref_manager().load_and_clean()

ref_mgr = get_ref_manager()
df_refs = carregar_refs()

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>📚 Referências Bibliográficas</h1>
  <p>Análise de Distribuição Geográfica, Linguística e Circulação do Conhecimento · Cadernos Pagu (1993-2001)</p>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_refs = len(df_refs)
n_trad     = int(df_refs["Eh_Traducao"].sum())
pct_trad   = n_trad / total_refs * 100
top_lingua = df_refs["Lingua_Base"].value_counts().idxmax()
n_paises_r = df_refs["Pais_Ori_Base"].nunique()

rc1, rc2, rc3, rc4 = st.columns(4)
for col, val, lbl in [
    (rc1, f"{total_refs:,}", "Referências"),
    (rc2, str(n_paises_r),   "Países de origem"),
    (rc3, f"{pct_trad:.1f}%","Obras traduzidas"),
    (rc4, top_lingua,        "Língua dominante"),
]:
    with col:
        st.markdown(f"""<div class="kpi-card">
          <p class="kpi-value">{val}</p>
          <p class="kpi-label">{lbl}</p>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── ABAS ──────────────────────────────────────────────────────────────────────
r1, r2, r3 = st.tabs([
    "🌍  Distribuição Geográfica",
    "🔤  Distribuição Linguística",
    "🔄  Tradução e Circulação",
])

if "pais_selecionado_mapa" not in st.session_state:
    st.session_state["pais_selecionado_mapa"] = None

# ── R1: GEOGRÁFICA ────────────────────────────────────────────────────────────
with r1:
    col_rank, col_rmap = st.columns([1, 2])

    with col_rank:
        st.subheader("Países mais citados")
        opcao_geo = st.radio(
            "Por:", ["País de origem do autor", "País de publicação"],
            horizontal=True, label_visibility="collapsed",
        )
        col_geo = "Pais_Ori_Base" if opcao_geo == "País de origem do autor" else "Pais_Pub_Base"
        ranking = ref_mgr.get_geo_ranking(df_refs, coluna=col_geo, top_n=15)

        fig_rank = px.bar(
            ranking.sort_values("Referências"),
            x="Referências", y="País", orientation="h",
            color="Referências", color_continuous_scale="Greens",
            text="Referências",
        )
        fig_rank.update_traces(
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Referências: %{x}<extra></extra>",
        )
        fig_rank.update_layout(
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(245,243,240,0.5)",
            margin=dict(t=10, b=10, l=10, r=120),
            xaxis=dict(showgrid=True, gridcolor="#C8E6DE"), height=500,
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    with col_rmap:
        col_geo_map = "Pais_Ori_Geo" if opcao_geo == "País de origem do autor" else "Pais_Pub_Geo"
        contagem_r = df_refs[col_geo_map].value_counts().reset_index()
        contagem_r.columns = ["Pais", "Quantidade"]

        st.subheader("Mapa de referências por país")

        pais_sel = st.session_state["pais_selecionado_mapa"]

        if pais_sel:
            total_obras_pais = int(df_refs[
                (df_refs["Pais_Ori_Geo"] == pais_sel) &
                (df_refs["Eh_Traducao"] == True)
            ].shape[0])

            if total_obras_pais > 0:
                st.info(
                    f"🗺️ **{GEO_PARA_PT.get(pais_sel, pais_sel)}** selecionado — "
                    f"**{total_obras_pais} obras** de autores deste país foram traduzidas. "
                    f"Clique em outro país para mudar, ou no oceano para limpar."
                )
            else:
                st.info(
                    f"🗺️ **{GEO_PARA_PT.get(pais_sel, pais_sel)}** — "
                    f"nenhuma obra de autores deste país aparece como tradução nos dados. "
                    f"Clique em outro país."
                )
        else:
            st.caption("🖱️ Clique em um país para ver os fluxos de tradução de saída.")

        geo_data_r = carregar_geojson()

        count_dict_r = dict(zip(contagem_r["Pais"], contagem_r["Quantidade"]))
        for feature in geo_data_r["features"]:
            nome = feature["properties"]["name"]
            feature["properties"]["referencias"] = count_dict_r.get(nome, 0)

        if len(contagem_r) >= 2:
            vals_r = contagem_r["Quantidade"].values.astype(float)
            percentis_r = np.percentile(vals_r, [0, 25, 50, 75, 90, 100])
            bins_ref = sorted(set(
                [max(0.0, float(percentis_r[0]) - 1)] +
                [float(x) for x in percentis_r[1:5]] +
                [float(percentis_r[5]) + 1]
            ))
            if len(bins_ref) < 2:
                bins_ref = 6
        else:
            bins_ref = 6

        mr = folium.Map(location=[20, 10], zoom_start=1.5, tiles="CartoDB positron")

        choro_ref = folium.Choropleth(
            geo_data=geo_data_r,
            data=contagem_r,
            columns=["Pais", "Quantidade"],
            key_on="feature.properties.name",
            fill_color="YlGn",
            fill_opacity=0.75,
            line_opacity=0.2,
            legend_name="Número de referências por país",
            nan_fill_color="white",
            nan_fill_opacity=0.3,
            bins=bins_ref,
        )
        choro_ref.add_to(mr)
        choro_ref.color_scale.width = 600

        folium.GeoJson(
            geo_data_r,
            style_function=lambda x: {
                "fillColor": "transparent",
                "color": "transparent",
                "weight": 0,
                "fillOpacity": 0,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["name", "referencias"],
                aliases=["🌍 País", "📚 Referências"],
                localize=True,
                sticky=True,
                style=(
                    "background-color: #0D5C4A;"
                    "color: white;"
                    "border: none;"
                    "border-radius: 8px;"
                    "font-size: 13px;"
                    "padding: 8px 12px;"
                ),
            ),
        ).add_to(mr)

        # ── SETAS DE TRADUÇÃO ──────────────────────────────────────────────────
        if pais_sel:
            src_coords = CENTROIDES.get(pais_sel)
            lingua_origem = PAIS_PARA_LINGUA.get(pais_sel)
            cor = COR_LINGUA.get(lingua_origem, "#E74C3C") if lingua_origem else "#E74C3C"

            if src_coords:
                traducoes_do_pais = df_refs[
                    (df_refs["Pais_Ori_Geo"] == pais_sel) &
                    (df_refs["Eh_Traducao"] == True) &
                    (df_refs["Tgt_Lang"].notna())
                ]

                if len(traducoes_do_pais) == 0:
                    st.caption(
                        f"Nenhuma tradução encontrada com autoria original "
                        f"de {GEO_PARA_PT.get(pais_sel, pais_sel)}."
                    )
                else:
                    fluxos_reais = (
                        traducoes_do_pais
                        .groupby("Tgt_Lang")
                        .size()
                        .reset_index(name="count")
                        .sort_values("count", ascending=False)
                    )

                    folium.CircleMarker(
                        location=src_coords,
                        radius=10,
                        color=cor,
                        fill=True,
                        fill_color=cor,
                        fill_opacity=0.95,
                        tooltip=(
                            f"Origem: {GEO_PARA_PT.get(pais_sel, pais_sel)} | "
                            f"{len(traducoes_do_pais)} obras traduzidas"
                        ),
                    ).add_to(mr)

                    for _, row in fluxos_reais.iterrows():
                        lang_code_dest = row["Tgt_Lang"]
                        n_obras = int(row["count"])
                        paises_destino = LINGUA_PARA_PAISES.get(lang_code_dest, [])

                        for pais_dest in paises_destino:
                            dst_coords = CENTROIDES.get(pais_dest)
                            if not dst_coords or pais_dest == pais_sel:
                                continue

                            espessura = max(2, min(14, n_obras / 5))
                            nome_lingua_dest = LANG_NAMES.get(lang_code_dest, lang_code_dest)

                            folium.PolyLine(
                                locations=[src_coords, dst_coords],
                                color=cor,
                                weight=espessura,
                                opacity=0.85,
                                tooltip=(
                                    f"{GEO_PARA_PT.get(pais_sel, pais_sel)} → "
                                    f"{GEO_PARA_PT.get(pais_dest, pais_dest)}: "
                                    f"{n_obras} obras traduzidas para {nome_lingua_dest}"
                                ),
                            ).add_to(mr)

                            folium.CircleMarker(
                                location=dst_coords,
                                radius=max(6, min(20, n_obras / 3)),
                                color=cor,
                                fill=True,
                                fill_color=cor,
                                fill_opacity=0.75,
                                tooltip=(
                                    f"Destino: {GEO_PARA_PT.get(pais_dest, pais_dest)} "
                                    f"({nome_lingua_dest}) | {n_obras} obras"
                                ),
                            ).add_to(mr)

        mapa_retorno = st_folium(
            mr,
            width="100%",
            height=500,
            returned_objects=["last_clicked"],
            key="mapa_referencias",
        )

        if mapa_retorno and mapa_retorno.get("last_clicked"):
            lat_c = mapa_retorno["last_clicked"]["lat"]
            lng_c = mapa_retorno["last_clicked"]["lng"]
            pais_clicado = identificar_pais_clicado(lat_c, lng_c, geo_data_r)

            if pais_clicado != st.session_state["pais_selecionado_mapa"]:
                st.session_state["pais_selecionado_mapa"] = pais_clicado
                st.rerun()

    st.subheader("Evolução dos países mais citados por década")
    temporal_geo = ref_mgr.get_temporal_geo(df_refs, top_n=5)
    fig_temp_geo = px.line(
        temporal_geo, x="Decada", y="Referências",
        color="Pais_Ori_Base", markers=True,
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={"Pais_Ori_Base": "País", "Decada": "Década"},
    )
    fig_temp_geo.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(245,243,240,0.6)",
        xaxis=dict(showgrid=True, gridcolor="#C8E6DE", dtick=10),
        yaxis=dict(showgrid=True, gridcolor="#C8E6DE"),
        hovermode="x unified", legend_title="País",
    )
    st.plotly_chart(fig_temp_geo, use_container_width=True)

# ── R2: LINGUÍSTICA ───────────────────────────────────────────────────────────
with r2:
    col_ling1, col_ling2 = st.columns([3, 2])

    with col_ling1:
        st.subheader("Obras por língua")
        lingua_dist = ref_mgr.get_lingua_dist(df_refs)
        lingua_dist["Cor"] = lingua_dist["Língua"].map(LINGUA_CORES).fillna("#95A5A6")

        n_linguas = len(lingua_dist)
        altura_ling = max(300, n_linguas * 48)

        fig_ling = px.bar(
            lingua_dist.sort_values("Obras"),
            x="Obras", y="Língua", orientation="h",
            color="Língua",
            color_discrete_map=LINGUA_CORES,
            text="Obras",
        )
        fig_ling.update_traces(textposition="outside",
                               hovertemplate="<b>%{y}</b><br>Obras: %{x}<extra></extra>")
        fig_ling.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(245,243,240,0.5)",
            margin=dict(t=10, b=10, l=10, r=60),
            xaxis=dict(showgrid=True, gridcolor="#C8E6DE"), height=altura_ling,
        )
        st.plotly_chart(fig_ling, use_container_width=True)

    with col_ling2:
        st.subheader("Originais vs Traduções")
        orig_trad = ref_mgr.get_original_vs_traducao(df_refs)
        fig_ot = px.pie(
            orig_trad, values="Quantidade", names="Tipo", hole=0.45,
            color_discrete_map={"Obra original": "#1A8A6E", "Tradução": "#F39C12"},
        )
        fig_ot.update_traces(
            textposition="inside", textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{value} obras<br>%{percent}<extra></extra>",
        )
        fig_ot.update_layout(
            showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20, b=20, l=20, r=20), height=380,
        )
        st.plotly_chart(fig_ot, use_container_width=True)

    st.subheader("Evolução das línguas por década (1950–2000)")
    lingua_temp = ref_mgr.get_lingua_temporal(df_refs)
    fig_ling_temp = px.line(
        lingua_temp, x="Decada", y="Obras",
        color="Lingua_Base", markers=True,
        color_discrete_map=LINGUA_CORES,
        labels={"Lingua_Base": "Língua", "Decada": "Década"},
    )
    fig_ling_temp.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(245,243,240,0.6)",
        xaxis=dict(showgrid=True, gridcolor="#C8E6DE", dtick=10),
        yaxis=dict(showgrid=True, gridcolor="#C8E6DE"),
        hovermode="x unified", legend_title="Língua",
    )
    st.plotly_chart(fig_ling_temp, use_container_width=True)

# ── R3: TRADUÇÃO E CIRCULAÇÃO ─────────────────────────────────────────────────
with r3:
    sankey_data = ref_mgr.get_sankey_data(df_refs, min_count=3)

    st.subheader("Fluxo de tradução do conhecimento")
    st.caption(
        "Cada faixa conecta a língua de **origem** (esquerda) à língua de **destino** (direita). "
        "A espessura indica o número de obras. "
        "Cores identificam a língua de origem."
    )

    if sankey_data["nodes"]:
        node_color_map = {
            "Inglês": "#2980B9", "Português": "#27AE60", "Francês": "#E67E22",
            "Espanhol": "#E74C3C", "Alemão": "#8E44AD", "Italiano": "#16A085",
        }
        node_colors = [node_color_map.get(n, "#95A5A6") for n in sankey_data["nodes"]]

        pares_src = [sankey_data["nodes"][s] for s in sankey_data["sources"]]
        link_colors = []
        for src_name in pares_src:
            base = node_color_map.get(src_name, "#95A5A6")
            r = int(base[1:3], 16)
            g = int(base[3:5], 16)
            b = int(base[5:7], 16)
            link_colors.append(f"rgba({r},{g},{b},0.4)")

        fig_sankey = go.Figure(go.Sankey(
            arrangement="snap",
            node=dict(
                pad=20, thickness=24,
                label=sankey_data["nodes"],
                color=node_colors,
                hovertemplate="<b>%{label}</b><br>Fluxo total: %{value}<extra></extra>",
            ),
            link=dict(
                source=sankey_data["sources"],
                target=sankey_data["targets"],
                value=sankey_data["values"],
                color=link_colors,
                hovertemplate=(
                    "<b>%{source.label}</b> → <b>%{target.label}</b>"
                    "<br>%{value} obras<extra></extra>"
                ),
            ),
        ))
        fig_sankey.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", height=440,
            margin=dict(t=30, b=20, l=20, r=20),
            font=dict(size=13, color="#1E1240"),
        )
        st.plotly_chart(fig_sankey, use_container_width=True)

    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        st.subheader("Ranking de pares de tradução")
        df_pairs = sankey_data["pairs_df"].copy()
        df_pairs["Par"] = df_pairs["De"] + " → " + df_pairs["Para"]
        df_pairs["Cor"] = df_pairs["De"].map(
            {v: k_hex for v, k_hex in {
                "Inglês": "#2980B9", "Francês": "#E67E22", "Alemão": "#8E44AD",
                "Espanhol": "#E74C3C", "Italiano": "#16A085",
            }.items()}
        ).fillna("#95A5A6")

        fig_pairs = px.bar(
            df_pairs.head(10).sort_values("Obras"),
            x="Obras", y="Par", orientation="h",
            color="De",
            color_discrete_map={
                "Inglês": "#2980B9", "Francês": "#E67E22", "Alemão": "#8E44AD",
                "Espanhol": "#E74C3C", "Italiano": "#16A085",
            },
            text="Obras",
        )
        fig_pairs.update_traces(textposition="outside",
                                hovertemplate="<b>%{y}</b><br>Obras: %{x}<extra></extra>")
        fig_pairs.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(245,243,240,0.5)",
            margin=dict(t=10, b=10, l=10, r=50),
            xaxis=dict(showgrid=True, gridcolor="#C8E6DE"),
            legend_title="Língua de origem", height=400,
        )
        st.plotly_chart(fig_pairs, use_container_width=True)

    with col_t2:
        st.subheader("Todas as traduções catalogadas")
        st.dataframe(sankey_data["pairs_df"], use_container_width=True, height=400)

    st.download_button(
        "⬇️ Exportar dados de tradução (.csv)",
        data=sankey_data["pairs_df"].to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
        file_name="traducoes_cadernos_pagu.csv", mime="text/csv",
    )

st.markdown("""<hr>
<div style='text-align:center;color:#999;font-size:0.78rem;padding:16px 0 4px'>
  Cadernos Pagu Analytics · Referências Bibliográficas · Plataforma desenvolvida com Streamlit
</div>""", unsafe_allow_html=True)
