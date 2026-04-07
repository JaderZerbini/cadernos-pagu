import pandas as pd
import os
import unicodedata


# ── NORMALIZAÇÃO ──────────────────────────────────────────────────────────────
def _norm(texto: str) -> str:
    """Remove acentos e converte para lowercase para comparação."""
    nfkd = unicodedata.normalize("NFKD", str(texto).strip())
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


# ── MAPA: texto normalizado → nome exato do GeoJSON (Natural Earth) ───────────
# O GeoJSON do folium usa nomes em inglês do Natural Earth.
# Cobrir variantes, abreviações, erros tipográficos em PT e EN.
MAPA_GEO: dict[str, str] = {
    # ── América do Sul ────────────────────────────────────────────────────────
    "brasil": "Brazil", "brazil": "Brazil", "br": "Brazil",
    "argentina": "Argentina",
    "chile": "Chile",
    "colombia": "Colombia", "colombia": "Colombia",
    "peru": "Peru",
    "uruguai": "Uruguay", "uruguay": "Uruguay",
    "bolivia": "Bolivia",
    "venezuela": "Venezuela",
    "paraguai": "Paraguay", "paraguay": "Paraguay",
    "equador": "Ecuador", "ecuador": "Ecuador",
    "guiana": "Guyana", "guyana": "Guyana",
    "suriname": "Suriname",
    # ── América Central e Caribe ──────────────────────────────────────────────
    "cuba": "Cuba",
    "mexico": "Mexico",
    "costa rica": "Costa Rica",
    "guatemala": "Guatemala",
    "honduras": "Honduras",
    "nicaragua": "Nicaragua",
    "panama": "Panama",
    "el salvador": "El Salvador",
    "republica dominicana": "Dominican Republic",
    "haiti": "Haiti",
    "jamaica": "Jamaica",
    "porto rico": "Puerto Rico",
    # ── América do Norte ──────────────────────────────────────────────────────
    "eua": "United States of America",
    "e.u.a": "United States of America",
    "e.u.a.": "United States of America",
    "estados unidos": "United States of America",
    "estados unidos da america": "United States of America",
    "estados unidos da america do norte": "United States of America",
    "usa": "United States of America",
    "us": "United States of America",
    "united states": "United States of America",
    "united states of america": "United States of America",
    "canada": "Canada",
    # ── Europa Ocidental ──────────────────────────────────────────────────────
    "franca": "France", "france": "France",
    "reino unido": "United Kingdom",
    "gra-bretanha": "United Kingdom",
    "gra bretanha": "United Kingdom",
    "inglatera": "United Kingdom",   # erro tipográfico frequente
    "inglaterra": "United Kingdom",
    "escocia": "United Kingdom",
    "gales": "United Kingdom",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "espanha": "Spain", "spain": "Spain",
    "portugal": "Portugal",
    "italia": "Italy", "italy": "Italy",
    "alemanha": "Germany", "germany": "Germany",
    "austria": "Austria",
    "belgica": "Belgium", "belgium": "Belgium",
    "holanda": "Netherlands",
    "paises baixos": "Netherlands",
    "netherlands": "Netherlands",
    "suica": "Switzerland", "switzerland": "Switzerland",
    "irlanda": "Ireland", "ireland": "Ireland",
    "luxemburgo": "Luxembourg",
    # ── Europa do Norte ───────────────────────────────────────────────────────
    "suecia": "Sweden", "sweden": "Sweden",
    "noruega": "Norway", "norway": "Norway",
    "dinamarca": "Denmark", "denmark": "Denmark",
    "finlandia": "Finland", "finland": "Finland",   # ← FIX: Finlândia → Finland
    "islandia": "Iceland", "iceland": "Iceland",
    # ── Europa do Leste ───────────────────────────────────────────────────────
    "russia": "Russia",
    "polonia": "Poland", "poland": "Poland",
    "republica tcheca": "Czech Republic",
    "chequia": "Czech Republic",
    "czech republic": "Czech Republic",
    "hungria": "Hungary", "hungary": "Hungary",
    "romenia": "Romania", "romania": "Romania",
    "bulgaria": "Bulgaria",
    "croacia": "Croatia",
    "eslovaquia": "Slovakia",
    "eslovenia": "Slovenia",
    "servia": "Serbia",
    "ucrania": "Ukraine",
    # ── Europa do Sul e Mediterrâneo ──────────────────────────────────────────
    "grecia": "Greece", "greece": "Greece",
    "turquia": "Turkey", "turkey": "Turkey",
    "israel": "Israel",
    # ── Ásia ─────────────────────────────────────────────────────────────────
    "japao": "Japan", "japan": "Japan",
    "china": "China",
    "india": "India",
    "coreia do sul": "South Korea",
    "south korea": "South Korea",
    "taiwan": "Taiwan",
    "indonesia": "Indonesia",
    "filipinas": "Philippines",
    "tailandia": "Thailand",
    "vietna": "Vietnam", "vietnam": "Vietnam",
    "malásia": "Malaysia", "malaysia": "Malaysia",
    "singapura": "Singapore",
    "paquistao": "Pakistan",
    "bangladesh": "Bangladesh",
    "iraque": "Iraq",
    "ira": "Iran",
    "arabia saudita": "Saudi Arabia",
    "emirados arabes unidos": "United Arab Emirates",
    # ── África ───────────────────────────────────────────────────────────────
    "africa do sul": "South Africa",
    "south africa": "South Africa",
    "nigeria": "Nigeria",
    "egito": "Egypt", "egypt": "Egypt",
    "kenya": "Kenya",
    "etiopia": "Ethiopia",
    "tanzania": "Tanzania",
    "marrocos": "Morocco", "morocco": "Morocco",
    "angola": "Angola",
    "mocambique": "Mozambique",
    "senegal": "Senegal",
    # ── Oceania ───────────────────────────────────────────────────────────────
    "australia": "Australia",
    "nova zelandia": "New Zealand",
}

