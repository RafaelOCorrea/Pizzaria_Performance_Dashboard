import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CARREGAMENTO E TRANSFORMAÇÃO DOS DADOS ---
@st.cache_data
def load_data():
    # Caminho corrigido e verificado
    file_path = 'pizza_sales_data.csv'

    if not os.path.exists(file_path):
        st.error(f"Erro: Arquivo de dados '{file_path}' não encontrado. Verifique o nome/local.")
        return pd.DataFrame() 

    # Leitura com tratamento para diferentes codificações
    try:
        df_sales = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df_sales = pd.read_csv(file_path, encoding='latin1')
    
    # 1. Limpeza e Renomeação
    df_sales.columns = [col.lower().replace('_', ' ') for col in df_sales.columns]
    # Tratamento da coluna de data/hora
    # O .dt.tz_localize(None) garante que a data seja limpa para uso local
    df_sales['order datetime'] = pd.to_datetime(df_sales['order datetime'], utc=True, errors='coerce').dt.tz_localize(None)

    df_sales = df_sales.rename(columns={
        'order id': 'ID pedido',
        'quantity': 'Quantidade do Pedido',
        'total item value': 'Valor Total por Item',
        'order datetime': 'Data Hora do Pedido',
        'month name': 'Nome do Mês',
        'day of week': 'Dia da Semana',
        'hour of day': 'Hora do Dia',
        'pizza name': 'Nome da Pizza',
        'pizza category': 'Categoria Pizza',
        'pizza size': 'Tamanho da Pizza'
    })
    
    # Adicionar coluna de número do mês para ordenação
    df_sales['Numero do Mês'] = df_sales['Data Hora do Pedido'].dt.month
    
    return df_sales

df_sales = load_data()

# Verifica se o DataFrame foi carregado antes de calcular os KPIs
if df_sales.empty:
    st.stop()


# --- 2. FUNÇÕES DE CÁLCULO DE KPIS GLOBAIS ---
def calculate_kpis(df):
    faturamento_total = df['Valor Total por Item'].sum()
    volume_de_vendas = df['Quantidade do Pedido'].sum()
    quantidade_de_pedidos = df['ID pedido'].nunique()
    
    if quantidade_de_pedidos > 0:
        ticket_medio_por_pedido = faturamento_total / quantidade_de_pedidos
    else:
        ticket_medio_por_pedido = 0
        
    return faturamento_total, volume_de_vendas, quantidade_de_pedidos, ticket_medio_por_pedido

# Funções de Formatação BRL (Para os cards)
def format_brl(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".").replace("R$ X", "R$ ")

def format_int(value):
    return f"{value:,.0f}".replace(",", ".")


# --- 3. CONFIGURAÇÃO DO LAYOUT STREAMLIT E FILTROS ---
st.set_page_config(layout="wide", page_title="Farinha Boa - Dash de Performance")

st.title("🍕 Dashboard de Performance de Vendas - Pizzaria Farinha Boa")
st.markdown("Monitoramento de Performance e Insights Estratégicos")

# --- BARRA LATERAL (SIDEBAR) PARA FILTRO ---
st.sidebar.header("Filtros de Análise")

# 1. FILTRO TEMPORAL (NOVO)
# Extrai as datas mínimas e máximas
df_data_min = df_sales['Data Hora do Pedido'].min().to_pydatetime().date()
df_data_max = df_sales['Data Hora do Pedido'].max().to_pydatetime().date()

st.sidebar.subheader("Intervalo de Tempo")
data_inicio = st.sidebar.date_input("Data de Início", value=df_data_min, min_value=df_data_min, max_value=df_data_max)
data_fim = st.sidebar.date_input("Data de Fim", value=df_data_max, min_value=df_data_min, max_value=df_data_max)

# Lógica de validação do filtro temporal
if data_inicio > data_fim:
    st.sidebar.error("Erro: A Data de Início não pode ser maior que a Data de Fim. Ajustando Data de Fim.")
    data_fim = data_inicio


# 2. FILTRO POR CATEGORIA (Existente)
categorias_limpas = df_sales['Categoria Pizza'].fillna('Não Categorizado').unique()
categorias = ['Todas'] + list(categorias_limpas)
st.sidebar.subheader("Filtro de Produto")

categoria_selecionada = st.sidebar.selectbox(
    "Selecione a Categoria de Pizza:",
    options=categorias
)

# --- LÓGICA DE FILTRAGEM MULTI-CRITÉRIO ---
df_temp = df_sales.copy()

# A. Filtrar por Categoria
if categoria_selecionada != 'Todas':
    df_temp = df_temp[df_temp['Categoria Pizza'] == categoria_selecionada].copy()

