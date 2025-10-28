import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 3. LAYOUT GERAL (DEVE FICAR NO TOPO E FORA DE QUALQUER IF) ---
# st.set_page_config deve ser a primeira chamada Streamlit
st.set_page_config(layout="wide", page_title="Farinha Boa - Dash de Performance")


# --- 1. CARREGAMENTO E TRANSFORMAÇÃO DOS DADOS ---
@st.cache_data
def load_data():
    file_path = 'pizza_sales_data.csv'

    if not os.path.exists(file_path):
        st.error(f"Erro: Arquivo de dados '{file_path}' não encontrado.")
        return pd.DataFrame() 

    try:
        df_sales = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df_sales = pd.read_csv(file_path, encoding='latin1')
    
    df_sales.columns = [col.lower().replace('_', ' ') for col in df_sales.columns]
    
    if 'order datetime' in df_sales.columns:
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
    
    if 'Data Hora do Pedido' in df_sales.columns:
        df_sales['Numero do Mês'] = df_sales['Data Hora do Pedido'].dt.month
    return df_sales


df_sales = load_data()
if df_sales.empty:
    st.stop()


# --- 2. FUNÇÕES DE CÁLCULO DE KPIS ---
def calculate_kpis(df):
    faturamento_total = df['Valor Total por Item'].sum()
    volume_de_vendas = df['Quantidade do Pedido'].sum()
    quantidade_de_pedidos = df['ID pedido'].nunique()
    ticket_medio = faturamento_total / quantidade_de_pedidos if quantidade_de_pedidos > 0 else 0
    return faturamento_total, volume_de_vendas, quantidade_de_pedidos, ticket_medio


