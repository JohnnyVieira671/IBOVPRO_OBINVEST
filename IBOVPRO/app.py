import streamlit as st
import plotly.express as px
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests 
import numpy as np
from pathlib import Path

# Configuração da Página - Layout Wide para ar de Dashboard Profissional
st.set_page_config(page_title="IBOV Pro | Terminal", page_icon="📈", layout="wide")

# --- ARQUITETURA DE DESIGN (CSS ADVANCED) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');

    /* Reset e Variáveis */
    :root {
        --bg-deep: #0B0E14;
        --card-bg: #151921;
        --border-color: #262C36;
        --accent-color: #00E676;
        --text-main: #E2E8F0;
        --text-dim: #94A3B8;
    }

    .stApp {
        background-color: var(--bg-deep);
        color: var(--text-main);
    }

    /* Header e Logo Area */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.5rem 3rem;
        background: rgba(21, 25, 33, 0.8);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 2rem;
        position: sticky;
        top: 0;
        z-index: 99;
    }

    /* Container de Conteúdo */
    .block-container {
        padding-top: 1rem !important;
        max-width: 1400px;
    }

    /* Cards e Formulários */
    div[data-testid="stForm"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }

    /* Botão de Ação (Venda/Mercado) */
   /* Botão de Ação Corrigido */
    div[data-testid="stForm"] button {
    background: linear-gradient(135deg, #00E676 0%, #00C853 100%) !important;
    color: #000000 !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 12px !important;
    width: 100%;
    }

    /* Garante que o texto continue visível no hover */
    div[data-testid="stForm"] button:hover {
    background: #00FF88 !important;
    color: #000000 !important;
    }

    /* Estilo das Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #1A1F29 !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px 10px 0 0 !important;
        padding: 10px 25px !important;
        color: var(--text-dim) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stTabs [aria-selected="true"] {
        border-top: 3px solid var(--accent-color) !important;
        color: white !important;
        background-color: var(--card-bg) !important;
    }

    /* Tabelas e Dataframes */
    .stDataFrame {
        border: 1px solid var(--border-color);
        border-radius: 12px;
    }

    /* Custom Labels */
    label {
        color: var(--text-dim) !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }

    /* Footer */
    .terminal-footer {
        padding: 2rem;
        text-align: center;
        border-top: 1px solid var(--border-color);
        color: #475569;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)


# # --- TOP NAVIGATION / HEADER ---
LOGO = Path(__file__).parent / "assets" / "logo.png"
c1, c2 = st.columns([1, 8], gap="small")
with c1:
    # Fundo branco com padding
    st.markdown("""
    <div style=padding-top:60px;">
    """, unsafe_allow_html=True)
    st.image(LOGO, use_container_width=True)  # ⚡ atualizado
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div style="margin-top: 40px; display:flex; justify-content:space-between; align-items:center;">
        <h2 style="font-family:'Plus Jakarta Sans'; font-weight:700; color:#fff; margin:0;">
            IBOV <span style="color:#00E676">PRO</span>
        </h2>
        <div style="font-family:'JetBrains Mono'; color:#00E676; 
                    background: rgba(0,230,118,0.1); padding: 5px 15px; 
                    border-radius: 20px; font-size: 0.8rem; white-space: nowrap;">
            ● DADOS DE MERCADO EM TEMPO REAL
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# CORE ENGINE (FUNCIONALIDADES MANTIDAS)
# -----------------------------
url = "https://pt.wikipedia.org/wiki/Lista_de_companhias_citadas_no_Ibovespa"
response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
tabelas = pd.read_html(response.text)
df_wiki = tabelas[0]
ibov_tickers = [ticker for ticker in df_wiki["Código"]]

aba_grafico, aba_tabela, aba_retorno = st.tabs([
    "🔭 ANÁLISES", 
    "⛓️ CORRELAÇÃO",
    "🏆 RANKING"
])
intervalo = "1d"

# --- ABA 1: ANALYTICS ---
with aba_grafico:
    st.markdown("### Analise de ativos")
    with st.form("form_visual"):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
        with c1:
            ativo_selecionado = st.selectbox("ATIVO", ibov_tickers)
        with c2:
            data_inicio = st.date_input("INÍCIO", value=datetime.today() - timedelta(days=365))
        with c3:
            data_fim = st.date_input("FIM")
        with c4:
            unidade_tempo = st.selectbox("AGRUPAMENTO", ["Diária", "Mensal", "Anual"])
        
        btn_grafico = st.form_submit_button("EXECUTAR ANÁLISE")

    if btn_grafico:
        prazin = abs(data_fim - data_inicio)
        hoje = datetime.today()

        if unidade_tempo == "Diária":
            tempo, intervalo, prazo, inicio = "dias", "1d", prazin.days, hoje - timedelta(days=prazin.days)
        elif unidade_tempo == "Mensal":
            tempo, intervalo, prazo, inicio = "meses", "1mo", prazin.days // 30, hoje - relativedelta(months=int(prazin.days // 30))
        else:
            tempo, intervalo, prazo, inicio = "anos", "1mo", prazin.days // 365, hoje - relativedelta(years=int(prazin.days // 365))

        with st.spinner("Sincronizando com Yahoo Finance..."):
            df = yf.Ticker(ativo_selecionado + ".SA").history(
                start=inicio.strftime("%Y-%m-%d"), end=hoje.strftime("%Y-%m-%d"), interval=intervalo
            )

            if not df.empty:
                if unidade_tempo == "Anual":
                    df['Ano'] = df.index.year
                    df = df.groupby('Ano')[["Open", "High", "Low", "Close", "Volume"]].mean()

                df["Cotação"] = df[["Open", "High", "Low", "Close"]].mean(axis=1)
                
                # Gráfico Estilo Terminal
                fig = px.area(df, x=df.index, y="Cotação", title=f"Performance Histórica: {ativo_selecionado}")
                fig.update_traces(line_color='#00E676', fillcolor='rgba(0, 230, 118, 0.1)', line_width=3)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font_color="#94A3B8", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#262C36")
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df.style.format(precision=2), use_container_width=True)

# --- ABA 2: CORRELAÇÃO ---
with aba_tabela:
    st.markdown("### Matriz de Interdependência de Ativos")
    with st.form("form_corr"):
        col_1, col_2, col_3 = st.columns([3, 1, 1])
        with col_1:
            ativos_selecionados = st.multiselect("SELECIONE OS TICKERS", ibov_tickers)
        with col_2:
            qtd = st.number_input("QUANTIDADE", min_value=1, value=30)
        with col_3:
            tempo = st.selectbox("ESCALA", ["Dias", "Meses", "Anos"])
        
        btn_corr = st.form_submit_button("GERAR MATRIZ")

    if btn_corr:
        if len(ativos_selecionados) >= 2:
            hoje = datetime.today()
            if tempo == "Dias": inicio = hoje - timedelta(days=qtd)
            elif tempo == "Meses": inicio = hoje - relativedelta(months=qtd)
            else: inicio = hoje - relativedelta(years=qtd)

            precos = pd.DataFrame()
            
            with st.spinner("Carregando...."):
                for t in ativos_selecionados:
                    d = yf.Ticker(t + ".SA").history(start=inicio.strftime("%Y-%m-%d"), end=hoje.strftime("%Y-%m-%d"))
                    if not d.empty: precos[t] = d["Close"]

            if not precos.empty:
                retornos_log = np.log(precos / precos.shift(1)).dropna()
                correlacao = retornos_log.corr()
                fig = px.imshow(
                                    correlacao, 
                                    text_auto=".2f", 
                                    color_continuous_scale="RdBu",
                                    aspect="auto",
                                    zmin=-1, zmax=1 
                                )
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("📋 Ver dados de retornos logarítmicos"):
                    st.dataframe(retornos_log.style.format(precision=4), use_container_width=True)
                
        else:
            st.error("Selecione pelo menos 2 ativos.")

# --- ABA 3: RANKING ---
with aba_retorno:
    st.markdown("### Líderes e retardatários do mercado")
    with st.form("form_rank"):
        r1, r2 = st.columns(2)
        with r1:
            qtd_ret = st.number_input("PERÍODO DE ANÁLISE", min_value=1, value=7)
        with r2:
            tempo_ret = st.selectbox("UNIDADE DE MEDIDA", ["Dias", "Meses", "Anos"])
        btn_rank = st.form_submit_button("SCANNER DE MERCADO")

    if btn_rank:
        hoje = datetime.today()
        if tempo_ret == "Dias": inicio = hoje - timedelta(days=qtd_ret)
        elif tempo_ret == "Meses": inicio = hoje - relativedelta(months=qtd_ret)
        else: inicio = hoje - relativedelta(years=qtd_ret)
        
        dados_retorno = []
        progress_text = "Mapeando Ativos..."
        my_bar = st.progress(0, text=progress_text)
        
        with st.spinner("Carregando...."):
            for i, ticker in enumerate(ibov_tickers):
                df_r = yf.Ticker(ticker + ".SA").history(start=inicio.strftime("%Y-%m-%d"), end=hoje.strftime("%Y-%m-%d"))
                if not df_r.empty:
                    ret = np.log(df_r["Close"].iloc[-1] / df_r["Open"].iloc[0]) * 100
                    dados_retorno.append([ticker, ret])
                my_bar.progress((i + 1) / len(ibov_tickers))
        
        st.session_state.dados_retorno = dados_retorno
        my_bar.empty()

    if "dados_retorno" in st.session_state and st.session_state.dados_retorno:
        df_rank = pd.DataFrame(st.session_state.dados_retorno, columns=["Ticker", "Retorno (%)"])
        toggle = st.toggle("ORDEM CRESCENTE", value=False)
        df_rank = df_rank.sort_values("Retorno (%)", ascending=toggle)
        
        st.dataframe(
            df_rank.style.format({"Retorno (%)": "{:.2f}%"}).background_gradient(cmap="RdBu", subset=["Retorno (%)"]),
            use_container_width=True, hide_index=True
        )

# --- FOOTER ---
st.markdown("""
    <div class="terminal-footer">
        SISTEMA DE ANÁLISE QUANTITATIVA IBOV PRO | VERSION 2.4.0 | DATA VIA YFINANCE PROTOCOL
    </div>
""", unsafe_allow_html=True)