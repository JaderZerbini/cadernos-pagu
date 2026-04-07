# 🚀 Guia de Deploy — Cadernos Pagu Analytics

## Plataforma recomendada: Streamlit Community Cloud

> **Por que não Netlify?**
> O Netlify só hospeda sites estáticos (HTML/JS). O projeto usa Python + Streamlit,
> então o servidor precisa rodar Python. O Streamlit Community Cloud foi feito
> exatamente para isso — e é **gratuito**.

---

## Passo a passo

### 1. Subir o projeto no GitHub

```bash
git init
git add .
git commit -m "Cadernos Pagu Analytics - versão inicial"
git branch -M main
git remote add origin https://github.com/JaderZerbini/cadernos-pagu.git
git push -u origin main
```

**Estrutura esperada no repositório:**
```
cadernos-pagu/
├── app.py
├── requirements.txt
├── models/
│   └── data_manager.py
└── data/
    └── raw/
        └── Doutorado_DADOS_GERAIS_cadernos_pagu.csv
```

### 2. Criar conta no Streamlit Cloud

Acesse: https://share.streamlit.io  
Faça login com a conta do GitHub.

### 3. Criar o app

1. Clique em **"New app"**
2. Selecione o repositório `cadernos-pagu`
3. Branch: `main`
4. Main file path: `app.py`
5. Clique em **"Deploy!"**

Aguarde 2–3 minutos. O app vai estar disponível em:
`https://SEU_USUARIO-cadernos-pagu.streamlit.app`

---

## Alternativas gratuitas

| Plataforma | Indicada para | Link |
|---|---|---|
| **Streamlit Cloud** ⭐ | Apps Streamlit (ideal) | share.streamlit.io |
| Hugging Face Spaces | Demos de pesquisa | huggingface.co/spaces |
| Render | Apps Python em geral | render.com |

---

## ⚠️ Atenção ao CSV

O arquivo de dados **não deve ser commitado publicamente** se contiver
informações sigilosas. Nesse caso, use a aba "Secrets" do Streamlit Cloud
para armazenar caminhos ou credenciais, ou adicione o arquivo via
`st.file_uploader` na própria interface.

Para uso acadêmico sem dados sensíveis, commitar o CSV junto ao repo é o
caminho mais simples.
