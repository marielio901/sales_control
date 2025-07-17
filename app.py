import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from PIL import Image

st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

# Carregamento da planilha
@st.cache_data
def carregar_dados():
    df = pd.read_excel("vendas.xlsx")
    df["Data da Venda"] = pd.to_datetime(df["Data da Venda"])
    df["Ano"] = df["Data da Venda"].dt.year
    df["Mês"] = df["Data da Venda"].dt.month
    return df

df = carregar_dados()

# Função para formatar números grandes
def formatar_moeda(valor):
    if valor >= 1_000_000_000:
        return f"R$ {valor / 1_000_000_000:.2f} Bilhões"
    elif valor >= 1_000_000:
        return f"R$ {valor / 1_000_000:.2f} Milhões"
    elif valor >= 1_000:
        return f"R$ {valor / 1_000:.2f} mil"
    else:
        return f"R$ {valor:.2f}"

def estrela_html(qtd):
    return "<span style='font-size: 22px;'>" + "⭐" * qtd + "</span>"

def carregar_foto(nome_arquivo):
    with open(nome_arquivo, "rb") as f:
        data = f.read()
    return f"data:image/png;base64,{base64.b64encode(data).decode()}"

# Sidebar - Filtros
st.sidebar.markdown("""
    <h1 style='font-size: 30px; color: #42AF99; text-align: center;'>
        Controle de Vendas
    </h1>
""", unsafe_allow_html=True)
anos = [st.sidebar.selectbox("Ano", sorted(df["Ano"].unique(), reverse=True))]
estados = st.sidebar.multiselect("Estado", sorted(df["Estado"].unique()), default=sorted(df["Estado"].unique()))
vendedores = st.sidebar.multiselect("Vendedor", sorted(df["Nome do vendedor"].unique()), default=sorted(df["Nome do vendedor"].unique()))

# Aplicar filtros
df_filtrado = df[
    (df["Ano"].isin(anos)) &
    (df["Estado"].isin(estados)) &
    (df["Nome do vendedor"].isin(vendedores))
]

# KPIs
st.title("📊 Dashboard de Vendas de Carros")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    total_vendas = df_filtrado['Valor de venda'].sum()
    st.markdown(f"""
    <div style='background-color:#1f2937; height: 130px; width: 100%; padding: 16px; display: flex; flex-direction: column; justify-content: center; align-items: center; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.3)'>
    <h3 style='color:white; text-align: center; margin: 0;'>💰 Total de Vendas</h3>
    <h2 style='color:#10B981; font-size: 42px; text-align: center; margin: 0;'>{formatar_moeda(total_vendas)}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background-color:#1f2937; height: 130px; width: 100%; padding: 16px; display: flex; flex-direction: column; justify-content: center; align-items: center; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.3)'>
        <h3 style='color:white; text-align: center; margin: 0;'>📈 Lucro Total</h3>
        <h2 style='color:#10B981; font-size: 42px; text-align: center; margin: 0;'>{formatar_moeda(df_filtrado['lucro da venda'].sum())}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background-color:#1f2937; height: 130px; width: 100%; padding: 16px; display: flex; flex-direction: column; justify-content: center; align-items: center; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.3)'>
        <h3 style='color:white; text-align: center; margin: 0;'>🧾 Ticket Médio</h3>
        <h2 style='color:#10B981; font-size: 42px; text-align: center; margin: 0;'>{formatar_moeda(df_filtrado['Valor de venda'].mean())}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style='background-color:#1f2937; height: 130px; width: 100%; padding: 16px; display: flex; flex-direction: column; justify-content: center; align-items: center; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.3)'>
        <h3 style='color:white; text-align: center; margin: 0;'>🛒 Quantidade de Vendas</h3>
        <h2 style='color:#10B981; font-size: 42px; text-align: center; margin: 0;'>{df_filtrado.shape[0]:,} unidades</h2>
    </div>
    """, unsafe_allow_html=True)

# Gráficos com Plotly em colunas
col1, col2 = st.columns(2)

with col1:
    st.markdown("""<h2 style='font-size: 30px; color: white; margin-bottom: 10px;'>📅 Vendas por Mês</h2>""", unsafe_allow_html=True)

    if len(anos) == 1:
        df_mes = df_filtrado[df_filtrado["Ano"] == anos[0]]
        vendas_mes = df_mes.groupby(df_mes["Data da Venda"].dt.month)[["Valor de venda"]].sum().reset_index()

        meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        vendas_mes["Mês"] = vendas_mes["Data da Venda"].apply(lambda x: meses_nomes[x - 1])
        vendas_mes = vendas_mes.sort_values("Data da Venda")

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=vendas_mes["Mês"],
            y=vendas_mes["Valor de venda"],
            mode="lines+markers",
            line=dict(color="#42AF99", shape="spline", width=3),
            marker=dict(color="#42AF99", size=8),
            hovertemplate='Valor de Vendas: R$ %{y:,.2f}<extra></extra>'
        ))

        fig1.update_layout(
            template="plotly_dark",
            xaxis_title="Mês",
            yaxis_title="Valor Total de Vendas",
            margin=dict(t=40, b=40),
            height=400
        )

        st.plotly_chart(fig1, use_container_width=True)

    else:
        st.warning("Selecione apenas um ano para visualizar o gráfico mensal.")




