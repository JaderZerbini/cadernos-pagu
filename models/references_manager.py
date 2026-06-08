import pandas as pd
import os
import re
import unicodedata


def _norm(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", str(texto).strip())
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


# Código de idioma → nome completo em PT
LANG_NAMES: dict[str, str] = {
    "PT": "Português", "EN": "Inglês", "FR": "Francês",
    "ES": "Espanhol", "DE": "Alemão", "IT": "Italiano",
    "RU": "Russo", "PL": "Polonês", "NL": "Neerlandês",
    "GR": "Grego",
}

# País normalizado → nome do GeoJSON  (None = descartar)
MAPA_GEO_REFS: dict[str, str | None] = {
    "brasil": "Brazil",
    "eua": "United States of America",
    "estados unidos": "United States of America",
    "eu": "United States of America",
    "providence, eua": "United States of America",
    "franca": "France",
    "alemanha": "Germany",
    "argentina": "Argentina",
    "australia": "Australia",
    "belgica": "Belgium",
    "canada": "Canada",
    "chile": "Chile",
    "colombia": "Colombia",
    "costa rica": "Costa Rica",
    "cuba": "Cuba",
    "dinamarca": "Denmark",
    "escocia": "United Kingdom",
    "espanha": "Spain",
    "grecia": "Greece",
    "grecia antiga": "Greece",
    "guatemala": "Guatemala",
    "hungria": "Hungary",
    "india": "India",
    "inglaterra": "United Kingdom",
    "italia": "Italy",
    "japao": "Japan",
    "mexico": "Mexico",
    "mocambique": "Mozambique",
    "monaco": "France",          # Mônaco → agrupa em França para o mapa
    "noruega": "Norway",
    "pais de gales": "United Kingdom",
    "paises baixos": "Netherlands",
    "panama": "Panama",
    "polonia": "Poland",
    "portugal": "Portugal",
    "portugual": "Portugal",     # typo na planilha
    "reino unido": "United Kingdom",
    "ruanda": "Rwanda",
    "russia": "Russia",
    "suecia": "Sweden",
    "suica": "Switzerland",
    "uruguai": "Uruguay",
    "venezuela": "Venezuela",
    "africa do sul": "South Africa",
    "austria": "Austria",
    "angola": "Angola",
    # Entradas combinadas → primeiro país
    "eua e canada": "United States of America",
    "eua e inglaterra": "United States of America",
    "brasil e eua": "Brazil",
    "brasil e franca": "Brazil",
    "australia e nova zelandia": "Australia",
    "canada e franca": "Canada",
    "franca e canada": "France",
    "inglaterra/eua": "United Kingdom",
    "monaco e franca": "France",
    # Entradas inválidas → None
    "paises nordicos": None,
    "america latina": None,
    "rio de janeiro": "Brazil",  # cidade → país
    "ingles": None,              # erro de preenchimento
    "(informacao nao disponivel - periodico)": None,
}

GEO_PARA_PT: dict[str, str] = {
    "Brazil": "Brasil", "United States of America": "EUA",
    "France": "França", "Germany": "Alemanha", "Argentina": "Argentina",
    "Australia": "Austrália", "Belgium": "Bélgica", "Canada": "Canadá",
    "Chile": "Chile", "Colombia": "Colômbia", "Costa Rica": "Costa Rica",
    "Cuba": "Cuba", "Denmark": "Dinamarca", "Greece": "Grécia",
    "Guatemala": "Guatemala", "Hungary": "Hungria", "India": "Índia",
    "Italy": "Itália", "Japan": "Japão", "Mexico": "México",
    "Mozambique": "Moçambique", "Netherlands": "Países Baixos",
    "Norway": "Noruega", "Panama": "Panamá", "Poland": "Polônia",
    "Portugal": "Portugal", "Rwanda": "Ruanda", "Russia": "Rússia",
    "Spain": "Espanha", "Sweden": "Suécia", "Switzerland": "Suíça",
    "United Kingdom": "Reino Unido", "Uruguay": "Uruguai",
    "Venezuela": "Venezuela", "South Africa": "África do Sul",
    "Austria": "Áustria", "Angola": "Angola",
}


LINGUAS_VALIDAS = {
    "Inglês", "Português", "Francês", "Espanhol", "Alemão",
    "Italiano", "Polonês", "Russo", "Grego antigo", "Bilíngue",
    "Neerlandês", "Latim",
}


class ReferencesManager:
    def __init__(self):
        base = os.path.dirname(os.path.dirname(__file__))
        self.raw_path    = os.path.join(base, "data", "raw")
        self.output_path = os.path.join(base, "data", "processed")
        os.makedirs(self.output_path, exist_ok=True)

    # ── CARGA ─────────────────────────────────────────────────────────────────
    def load_and_clean(self) -> pd.DataFrame:
        filepath = os.path.join(self.raw_path, "CP_DADOS_GERAIS__REFERENCIAS_.xlsx")
        df = pd.read_excel(filepath)
        df.columns = [c.strip() for c in df.columns]

        df = df.rename(columns={
            "Autoria": "Autoria",
            "Localização de onde foi publicada a obra referenciada": "Pais_Pub_Raw",
            "Data de publicação da obra referenciada":               "Ano_Raw",
            "Língua da publicação - tradução":                       "Lingua_Raw",
            "Localização da autoria original":                       "Pais_Ori_Raw",
            "Referência completa como consta no artigo":             "Referencia",
        })

        df["Ano"]    = pd.to_numeric(df["Ano_Raw"],  errors="coerce").astype("Int64")
        df["Decada"] = (df["Ano"] // 10 * 10).astype("Int64")

        # Geolocalização
        df["Pais_Pub_Geo"]  = df["Pais_Pub_Raw"].apply(self._resolver_geo)
        df["Pais_Pub_Base"] = df["Pais_Pub_Geo"].apply(lambda x: GEO_PARA_PT.get(x, x) if x else None)
        df["Pais_Ori_Geo"]  = df["Pais_Ori_Raw"].apply(self._resolver_geo)
        df["Pais_Ori_Base"] = df["Pais_Ori_Geo"].apply(lambda x: GEO_PARA_PT.get(x, x) if x else None)

        # Língua
        df["Lingua_Base"] = df["Lingua_Raw"].apply(self._lingua_base)
        df["Eh_Traducao"] = df["Lingua_Raw"].apply(self._eh_traducao)
        df["Src_Lang"]    = df["Lingua_Raw"].apply(lambda x: self._par_traducao(x)[0])
        df["Tgt_Lang"]    = df["Lingua_Raw"].apply(lambda x: self._par_traducao(x)[1])

        return df

    # ── MÉTODOS DE ANÁLISE ────────────────────────────────────────────────────
    def get_geo_ranking(self, df: pd.DataFrame, coluna: str = "Pais_Ori_Base",
                        top_n: int = 15) -> pd.DataFrame:
        """Top N países por número de referências."""
        counts = (
            df[coluna].dropna()
            .value_counts().head(top_n)
            .reset_index()
        )
        counts.columns = ["País", "Referências"]
        return counts

    def get_temporal_geo(self, df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
        """Evolução por década dos top N países de origem (1950+)."""
        top_paises = df["Pais_Ori_Base"].value_counts().head(top_n).index.tolist()
        filtrado = df[
            df["Pais_Ori_Base"].isin(top_paises)
            & df["Decada"].notna()
            & (df["Decada"] >= 1950)
        ]
        result = (
            filtrado.groupby(["Decada", "Pais_Ori_Base"])
            .size().reset_index(name="Referências")
        )
        result["Decada"] = result["Decada"].astype(int)
        return result

    def get_lingua_dist(self, df: pd.DataFrame) -> pd.DataFrame:
        counts = (
            df["Lingua_Base"]
            .dropna()
            .loc[lambda s: s.isin(LINGUAS_VALIDAS)]
            .value_counts()
            .reset_index()
        )
        counts.columns = ["Língua", "Obras"]
        return counts

    def get_original_vs_traducao(self, df: pd.DataFrame) -> pd.DataFrame:
        total     = len(df.dropna(subset=["Lingua_Raw"]))
        traducoes = int(df["Eh_Traducao"].sum())
        originais = total - traducoes
        return pd.DataFrame({
            "Tipo":       ["Obra original", "Tradução"],
            "Quantidade": [originais, traducoes],
        })

    def get_lingua_temporal(self, df: pd.DataFrame) -> pd.DataFrame:
        filtrado = df[
            df["Lingua_Base"].isin(LINGUAS_VALIDAS)
            & df["Decada"].notna()
            & (df["Decada"] >= 1950)
        ]
        result = (
            filtrado.groupby(["Decada", "Lingua_Base"])
            .size().reset_index(name="Obras")
        )
        result["Decada"] = result["Decada"].astype(int)
        return result

    def get_sankey_data(self, df: pd.DataFrame, min_count: int = 3) -> dict:
        """Dados para o diagrama Sankey de fluxos de tradução."""
        pares = (
            df[df["Eh_Traducao"] & df["Src_Lang"].notna() & df["Tgt_Lang"].notna()]
            .groupby(["Src_Lang", "Tgt_Lang"])
            .size()
            .reset_index(name="count")
        )
        pares = pares[pares["count"] >= min_count].copy()

        nodes_raw = list(set(pares["Src_Lang"].tolist() + pares["Tgt_Lang"].tolist()))
        node_idx  = {n: i for i, n in enumerate(nodes_raw)}

        pairs_df = pares.copy()
        pairs_df["De"]   = pairs_df["Src_Lang"].map(LANG_NAMES).fillna(pairs_df["Src_Lang"])
        pairs_df["Para"] = pairs_df["Tgt_Lang"].map(LANG_NAMES).fillna(pairs_df["Tgt_Lang"])
        pairs_df = pairs_df[["De", "Para", "count"]].rename(columns={"count": "Obras"})

        return {
            "nodes":    [LANG_NAMES.get(n, n) for n in nodes_raw],
            "sources":  [node_idx[s] for s in pares["Src_Lang"]],
            "targets":  [node_idx[t] for t in pares["Tgt_Lang"]],
            "values":   pares["count"].tolist(),
            "pairs_df": pairs_df.sort_values("Obras", ascending=False).reset_index(drop=True),
        }

    # ── HELPERS ───────────────────────────────────────────────────────────────
    def _resolver_geo(self, valor) -> str | None:
        if pd.isna(valor):
            return None
        chave = _norm(str(valor))
        if chave in MAPA_GEO_REFS:
            return MAPA_GEO_REFS[chave]
        for k, v in MAPA_GEO_REFS.items():
            if k and len(k) >= 5 and chave.startswith(k):
                return v
        raw = str(valor).split("/")[0].strip()
        return raw.title() if raw else None

    @staticmethod
    def _lingua_base(valor) -> str:
        if pd.isna(valor):
            return ""
        return str(valor).strip().split("(")[0].strip()

    @staticmethod
    def _eh_traducao(valor) -> bool:
        return ">" in str(valor)

    @staticmethod
    def _par_traducao(valor) -> tuple[str | None, str | None]:
        if pd.isna(valor):
            return None, None
        m = re.search(r"\((?:tradução\s+)?([A-Z]{2})\s*[>→]\s*([A-Z]{2})", str(valor))
        if m:
            return m.group(1), m.group(2)
        return None, None