# ── NOMES EM PORTUGUÊS para exibição na UI ────────────────────────────────────
GEO_PARA_PT: dict[str, str] = {
    "Brazil": "Brasil",
    "United States of America": "EUA",
    "France": "França",
    "Mexico": "México",
    "Argentina": "Argentina",
    "United Kingdom": "Reino Unido",
    "Spain": "Espanha",
    "Portugal": "Portugal",
    "Italy": "Itália",
    "Germany": "Alemanha",
    "Chile": "Chile",
    "Colombia": "Colômbia",
    "Peru": "Peru",
    "Uruguay": "Uruguai",
    "Bolivia": "Bolívia",
    "Venezuela": "Venezuela",
    "Cuba": "Cuba",
    "Canada": "Canadá",
    "Australia": "Austrália",
    "Japan": "Japão",
    "China": "China",
    "India": "Índia",
    "South Africa": "África do Sul",
    "Switzerland": "Suíça",
    "Belgium": "Bélgica",
    "Netherlands": "Países Baixos",
    "Sweden": "Suécia",
    "Norway": "Noruega",
    "Denmark": "Dinamarca",
    "Finland": "Finlândia",
    "Russia": "Rússia",
    "Poland": "Polônia",
    "Czech Republic": "República Tcheca",
    "Turkey": "Turquia",
    "Greece": "Grécia",
    "Israel": "Israel",
    "Nigeria": "Nigéria",
    "Costa Rica": "Costa Rica",
    "Paraguay": "Paraguai",
    "Ecuador": "Equador",
    "South Korea": "Coreia do Sul",
    "Morocco": "Marrocos",
    "Egypt": "Egito",
    "Angola": "Angola",
    "Mozambique": "Moçambique",
    "Hungary": "Hungria",
    "Romania": "Romênia",
    "Austria": "Áustria",
    "Ireland": "Irlanda",
    "Iceland": "Islândia",
    "Ukraine": "Ucrânia",
    "New Zealand": "Nova Zelândia",
}