# B. Filtrar por Data (Aplicando o filtro temporal)
# Compara a parte da data da coluna 'Data Hora do Pedido' com as datas selecionadas
df_sales_filtered = df_temp[
    (df_temp['Data Hora do Pedido'].dt.date >= data_inicio) & 
    (df_temp['Data Hora do Pedido'].dt.date <= data_fim)
].copy()

# Tratamento de erro após o filtro (se o usuário filtrou para algo vazio)
if df_sales_filtered.empty:
    st.warning("Nenhum dado encontrado para o intervalo de tempo e categoria selecionados.")
    # Usamos o DataFrame vazio para que os KPIs e gráficos mostrem zero
else:
    # Recalcula KPIs com o DataFrame filtrado
    faturamento_total, volume_de_vendas, quantidade_de_pedidos, ticket_medio_por_pedido = calculate_kpis(df_sales_filtered)


# --- 4. EXIBIÇÃO DOS KPIS (COM FILTRO) ---
st.header("Indicadores-Chave de Desempenho (KPIs)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Faturamento Total", value=format_brl(faturamento_total))

with col2:
    st.metric(label="Volume de Vendas (Pizzas)", value=format_int(volume_de_vendas))

with col3:
    st.metric(label="Total de Pedidos", value=format_int(quantidade_de_pedidos))
    
with col4:
    st.metric(label="Ticket Médio por Pedido", value=format_brl(ticket_medio_por_pedido))


st.markdown("---")


# --- 5. GRÁFICO 1: TENDÊNCIA MENSAL DE FATURAMENTO (CORRIGIDO) ---
st.header("📈 Tendência de Faturamento Mensal (Sazonalidade)")

# Mapeamento para garantir que os meses sejam exibidos em português
MONTH_MAP = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

# 1. Agrupamento pelo Número do Mês (garantindo a ordem)
# Verifica se o DF não está vazio antes de agrupar para evitar erro
if not df_sales_filtered.empty:
    df_mensal = df_sales_filtered.groupby('Numero do Mês')['Valor Total por Item'].sum().reset_index()
    df_mensal = df_mensal.rename(columns={'Valor Total por Item': 'Faturamento Mensal'})

    # 2. Adiciona o nome do mês em português (apenas para exibição)
    df_mensal['Nome do Mês PT'] = df_mensal['Numero do Mês'].map(MONTH_MAP)

    # 3. Ordena pelo Número do Mês
    df_mensal = df_mensal.sort_values(by='Numero do Mês', ascending=True)

    # Lista de nomes ordenados para forçar o eixo X
    MESES_ORDENADOS = df_mensal['Nome do Mês PT'].tolist()
    
    fig_mensal = px.line(
        df_mensal,
        x='Nome do Mês PT', # Usamos a nova coluna para o eixo X
        y='Faturamento Mensal',
        markers=True,
        title='Evolução do Faturamento ao Longo do Ano',
        labels={'Nome do Mês PT': 'Mês', 'Faturamento Mensal': 'Faturamento (R$)'}
    )
    fig_mensal.update_traces(line_color='#FF4B4B')
    fig_mensal.update_layout(xaxis_title=None)

    # Forçamos o Plotly a usar a ordem exata da lista gerada
    fig_mensal.update_xaxes(categoryorder='array', categoryarray=MESES_ORDENADOS)

    st.plotly_chart(fig_mensal, use_container_width=True)
else:
    st.info("O gráfico de Tendência Mensal está vazio devido ao filtro selecionado.")


# --- 6. GRÁFICOS DE PERFORMANCE (DIA E HORA) ---

st.markdown("---")

st.header("🎯 Análise de Performance: Dia da Semana e Hora")

col5, col6 = st.columns(2)

if not df_sales_filtered.empty:
    # GRÁFICO 2: Volume de Vendas por Dia da Semana
    df_dia = df_sales_filtered.groupby(['Dia da Semana'])['Quantidade do Pedido'].sum().reset_index()

    # Garantindo a ordem correta dos dias da semana
    order_dia = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    order_dia_pt = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']

    df_dia['Dia da Semana PT'] = pd.Categorical(df_dia['Dia da Semana'].map(dict(zip(order_dia, order_dia_pt))), categories=order_dia_pt, ordered=True)
    df_dia = df_dia.sort_values('Dia da Semana PT')

    fig_dia = px.bar(
        df_dia,
        x='Dia da Semana PT',
        y='Quantidade do Pedido',
        title='Volume de Vendas por Dia da Semana',
        labels={'Dia da Semana PT': 'Dia da Semana', 'Quantidade do Pedido': 'Volume de Pizzas Vendidas'},
        color='Quantidade do Pedido',
        color_continuous_scale=px.colors.sequential.Reds
    )
    fig_dia.update_layout(xaxis_title=None)

    with col5:
        st.subheader("Quando Vender Mais?")
        st.plotly_chart(fig_dia, use_container_width=True)


    # GRÁFICO 3: Vendas por Hora do Dia
    df_hora = df_sales_filtered.groupby('Hora do Dia')['Quantidade do Pedido'].sum().reset_index()

    fig_hora = px.bar(
        df_hora,
        x='Hora do Dia',
        y='Quantidade do Pedido',
        title='Distribuição de Vendas por Hora',
        labels={'Hora do Dia': 'Hora', 'Quantidade do Pedido': 'Volume de Pizzas Vendidas'},
        color_continuous_scale=px.colors.sequential.Reds
    )
    fig_hora.update_layout(xaxis_title='Hora do Dia', yaxis_title='Volume de Vendas')

    with col6:
        st.subheader("Melhores Horários para a Cozinha")
        st.plotly_chart(fig_hora, use_container_width=True)
