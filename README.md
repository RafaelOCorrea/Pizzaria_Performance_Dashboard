# Pizzaria_Performance_Dashboard
# 🍕 Dashboard de Performance de Vendas: Pizzaria Farinha Boa

**Link para o Dashboard Interativo (Streamlit Cloud):**

👉 [**[https://pizzariaperformancedashboard-f29pdqr5djcmyjpncq87et.streamlit.app/]**](https://pizzariaperformancedashboard-f29pdqr5djcmyjpncq87et.streamlit.app/) 👈

## 🎯 Visão Geral do Projeto

Este projeto demonstra o ciclo completo de Data Science/Analytics, desde a extração (simulada) e tratamento de dados até a entrega de uma ferramenta de Business Intelligence (BI) interativa. O objetivo é fornecer à gerência da pizzaria *Farinha Boa* insights acionáveis sobre padrões de vendas, otimização de horários e gestão de portfólio.

**Tecnologias de Frontend e Backend:**

| Área | Ferramenta / Linguagem |
| :--- | :--- |
| **Linguagem** | Python |
| **Manipulação de Dados** | Pandas |
| **Visualização** | Plotly Express (Gráficos Interativos) |
| **Web App / Deployment** | Streamlit (Desenvolvimento e Deploy em Nuvem) |
| **Controle de Versão** | Git / GitHub |

---

## 💡 Resultados e Recomendações Estratégicas (CRISP-DM: Avaliação)

A análise exploratória (EDA) dos dados de vendas revelou padrões críticos que embasam as seguintes recomendações:

### 1. Otimização de Turnos e Campanhas (Análise de Hora e Dia)

A gestão ineficiente de recursos pode ser resolvida focando em **cobrir os picos** e **estimular os vales**.

| Análise | Insight | Recomendação Estratégica |
| :--- | :--- | :--- |
| **Pico de Almoço (12h-14h) e Jantar (17h-19h)** | Picos representam **57% do volume total** (28.223 pizzas). A cozinha pode estar sobrecarregada, e o pós-jantar (após 20h) está subutilizado. | **Ajuste de Equipe (Staffing):** Concentrar o maior número de cozinheiros e entregadores nos picos. **Promoção de Vales:** Implementar cupons ou combos de "Happy Hour" (14h-17h) e "Super Tarde da Noite" (após 20h) para distribuir a receita. |
| **Picos Semanais** | A demanda se concentra em **Quinta, Sexta e Sábado** (quase 50% das vendas). Domingo e Segunda são os dias mais fracos. | **Marketing de Baixa Temporada:** Direcionar campanhas de marketing de fidelidade ou descontos agressivos especificamente para **Domingo e Segunda-feira**, buscando equilibrar o fluxo de caixa semanal. |

### 2. Gestão de Portfólio (Análise de Produto)

A distribuição de vendas indica oportunidades de monetização e corte de custos.

| Grupo de Pizzas | Volume de Vendas | Recomendação Estratégica |
| :--- | :--- | :--- |
| **Alta Venda (Top 12)** | 26.000 pizzas | **Estratégia de Preço/Rentabilidade:** Avaliar a margem de lucro. Por serem essenciais, um pequeno aumento de preço não afeta o volume, mas maximiza o faturamento total. |
| **Baixa Venda (Últimas 10)** | 9.000 pizzas | **Estratégia de Custo/Risco:** Colocar esses itens em promoção (para aumentar giro e reduzir insumos parados) ou **avaliar a remoção do cardápio**, pois ingredientes perecíveis de baixa rotatividade geram desperdício. |

---

## 🛠️ Detalhes Técnicos e Inovações

A aplicação foi desenvolvida com foco na Usabilidade (UX) e na robustez do código.

### Funcionalidades de UX (Experiência do Usuário)

* **Filtro Temporal Avançado:** Implementação do filtro `st.sidebar.date_input` em formato de calendário, permitindo aos gestores comparar períodos específicos de vendas (ex: Semana 1 vs. Semana 4).
* **Tema Escuro (