with col2:
    st.subheader("Vendas por Fabricante")
    fabricantes = df_filtrado.groupby("Fabricante")["Valor de venda"].sum().reset_index()
    fabricantes["Percentual"] = fabricantes["Valor de venda"] / fabricantes["Valor de venda"].sum() * 100

    # Cores variadas com base no #42AF99, mantendo harmonia com o dashboard
    cores_personalizadas = [
        "#1A69D1",  # Verde água principal
        "#D61576",  # Azul petróleo
        "#345857",  # Verde suave
        "#CE9823",  # Azul claro
        "#5A267C",  # Verde menta
        "#2C9B5A"   # Verde azulado
    ]

    fig2 = px.pie(
        fabricantes,
        values="Percentual",
        names="Fabricante",
        hole=0.5,
        template="plotly_dark",
        title="Participação de Vendas por Fabricante"
    )

    fig2.update_traces(
        textinfo="percent+label",
        textfont_size=18,
        marker=dict(colors=cores_personalizadas, line=dict(color='black', width=2))
    )

    fig2.update_layout(font_color="white")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Distribuição Geográfica e Lucro por Estado")
col3, col4 = st.columns(2, gap="medium")

with col3:
    lucros_estado = df_filtrado.groupby("Estado")["lucro da venda"].sum().reset_index().sort_values(by="lucro da venda", ascending=False)
    fig_col = px.bar(
        lucros_estado,
        x="Estado",
        y="lucro da venda",
        labels={"lucro da venda": "Lucro Total"},
        template="plotly_dark",
        color_discrete_sequence=["#42AF99"]
    )
    fig_col.update_traces(
        text=lucros_estado["lucro da venda"].apply(formatar_moeda),
        textposition="outside",
        textfont_size=24
    )
    fig_col.update_layout(title="Lucro por Estado", xaxis_tickfont=dict(size=16))
    st.plotly_chart(fig_col, use_container_width=True)

with col4:
    vendas_estado = df_filtrado.groupby("Estado")["Valor de venda"].sum().reset_index()
    vendas_estado["Percentual"] = vendas_estado["Valor de venda"] / vendas_estado["Valor de venda"].sum() * 100

    coordenadas_estados = {
        "AC": [-70.55, -9.02], "AL": [-36.55, -9.71], "AM": [-63.90, -3.07], "AP": [-51.77, 1.41],
        "BA": [-41.71, -12.27], "CE": [-39.29, -5.20], "DF": [-47.93, -15.78], "ES": [-40.33, -19.55],
        "GO": [-49.38, -15.98], "MA": [-45.27, -5.42], "MG": [-44.55, -18.10], "MS": [-54.54, -20.51],
        "MT": [-56.10, -12.64], "PA": [-52.29, -3.79], "PB": [-36.72, -7.12], "PE": [-36.95, -8.28],
        "PI": [-42.79, -7.72], "PR": [-51.55, -24.89], "RJ": [-43.20, -22.90], "RN": [-36.52, -5.80],
        "RO": [-63.90, -11.22], "RR": [-61.37, 2.82], "RS": [-51.23, -30.03], "SC": [-49.40, -27.33],
        "SE": [-37.44, -10.57], "SP": [-46.63, -23.55], "TO": [-48.20, -10.25]
    }

    vendas_estado["lon"] = vendas_estado["Estado"].map(lambda x: coordenadas_estados.get(x, [0, 0])[0])
    vendas_estado["lat"] = vendas_estado["Estado"].map(lambda x: coordenadas_estados.get(x, [0, 0])[1])

    fig_mapa = px.choropleth(
        vendas_estado,
        geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        locations="Estado",
        featureidkey="properties.sigla",
        color="Percentual",
        color_continuous_scale=["#D1F2EB", "#42AF99", "#0E6655"],
        labels={"Percentual": "% de Vendas"},
        scope="south america",
        template="plotly_dark"
    )

    max_pct = vendas_estado["Percentual"].max()
    for _, row in vendas_estado.iterrows():
        tamanho = 15 + (row['Percentual'] / max_pct) * 60
        fig_mapa.add_trace(go.Scattergeo(
            lon=[row["lon"]],
            lat=[row["lat"]],
            text=f"{row['Percentual']:.2f}%",
            mode='markers+text',
            textposition="middle center",
            textfont=dict(color="white", size=18),
            marker=dict(size=tamanho, color="rgba(0,0,0,0.7)", line=dict(color="white", width=1)),
            showlegend=False
        ))

    fig_mapa.update_geos(fitbounds="locations", visible=True)
    fig_mapa.update_layout(height=500, margin={"r":0,"t":10,"l":0,"b":0})
    st.plotly_chart(fig_mapa, use_container_width=True)