class DataManager:
    def __init__(self):
        base = os.path.dirname(os.path.dirname(__file__))
        self.raw_path    = os.path.join(base, "data", "raw")
        self.output_path = os.path.join(base, "data", "processed")
        os.makedirs(self.output_path, exist_ok=True)

    # ─────────────────────────────────────────────────────────────────────────
    def load_and_clean(self) -> tuple[pd.DataFrame, int]:
        """
        Carrega, limpa e processa o CSV.
        Retorna (df_limpo, n_descartados).
        """
        filepath = os.path.join(
            self.raw_path, "Doutorado_DADOS_GERAIS_cadernos_pagu.csv"
        )
        df = self._ler_csv(filepath)

        # Normaliza cabeçalhos
        df.columns = [c.strip().upper() for c in df.columns]

        # Detecta colunas por nome canônico ou variantes
        col_ano   = self._col(df, ["ANO", "YEAR"])
        col_tit   = self._col(df, ["TÍTULO", "TITULO", "TITLE", "ARTIGO"])
        col_autor = self._col(df, ["AUTORIA", "AUTOR", "AUTORES", "AUTHOR"])
        col_local = self._col(df, [
            "LOCALIZAÇÃO_DA_AUTORIA_(PAÍS)",
            "LOCALIZACAO_DA_AUTORIA_(PAIS)",
            "LOCALIZAÇÃO DA AUTORIA (PAÍS)",
            "LOCALIZACAO DA AUTORIA (PAIS)",
            "PAÍS", "PAIS", "LOCALIZAÇÃO", "LOCALIZACAO", "COUNTRY",
        ])
        col_ling = self._col(df, [
            "LÍNGUA DE PUBLICAÇÃO", "LINGUA DE PUBLICACAO",
            "LÍNGUA", "LINGUA", "LANGUAGE",
        ])
        col_trad = self._col(df, [
            "TRADUTOR(A)", "TRADUTORA", "TRADUTOR",
            "QUAIS TRADUÇÕES", "QUAIS TRADUCOES", "TRANSLATOR",
        ])

        criticas = [c for c in [col_ano, col_autor, col_local] if c]

        # Substitui ruído por NaN
        ruido = {"x", "X", "nan", "NaN", " ", "", "-", "--", "N/D", "n/d", "s/d", "S/D"}
        df = df.replace(list(ruido), pd.NA)

        # Auditoria: remove duplicatas e registros incompletos
        df = df.drop_duplicates(subset=criticas)
        mask_nulos = df[criticas].isna().any(axis=1)
        df_descart = df[mask_nulos]
        df_limpo   = df[~mask_nulos].copy()
        n_descartados = len(df_descart)

        df_descart.to_csv(
            os.path.join(self.output_path, "dados_descartados.csv"),
            index=False, encoding="utf-8-sig"
        )

        # ── Colunas derivadas ─────────────────────────────────────────────────
        df_limpo["Ano"] = (
            pd.to_numeric(df_limpo[col_ano], errors="coerce")
            .fillna(0).astype(int)
        )

        # País: GeoJSON (inglês) e Base (português amigável)
        df_limpo["Pais_Geo"]  = df_limpo[col_local].apply(self._resolver_geo)
        df_limpo["Pais_Base"] = df_limpo["Pais_Geo"].apply(
            lambda x: GEO_PARA_PT.get(x, x)
        )

        df_limpo["Língua"]  = df_limpo[col_ling].fillna("N/A") if col_ling else "N/A"
        df_limpo["Tradução"] = df_limpo[col_trad].fillna("Não traduzido") if col_trad else "Não traduzido"

        df_limpo["Eh_Internacional"] = df_limpo["Pais_Geo"] != "Brazil"

        # Normaliza nomes canônicos das colunas de texto
        if col_tit and col_tit != "TÍTULO":
            df_limpo = df_limpo.rename(columns={col_tit: "TÍTULO"})
        elif not col_tit:
            df_limpo["TÍTULO"] = "Sem título"

        if col_autor and col_autor != "AUTORIA":
            df_limpo = df_limpo.rename(columns={col_autor: "AUTORIA"})
        elif not col_autor:
            df_limpo["AUTORIA"] = "Sem autoria"

        # Exporta base limpa para auditoria
        df_limpo.to_csv(
            os.path.join(self.output_path, "dados_processados.csv"),
            index=False, encoding="utf-8-sig"
        )

        return df_limpo, n_descartados

    # ─────────────────────────────────────────────────────────────────────────
    def get_timeline_data(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "AUTORIA" not in df.columns:
            return pd.DataFrame(columns=["Ano", "Total", "Internacionais", "% Internacional"])

        stats = (
            df.groupby("Ano")
            .agg(Total=("AUTORIA", "count"), Internacionais=("Eh_Internacional", "sum"))
            .reset_index()
        )
        stats["% Internacional"] = (
            stats["Internacionais"] / stats["Total"] * 100
        ).round(2)
        return stats

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _ler_csv(path: str) -> pd.DataFrame:
        """Tenta múltiplos encodings; lida com arquivos exportados pelo Excel."""
        for enc in ("utf-8-sig", "latin-1", "utf-8", "cp1252"):
            try:
                return pd.read_csv(path, encoding=enc)
            except (UnicodeDecodeError, Exception):
                continue
        raise ValueError(f"Não foi possível ler o arquivo: {path}")

    @staticmethod
    def _col(df: pd.DataFrame, candidatos: list[str]) -> str | None:
        """Retorna o nome real da coluna, buscando por lista de candidatos."""
        for c in candidatos:
            if c in df.columns:
                return c
        # Busca parcial normalizada (robustez contra espaços e acentos extras)
        for candidato in candidatos:
            nc = _norm(candidato)
            for col in df.columns:
                if nc in _norm(col) or _norm(col) in nc:
                    return col
        return None

    def _resolver_geo(self, valor) -> str:
        """
        Mapeia um valor bruto do CSV para o nome exato do GeoJSON.
        Etapas: (1) pega o 1º país se houver múltiplos, (2) normaliza,
        (3) busca exata, (4) busca parcial, (5) retorna original.
        """
        if pd.isna(valor):
            return "Desconhecido"

        # Separa múltiplos países (ex: "Brasil/França")
        primeiro = (
            str(valor).split("/")[0].split("\\")[0]
                      .split(";")[0].split(",")[0].strip()
        )
        chave = _norm(primeiro)

        if chave in MAPA_GEO:
            return MAPA_GEO[chave]

        # Busca parcial — ex: "Brasil (SP)" → "brasil"
        for k, v in MAPA_GEO.items():
            if chave.startswith(k) or k.startswith(chave):
                return v

        # Valor não mapeado — retorna capitalizado para auditoria manual
        return primeiro.title()