else:
    st.info("Os gráficos de Performance (Dia e Hora) estão vazios devido ao filtro selecionado.")


# --- 7. GRÁFICOS DE PRODUTO (RANKING E CATEGORIA) ---

st.markdown("---")

st.header("🍕 Análise de Produto: Rankings e Rentabilidade")

col7, col8 = st.columns(2)

if not df_sales_filtered.empty:
    # GRÁFICO 4: Ranking das 10 Pizzas Mais Vendidas (Volume)
    df_pizza_rank = df_sales_filtered.groupby('Nome da Pizza')['Quantidade do Pedido'].sum().reset_index()
    df_pizza_rank = df_pizza_rank.sort_values('Quantidade do Pedido', ascending=False).head(10)

    fig_rank_vol = px.bar(
        df_pizza_rank,
        x='Quantidade do Pedido',
        y='Nome da Pizza',
        orientation='h', 
        title='Top 10 Pizzas por Volume de Vendas',
        labels={'Quantidade do Pedido': 'Volume de Pizzas Vendidas', 'Nome da Pizza': ''},
        color_discrete_sequence=['#4CAF50'] 
    )
    fig_rank_vol.update_layout(yaxis={'categoryorder':'total ascending'})

    with col7:
        st.subheader("Top 10 Pizzas (Volume)")
        st.plotly_chart(fig_rank_vol, use_container_width=True)


    # GRÁFICO 5: Ranking das Categorias por Faturamento (Rentabilidade)
    df_categoria_rank = df_sales_filtered.groupby('Categoria Pizza')['Valor Total por Item'].sum().reset_index()
    df_categoria_rank = df_categoria_rank.sort_values('Valor Total por Item', ascending=False)

    fig_rank_fat = px.pie(
        df_categoria_rank,
        values='Valor Total por Item',
        names='Categoria Pizza',
        title='Faturamento por Categoria de Pizza',
        color_discrete_sequence=px.colors.sequential.Sunsetdark
    )
    fig_rank_fat.update_traces(textposition='inside', textinfo='percent+label')

    with col8:
        st.subheader("Faturamento por Categoria")
        st.plotly_chart(fig_rank_fat, use_container_width=True)
else:
    st.info("Os gráficos de Produto (Ranking e Categoria) estão vazios devido ao filtro selecionado.")


# --- 8. GRÁFICO 6: ANÁLISE DE TAMANHO (PRICING) ---
st.markdown("---")

st.header("📏 Insights de Pricing: Análise por Tamanho")

if not df_sales_filtered.empty:
    # Gráfico 6: Faturamento por Tamanho da Pizza
    df_tamanho = df_sales_filtered.groupby('Tamanho da Pizza')['Valor Total por Item'].sum().reset_index()

    # Ordenação para Tamanhos P, M, G, XL, XXL (se existirem)
    order_tamanho = ['S', 'M', 'L', 'XL', 'XXL']
    df_tamanho['Tamanho da Pizza'] = pd.Categorical(df_tamanho['Tamanho da Pizza'], categories=order_tamanho, ordered=True)
    df_tamanho = df_tamanho.sort_values('Tamanho da Pizza')

    fig_tamanho = px.bar(
        df_tamanho,
        x='Tamanho da Pizza',
        y='Valor Total por Item',
        title='Faturamento Total por Tamanho da Pizza',
        labels={'Tamanho da Pizza': 'Tamanho', 'Valor Total por Item': 'Faturamento (R$)'},
        color='Valor Total por Item',
        color_continuous_scale=px.colors.sequential.Teal
    )
    fig_tamanho.update_layout(yaxis_title=None)

    st.plotly_chart(fig_tamanho, use_container_width=True)
else:
    st.info("O gráfico de Análise por Tamanho está vazio devido ao filtro selecionado.")

st.markdown("---")
# FIM DO CÓDIGO