# 🪙 Ranking de Vendas
st.subheader("🪙 Ranking de Vendas")
col1, col2, col3, col4 = st.columns(4)

vendedores_nomes = ["Ana Clara Nogueira", "Francisco Castro", "Gustavo Mendes", "Samuel Rezende"]
arquivos_fotos = ["imagens/1- Ana Clara Nogueira.png", "imagens/2- Francisco Castro.png", "imagens/3- Gustavo Mendes.png", "imagens/4- Samuel Rezende.png"]

# Ranqueamento por vendas totais
df_ranking = df_filtrado.groupby("Nome do vendedor")["Valor de venda"].sum().reset_index().sort_values(by="Valor de venda", ascending=False)
ranking_dict = {nome: i+1 for i, nome in enumerate(df_ranking["Nome do vendedor"].tolist())}

for i, (col, nome, foto) in enumerate(zip([col1, col2, col3, col4], vendedores_nomes, arquivos_fotos)):
    df_vend = df_filtrado[df_filtrado["Nome do vendedor"] == nome]
    total = df_vend["Valor de venda"].sum()
    media = df_vend["Valor de venda"].mean()
    qtd = df_vend.shape[0]
    posicao = ranking_dict.get(nome, 4)

    if posicao == 1:
        estrelas = 7
    elif posicao == 2:
        estrelas = 5
    elif posicao == 3:
        estrelas = 4
    else:
        estrelas = 3

    col.markdown(f"""
        <div style='background-color: #1f2937; padding: 12px 12px 24px 12px; border-radius: 10px; margin-bottom: 20px;'>
            <div style='display: flex; align-items: center;'>
                <img src='{carregar_foto(foto)}' width='100' style='border-radius: 50%; margin-right: 12px;'>
                <div>
                    <h3 style='color:white; margin: 4px 0; font-size: 36px;'>{nome}</h3>
                    {estrela_html(estrelas)}
                </div>
            </div>
            <p style='color:#10B981;margin:8px 0;'>💹 Média de Venda: <strong>{formatar_moeda(media)}</strong></p>
            <p style='color:#10B981;margin:4px 0;'>💰 Total Vendido: <strong>{formatar_moeda(total)}</strong></p>
            <p style='color:#10B981;margin:4px 0;'>📦 Total de Vendas: <strong>{qtd} unidades</strong></p>
        </div>
    """, unsafe_allow_html=True)

    df_vend_mes = df_vend.groupby(df_vend["Data da Venda"].dt.month).size().reset_index(name="Quantidade")
    df_vend_mes["Mês"] = df_vend_mes["Data da Venda"]
    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    df_vend_mes["Mês Nome"] = df_vend_mes["Mês"].apply(lambda x: meses_nomes[x-1])

    fig = px.line(
        df_vend_mes,
        x="Mês Nome",
        y="Quantidade",
        markers=True,
        template="plotly_dark",
        line_shape="spline"
    )
    fig.update_traces(
        text=df_vend_mes["Quantidade"],
        textposition="top center",
        line=dict(color="#42AF99", width=3)
    )
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
    col.plotly_chart(fig, use_container_width=True)

# 📋 Tabela de Vendas
st.subheader("📋 Tabela de Vendas")

# Formatação personalizada
import pandas as pd
df_exibicao = df_filtrado.copy()

# Garantindo formatação de 'Lucro da Venda' como reais, se já existir
if 'lucro da venda' in df_exibicao.columns:
    df_exibicao['lucro da venda'] = df_exibicao['lucro da venda'].apply(lambda x: f'R$ {float(str(x).replace("R$", "").replace(".", "").replace(",", ".")):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notnull(x) else x)

# Formatando colunas de data
colunas_data = [col for col in df_exibicao.columns if 'Data' in col]
for col in colunas_data:
    df_exibicao[col] = df_exibicao[col].dt.strftime('%d/%m/%Y')

# Formatando colunas de dinheiro (incluindo 'Comissão')
colunas_dinheiro = [col for col in df_exibicao.columns if 'Valor' in col or 'Preço' in col or 'Comissão' in col or 'Custo' in col or 'lucro' in col]
for col in colunas_dinheiro:
    df_exibicao[col] = df_exibicao[col].apply(lambda x: f'R$ {float(str(x).replace("R$", "").replace(".", "").replace(",", ".")):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notnull(x) else x)

# Formatando colunas de porcentagem com indicadores
colunas_porcentagem = [col for col in df_exibicao.columns if ('%' in col or 'Taxa' in col or 'Porcentagem' in col) and 'Comissão' not in col]
for col in colunas_porcentagem:
    def formatar_percentual(valor):
        percentual = valor * 100
        if percentual > 30:
            return f'🟢▲ {percentual:.2f}%'
        else:
            return f'🔴▼ {percentual:.2f}%'
    df_exibicao[col] = df_exibicao[col].apply(formatar_percentual)

# Exibindo
st.dataframe(df_exibicao.reset_index(drop=True), use_container_width=True)
