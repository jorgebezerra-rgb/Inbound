import streamlit as st
import pandas as pd
import altair as alt
from streamlit_autorefresh import st_autorefresh
import base64
import io

# --- Configuração da Página ---
st.set_page_config(
    page_title="Black Friday - Inbound",
    page_icon="📊",
    layout="wide"
)

#--- Faz a pagina atualizar a cada 5 minutos
st_autorefresh(interval=300 * 1000, key='data_refresh')


# --- Função para tocar o áudio A PARTIR DE UM ARQUIVO ---
def tocar_audio(caminho_arquivo):
    """Lê um arquivo de áudio local, converte para Base64 e o toca no Streamlit."""
    try:
        with open(caminho_arquivo, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay="true">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(
                md,
                unsafe_allow_html=True,
            )
    except FileNotFoundError:
        st.warning(f"Arquivo de áudio '{caminho_arquivo}' não encontrado. Coloque-o na mesma pasta do script.")

# --- Função para gerar um gráfico de medidor (velocímetro) ---
def gerar_grafico_medidor(valor, meta, altura=200):
    """
    Gera o código HTML/SVG para um gráfico de medidor com faixas de cor precisas e limite de 150%.
    """
    if meta is None or meta == 0:
        percentual = 0
    else:
        percentual = (valor / meta) * 100

    angulo_ponteiro = -90 + (min(percentual, 150) * 1.2)

    # Cores ATUALIZADAS para o tema escuro
    COR_VERMELHO = "#DC143C"
    COR_LARANJA = "#FFBF00"
    COR_VERDE = "#31859c"
    COR_PONTEIRO = "#ffffff"

    cor_valor_atual = COR_VERMELHO
    if percentual > 40 and percentual <= 90:
        cor_valor_atual = COR_LARANJA
    elif percentual > 90:
        cor_valor_atual = COR_VERDE

    RAIO = 80
    LARGURA_TRACO = 25
    PERIMETRO_TOTAL_ARCO = 3.14159 * RAIO

    comprimento_vermelho = PERIMETRO_TOTAL_ARCO * (40 / 150)
    comprimento_laranja = PERIMETRO_TOTAL_ARCO * ((90 - 40) / 150)
    comprimento_verde = PERIMETRO_TOTAL_ARCO * ((150 - 90) / 150)

    offset_laranja = -comprimento_vermelho
    offset_verde = -(comprimento_vermelho + comprimento_laranja)

    html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; font-family: sans-serif; height: {altura}px;">
        <svg viewBox="0 0 200 120" style="width: 100%; height: auto; overflow: visible;">
            <path d="M 20 100 A {RAIO} {RAIO} 0 0 1 180 100" fill="none" stroke="{COR_VERMELHO}" stroke-width="{LARGURA_TRACO}"
                  stroke-dasharray="{comprimento_vermelho} {PERIMETRO_TOTAL_ARCO}" />
            <path d="M 20 100 A {RAIO} {RAIO} 0 0 1 180 100" fill="none" stroke="{COR_LARANJA}" stroke-width="{LARGURA_TRACO}"
                  stroke-dasharray="{comprimento_laranja} {PERIMETRO_TOTAL_ARCO}" stroke-dashoffset="{offset_laranja}" />
            <path d="M 20 100 A {RAIO} {RAIO} 0 0 1 180 100" fill="none" stroke="{COR_VERDE}" stroke-width="{LARGURA_TRACO}"
                  stroke-dasharray="{comprimento_verde} {PERIMETRO_TOTAL_ARCO}" stroke-dashoffset="{offset_verde}" />
            <g transform="translate(100, 100)">
                <line x1="0" y1="0" x2="0" y2="-65" stroke="{COR_PONTEIRO}" stroke-width="4" transform="rotate({angulo_ponteiro} 0 0)" />
                <circle cx="0" cy="0" r="8" fill="{COR_PONTEIRO}" />
                <circle cx="0" cy="0" r="4" fill="white" />
            </g>
            <text x="20" y="115" font-size="14" fill="#666" text-anchor="start">0%</text>
            <text x="180" y="115" font-size="14" fill="#666" text-anchor="end">150%</text>
        </svg>
        <div style="font-size: 28px; font-weight: bold; text-align: center; margin-top: -85px; color: {cor_valor_atual};">
            {percentual:.1f}%
        </div>
        <div style="font-size: 16px; text-align: center; color: #666; margin-top: 30px;">
            Atingimento
        </div>
    </div>
    """
    return html



# --- Carregamento e Tratamento dos Dados ---
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbPgQ6euKLUaDZzAYKEZ-prfTh3V0Pj1skjdqssT1P6wZuQudV2ey0RhCkHYpR7DX322Hqth6ZyHOT/pub?gid=0&single=true&output=csv"
    try:
        df_completo = pd.read_csv(url, thousands='.')
        df_grafico = df_completo[['Horas', 'Meta Hora', 'Produção Hora']].head(10).copy()
        for coluna in ['Horas', 'Meta Hora', 'Produção Hora']:
            df_grafico[coluna] = pd.to_numeric(df_grafico[coluna], errors='coerce')
        df_grafico.fillna(0, inplace=True)
        df_grafico = df_grafico.astype(int)
        produzido_total = df_grafico['Produção Hora'].sum()
        projecao_final = pd.to_numeric(df_completo['Projeção '].dropna().iloc[-1], errors='coerce')
        return produzido_total, projecao_final, df_grafico
    except Exception as e:
        st.error(f"Não foi possível carregar os dados da planilha. Erro: {e}")
        return 0, 0, pd.DataFrame()


# --- Interface do Dashboard ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("dafiti.gif", width=120)
with col2:
    st.title("Black Friday - Inbound")

st.markdown("""<style>
[data-testid="stMetricValue"] { font-size: 50px; }
[data-testid="stMetricLabel"] { font-size: 20px; }
</style>""", unsafe_allow_html=True)

produzido, projecao, df = carregar_dados()

st.header("Resumo do Dia")
st.divider()

atingimento = (produzido / projecao) * 100 if projecao else 0

if atingimento >= 100:
    st.balloons()
    tocar_audio("som_meta_batida.mp3")

col1, col2, col3 = st.columns(3)
col1.metric("Produzido (Total)", f"{produzido or 0:,.0f}".replace(",", "."))
col2.metric("Projeção", f"{projecao or 0:,.0f}".replace(",", "."))
col3.metric("Atingimento da Projeção", f"{atingimento:.2f} %")

st.divider()

# --- Layout dos Gráficos ---
col_medidor, col_barras = st.columns([1, 3])

with col_medidor:
    st.markdown("<h3 style='text-align: center;'>Atingimento da Projeção</h3>", unsafe_allow_html=True)
    html_medidor = gerar_grafico_medidor(produzido, projecao)
    st.components.v1.html(html_medidor, height=250)


with col_barras:
    st.markdown("<h3 style='text-align: center;'>Produção por Hora</h3>", unsafe_allow_html=True)
    if not df.empty:
        base = alt.Chart(df).encode(
            x=alt.X('Horas:O',
                    title='Horas do Dia',
                    axis=alt.Axis(
                        labelAngle=0,
                        labelFontSize=15,
                        titleFontSize=16,
                        domain=False,
                        ticks=False,
                        labelColor='white',
                        titleColor='white'
                    ))
        ).properties(height=400)

        barras = base.mark_bar(
            size=60,
            cornerRadiusTopLeft=8,
            cornerRadiusTopRight=8
        ).encode(
            y=alt.Y('Produção Hora:Q',
                    title='Quantidade Produzida',
                    axis=alt.Axis(
                        grid=True,
                        gridColor='#2e2f37',
                        gridDash=[1, 5],
                        domain=False,
                        ticks=False,
                        labelFontSize=14,
                        titleFontSize=16,
                        labelColor='white',
                        titleColor='white'
                    )),
            tooltip=['Horas', 'Produção Hora', 'Meta Hora'],
            color=alt.condition(
                alt.datum['Produção Hora'] >= alt.datum['Meta Hora'],
                alt.value('#31859c'),
                alt.value('#DC143C')
            )
        )

        linha = base.mark_line(
            color='#9bbb59',
            strokeWidth=5,
            interpolate='monotone'
        ).encode(
            y=alt.Y('Meta Hora:Q', title=''),
            tooltip=['Horas', 'Produção Hora', 'Meta Hora']
        )
        
        texto_barras = barras.mark_text(
            align='center', baseline='middle', dy=-15, fontSize=15, fontWeight='bold'
        ).encode(text='Produção Hora:Q', color=alt.value('white'))

        grafico_combinado = (alt.layer(barras, linha, texto_barras)
                             .configure_view(
                                 stroke=None
                             ).configure_axis(
                                 labelFont='sans-serif',
                                 titleFont='sans-serif'
                             ))

        st.altair_chart(grafico_combinado, use_container_width=True)
    else:
        st.warning("Não há dados para exibir no gráfico.")