def format_brl(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_int(value):
    return f"{value:,.0f}".replace(",", ".")


# ======================================================================
# --- LÓGICA DE FILTRAGEM (MOVIDA PARA FORA DO IF/ELIF) ---
# O Streamlit precisa processar os filtros da sidebar antes de decidir qual página mostrar.

# --- 4. FILTROS ---
st.sidebar.header("Filtros de Análise")

# Datas
df_data_min = df_sales['Data Hora do Pedido'].min().date()
df_data_max = df_sales['Data Hora do Pedido'].max().date()

st.sidebar.subheader("Intervalo de Tempo")
data_inicio = st.sidebar.date_input("Data de Início", value=df_data_min, min_value=df_data_min, max_value=df_data_max)
data_fim = st.sidebar.date_input("Data de Fim", value=df_data_max, min_value=df_data_min, max_value=df_data_max)

if data_inicio > data_fim:
    st.sidebar.error("A Data de Início não pode ser maior que a Data de Fim.")
    data_fim = data_inicio

# Categoria
categorias_limpas = df_sales['Categoria Pizza'].fillna('Não Categorizado').unique()
categorias = ['Todas'] + list(categorias_limpas)
categoria_selecionada = st.sidebar.selectbox("Categoria de Pizza:", options=categorias)

# Dia da Semana (Manter o mapeamento se você precisar dele para o filtro de dados posterior)
dias_ingles = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dias_portugues = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
mapa_dias = dict(zip(dias_ingles, dias_portugues))

opcoes_dia_semana = ['Todos'] + dias_portugues
dia_semana_selecionado = st.sidebar.selectbox(
    "Dia da Semana:",
    options=opcoes_dia_semana,
    index=0 
)


# --- 5. FILTRAGEM DE DADOS ---
df_sales_filtrado = df_sales.copy()

# Data
df_sales_filtrado = df_sales_filtrado[
    (df_sales_filtrado['Data Hora do Pedido'].dt.date >= data_inicio) & 
    (df_sales_filtrado['Data Hora do Pedido'].dt.date <= data_fim)
]

# Categoria
if categoria_selecionada != 'Todas':
    df_sales_filtrado = df_sales_filtrado[df_sales_filtrado['Categoria Pizza'] == categoria_selecionada]

# Dia da Semana
if dia_semana_selecionado != 'Todos':
    dia_ingles = [k for k, v in mapa_dias.items() if v == dia_semana_selecionado][0]
    df_sales_filtrado = df_sales_filtrado[df_sales_filtrado['Dia da Semana'] == dia_ingles]

df_sales_filtered = df_sales_filtrado


# --- 6. KPIS (CALCULADO AQUI, FORA DO IF) ---
if df_sales_filtered.empty:
    st.warning("Nenhum dado encontrado para o filtro selecionado.")
    faturamento_total, volume_de_vendas, quantidade_de_pedidos, ticket_medio = 0, 0, 0, 0
else:
    faturamento_total, volume_de_vendas, quantidade_de_pedidos, ticket_medio = calculate_kpis(df_sales_filtered)


# ======================================================================
# --- NOVO BLOCO: NAVEGAÇÃO MULTIPÁGINA ---
st.sidebar.title("Navegação")
selecao = st.sidebar.selectbox(
    "Escolha a Seção:", 
    options=["📊 Painel Principal", "🧠 Recomendações Estratégicas"],
    index=0) # Define o Dashboard como padrão ao iniciar

# --- LÓGICA DE EXIBIÇÃO ---

if selecao == "📊 Painel Principal":
    
    st.title("🍕 Dashboard de Performance de Vendas - Pizzaria Farinha Boa")
    st.markdown("Monitoramento de Performance e Insights Estratégicos")
    
    
    # --- 6. KPIS (EXIBIÇÃO) ---
    col1, col2, col3, col4 = st.columns(4)
    # A variável 'faturamento_total' AGORA está definida e pode ser usada
    col1.metric("Faturamento Total", format_brl(faturamento_total))
    col2.metric("Volume de Vendas (Pizzas)", format_int(volume_de_vendas))
    col3.metric("Total de Pedidos", format_int(quantidade_de_pedidos))
    col4.metric("Ticket Médio por Pedido", format_brl(ticket_medio))
    st.markdown("---")


    # --- 7. GRÁFICO DE FATURAMENTO MENSAL ---
    # ... todo o código de gráficos (fig_mensal, fig_dia, fig_hora, fig_rank_vol, fig_rank_fat, fig_tamanho)
    # COPIAR A PARTIR DA LINHA 175 DO SEU CÓDIGO ANTERIOR E COLAR AQUI, MANTENDO A INDENTAÇÃO.

    if not df_sales_filtered.empty:
        MONTH_MAP = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
            7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        df_mensal = df_sales_filtered.groupby('Numero do Mês')['Valor Total por Item'].sum().reset_index()
        df_mensal['Nome do Mês PT'] = df_mensal['Numero do Mês'].map(MONTH_MAP)

        fig_mensal = px.line(df_mensal, x='Nome do Mês PT', y='Valor Total por Item', markers=True,
                             title='Evolução do Faturamento ao Longo do Ano',
                             labels={'Nome do Mês PT': 'Mês', 'Valor Total por Item': 'Faturamento (R$)'})
        fig_mensal.update_traces(line_color='#FF4B4B')
        fig_mensal.update_layout(xaxis_title=None, dragmode=False)
        fig_mensal.update_xaxes(fixedrange=True)
        fig_mensal.update_yaxes(fixedrange=True)
        st.plotly_chart(fig_mensal, use_container_width=True)
    st.markdown("---")


    # --- 8. DEMAIS GRÁFICOS (mantidos sem alterações de estilo) ---
    st.header("🎯 Análise de Performance: Dia da Semana e Hora")
    col5, col6 = st.columns(2)

    if not df_sales_filtered.empty:
        # Volume de Vendas por Dia da Semana
        df_dia = df_sales_filtered.groupby(['Dia da Semana'])['Quantidade do Pedido'].sum().reset_index()
        df_dia['Dia da Semana PT'] = df_dia['Dia da Semana'].map(mapa_dias)
        df_dia = df_dia.sort_values('Dia da Semana PT', key=lambda s: s.map({v: i for i, v in enumerate(dias_portugues)}))

        fig_dia = px.bar(df_dia, x='Dia da Semana PT', y='Quantidade do Pedido',
                         title='Volume de Vendas por Dia da Semana',
                         labels={'Dia da Semana PT': 'Dia da Semana', 'Quantidade do Pedido': 'Volume de Pizzas Vendidas'},
                         color='Quantidade do Pedido', color_continuous_scale=px.colors.sequential.Reds)
        fig_dia.update_layout(xaxis_title=None, dragmode=False)
        fig_dia.update_xaxes(fixedrange=True)
        fig_dia.update_yaxes(fixedrange=True)
        col5.plotly_chart(fig_dia, use_container_width=True)

        # Vendas por Hora
        df_hora = df_sales_filtered.groupby('Hora do Dia')['Quantidade do Pedido'].sum().reset_index()
        fig_hora = px.bar(df_hora, x='Hora do Dia', y='Quantidade do Pedido',
                          title='Distribuição de Vendas por Hora',
                          labels={'Hora do Dia': 'Hora', 'Quantidade do Pedido': 'Volume de Pizzas Vendidas'},
                          color_continuous_scale=px.colors.sequential.Reds)
        fig_hora.update_layout(xaxis_title='Hora do Dia', yaxis_title='Volume de Vendas', dragmode=False)
        fig_hora.update_xaxes(fixedrange=True)
        fig_hora.update_yaxes(fixedrange=True)
        col6.plotly_chart(fig_hora, use_container_width=True)

    st.markdown("---")


    # --- 9. RANKINGS E PRODUTOS ---
    st.header("🍕 Análise de Produto: Rankings e Rentabilidade")
    col7, col8 = st.columns(2)

    if not df_sales_filtered.empty:
        # Top 10 Pizzas
        df_pizza_rank = df_sales_filtered.groupby('Nome da Pizza')['Quantidade do Pedido'].sum().reset_index()
        df_pizza_rank = df_pizza_rank.sort_values('Quantidade do Pedido', ascending=False).head(10)

        fig_rank_vol = px.bar(df_pizza_rank, x='Quantidade do Pedido', y='Nome da Pizza',
                              orientation='h', title='Top 10 Pizzas por Volume de Vendas',
                              labels={'Quantidade do Pedido': 'Volume', 'Nome da Pizza': ''},
                              color_discrete_sequence=['#4CAF50'])
        fig_rank_vol.update_layout(yaxis={'categoryorder': 'total ascending'}, dragmode=False)
        fig_rank_vol.update_xaxes(fixedrange=True)
        fig_rank_vol.update_yaxes(fixedrange=True)
        col7.plotly_chart(fig_rank_vol, use_container_width=True)

        # Faturamento por Categoria
        df_categoria_rank = df_sales_filtered.groupby('Categoria Pizza')['Valor Total por Item'].sum().reset_index()
        df_categoria_rank = df_categoria_rank.sort_values('Valor Total por Item', ascending=False)

        fig_rank_fat = px.pie(df_categoria_rank, values='Valor Total por Item', names='Categoria Pizza',
                              title='Faturamento por Categoria de Pizza',
                              color_discrete_sequence=px.colors.sequential.Sunsetdark)
        fig_rank_fat.update_traces(textposition='inside', textinfo='percent+label')
        col8.plotly_chart(fig_rank_fat, use_container_width=True)

    st.markdown("---")


    # --- 10. INSIGHTS DE TAMANHO ---
    st.header("📏 Insights de Pricing: Análise por Tamanho")

    if not df_sales_filtered.empty:
        df_tamanho = df_sales_filtered.groupby('Tamanho da Pizza')['Valor Total por Item'].sum().reset_index()
        order_tamanho = ['S', 'M', 'L', 'XL', 'XXL']
        df_tamanho['Tamanho da Pizza'] = pd.Categorical(df_tamanho['Tamanho da Pizza'], categories=order_tamanho, ordered=True)
        df_tamanho = df_tamanho.sort_values('Tamanho da Pizza')

        fig_tamanho = px.bar(df_tamanho, x='Tamanho da Pizza', y='Valor Total por Item',
                              title='Faturamento Total por Tamanho da Pizza',
                              labels={'Tamanho da Pizza': 'Tamanho', 'Valor Total por Item': 'Faturamento (R$)'},
                              color='Valor Total por Item', color_continuous_scale=px.colors.sequential.Teal)
        fig_tamanho.update_layout(yaxis_title=None, dragmode=False)
        fig_tamanho.update_xaxes(fixedrange=True)
        fig_tamanho.update_yaxes(fixedrange=True)
        st.plotly_chart(fig_tamanho, use_container_width=True)

    st.markdown("---")
    
# ----------------------------------------------------------------------
# --- NOVA PÁGINA: RECOMENDAÇÕES ESTRATÉGICAS ---

elif selecao == "🧠 Recomendações Estratégicas":
    
    st.header("💡 Recomendações Estratégicas e Planos de Ação")
    st.markdown("### Visão RevOps: Transformando Dados em Lucro e Eficiência Operacional")
    
    # ----------------------------------------------------------------------
    # --- 1. Otimização de Turnos e Campanhas (Análise de Hora e Dia) ---
    st.markdown("---")
    st.subheader("1. Otimização de Turnos e Campanhas (Análise de Hora e Dia)")
    st.markdown("A gestão ineficiente de recursos pode ser resolvida focando em **cobrir os picos** e **estimular os vales**.")

    # Tabela 1: Picos de Atendimento
    st.markdown("#### Foco 1.1: Cobertura de Picos (12h-14h e 17h-19h)")
    col_analise_pico, col_acao_pico = st.columns(2)
    
    with col_analise_pico:
        st.info("**Análise e Entendimento:**")
        st.markdown(
            """
            * Os Picos de Almoço (12h-14h) e Jantar (17h-19h) representam **57% do volume total** (28.223 pizzas).
            * **Risco:** A cozinha pode estar sobrecarregada, afetando a qualidade e a satisfação do cliente.
            """
        )
    
    with col_acao_pico:
        st.warning("**Recomendação Estratégica:**")
        st.markdown(
            """
            * **Ajuste de Equipe:** Concentrar o maior número de cozinheiros e entregadores nos horários de pico.
            * **Promoção de Vales:** Implementar cupons ou combos de "Happy Hour" (14h-17h) e "Super Tarde da Noite" (após 20h) para distribuir a receita.
            """
        )

    # Tabela 2: Picos Semanais
    st.markdown("#### Foco 1.2: Equilíbrio Semanal")
    col_analise_semanal, col_acao_semanal = st.columns(2)

    with col_analise_semanal:
        st.info("**Análise e Entendimento:**")
        st.markdown(
            """
            * A demanda se concentra em **Quinta, Sexta e Sábado** (quase 50% das vendas).
            * **Risco:** Domingo e Segunda são os dias mais fracos, subutilizando a capacidade operacional.
            """
        )

    with col_acao_semanal:
        st.warning("**Recomendação Estratégica:**")
        st.markdown(
            """
            * **Marketing de Baixa Temporada:** Direcionar campanhas de fidelidade ou descontos específicos para **Domingo e Segunda-feira**, buscando equilibrar o fluxo de caixa semanalmente.
            """
        )
    
    st.markdown("---")


    # ----------------------------------------------------------------------
    # --- 2. Gestão de Portfólio (Análise de Produto) ---
    st.subheader("2. Gestão de Portfólio para Rentabilidade (RevOps)")
    st.markdown("A distribuição de vendas indica oportunidades claras de monetização e corte de custos de estoque (desperdício).")
    
    # Tabela 3: Alta Venda
    st.markdown("#### Foco 2.1: Alta Venda (Top 12) – Maximização de Margem")
    col_analise_alta, col_acao_alta = st.columns(2)

    with col_analise_alta:
        st.info("**Análise e Entendimento:**")
        st.markdown(f"**Volume:** 26.000 pizzas (Produtos que os clientes amam e procuram).")
        st.markdown("**Oportunidade:** Estes são os carros-chefe. Seus preços raramente afetam o volume, mas afetam MUITO a margem.")
    
    with col_acao_alta:
        st.warning("**Recomendação Estratégica:**")
        st.markdown(
            """
            * **Estratégia de Preço/Rentabilidade:** Avaliar a margem de lucro. Um pequeno aumento de preço (1% a 3%) não afetará o volume, mas **maximizará o faturamento total.**
            """
        )

    # Tabela 4: Baixa Venda
    st.markdown("#### Foco 2.2: Baixa Venda (Últimas 10) – Redução de Risco")
    col_analise_baixa, col_acao_baixa = st.columns(2)

    with col_analise_baixa:
        st.info("**Análise e Entendimento:**")
        st.markdown(f"**Volume:** 9.000 pizzas (Baixa rotatividade e alto custo de estoque).")
        st.markdown("**Risco:** Ingredientes perecíveis de baixa rotatividade geram desperdício e amarram capital de giro.")
    
    with col_acao_baixa:
        st.warning("**Recomendação Estratégica:**")
        st.markdown(
            """
            * **Estratégia de Custo/Risco:** Colocar esses itens em promoção (para aumentar o giro) ou **avaliar a remoção do cardápio**, liberando espaço e capital.
            """
        )

    st.markdown("---")
    
    # ----------------------------------------------------------------------
    # --- 3. PROVA DE CONCEITO FINAL ---
    st.subheader("3. Conclusão da Análise (Foco em RevOps)")
    
    st.success(
        f"🎯 **De Dados à Decisão Acionável:** Os insights apresentados demonstram como o diagnóstico preciso se traduz em um **Plano de Ação** para a Pizzaria Farinha Boa. "
        f"A metodologia de dados focada em **Receita e Eficiência Operacional (RevOps)** é a chave para: "
        f"1. **Maximizar a Margem** nos produtos de alta venda. "
        f"2. **Reduzir o Risco** e o desperdício nos itens de baixa rotatividade. "
        f"3. **Otimizar a Alocação** de recursos humanos nos picos de demanda."
    )