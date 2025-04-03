# streamlit run c:/Users/Alunos/Downloads/dash/teste3.py

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import pickle
import requests
import io

# Configuração de página para usar todo o espaço disponível
st.set_page_config(layout="wide")

# Carregando os DataFrames
df_raw = pd.read_csv('https://github.com/LOUMERIM/Dashboard-DSS/raw/refs/heads/main/df_raw.csv')
df_processed = pd.read_csv('https://github.com/LOUMERIM/Dashboard-DSS/raw/refs/heads/main/DB-SaudeMental-Tech_processed.csv')
df_mapa = pd.read_csv('https://github.com/LOUMERIM/Dashboard-DSS/raw/refs/heads/main/Geodados/df_raw_mapa.csv')
df_raw_pt = pd.read_csv('https://github.com/LOUMERIM/Dashboard-DSS/raw/refs/heads/main/df_raw_traduzido.csv')

# Personalização de formatação, barra lateral e dos botões
st.markdown(
    """
    <style>
        /* Cor de fundo do dashboard */
        .stApp {
            background-color: #082338;  /* Cor de fundo do dashboard: azul escuro */
        }

        /* Removendo padding e espaçamentos padrão */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        /* Expande os gráficos para usar todo o espaço disponível*/
        /*.stChart, .stDataFrame { */
        /*    width: 100% !important; */
        /* } */

        /* Estilos para os gráficos Plotly */
        [data-testid="stPlotlyChart"] {
            border-radius: 15px;
            overflow: hidden;
        }

        /* Personalização da barra lateral */
        section[data-testid="stSidebar"] {
            background-color: #0e1117; /* Cor de fundo da aba lateral: preto */
            width: 260px !important;   /* Alterar de acordo com a largura desejada */
        }

        /* Personalização dos botões */
        div.stButton > button {
            width: 100%;
            height: 60px;
            background-color: #4CAF50; /* Cor de fundo do botão: verde */
            border-radius: 12px;       /* Bordas arredondadas */
            border: none;              /* Remove a borda ao passar o mouse*/
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); /* Sombra */
        }
        div.stButton > button:hover {
            background-color: #45a049; /* Cor de fundo ao passar o mouse: verde escuro*/
        }
        div.stButton > button > div > p {
            font-size: 20px;    /* Tamanho da fonte do texto */
            color: white;       /* Cor do texto */
            font-weight: bold;  /* Texto em negrito */
        }

        /* Estilo para os gráficos Plotly */
        [data-testid="stPlotlyChart"] {
            border-radius: 15px; /* Bordas arredondadas */
            overflow: hidden;    /* Esconde o conteúdo que ultrapassa os limites do gráfico */
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar com título
with st.sidebar:
    st.sidebar.markdown("<h1 style='font-size:24px;"
                               "font-weight: bold;"
                               "text-align: center;"
                               "color: white;'"
                    ">Selecione a Página</h1>", unsafe_allow_html=True)

    # Botões para mudar de página
    if st.button('📊 Análise Descritiva', use_container_width=True):
        st.session_state.pagina = 'Página 1'
    if st.button('💡 Insights', use_container_width=True):
        st.session_state.pagina = 'Página 2'
    if st.button('📝 Questionário', use_container_width=True):
        st.session_state.pagina = 'Página 3'

# Inicializa estado da página
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'Página 1'

# Conteúdo principal expansível
st.markdown("<h1 style='font-size: 44px;'>Impactos do Trabalho Excessivo na Saúde de Empregados em TI</h1>", unsafe_allow_html=True)
    
if st.session_state.pagina == 'Página 1': ##############################################################
    st.subheader("Análise Descritiva do Dataset")

    # Calcular o distúrbio mais comum
    coluna_disturbios = "Em caso afirmativo, com qual(is) condição(ões) você foi diagnosticado?"
    disturbio_mais_comum = df_raw[coluna_disturbios].value_counts().idxmax()

    # Calcular o total de perguntas (colunas no dataset)
    total_perguntas = df_raw.shape[1]

    # Calcular o total de respondentes (linhas no dataset)
    total_respondentes = df_raw.shape[0]

    # Calcular a quantidade de distúrbios mentais únicos
    quantidade_disturbios = df_raw[coluna_disturbios].nunique()

    with st.container():
        st.markdown("### 📊 Resumo Descritivo")
        
        # Primeira linha com 3 colunas
        col1, col2, col3 = st.columns(3)
        col1.metric(label="🔹 Total de dados", value=total_respondentes)
        col2.metric(label="🔹 Total de perguntas", value=total_perguntas)
        col3.metric(label="🔹 Quantidade de distúrbios mentais", value=quantidade_disturbios)
        
        # Segunda linha com 1 coluna ocupando todo o espaço
        col4 = st.container()
        with col4:
            st.metric(label="🔹 Distúrbio mais comum", value=disturbio_mais_comum)


        # Divisão de espaço para gráficos adicionais
        col1, col2 = st.columns(2, gap='small')
        
        with col1:
            df_graf_2 = df_processed[['Back-end Developer', 'Front-end Developer', 'Supervisor/Team Lead', 'Executive Leadership',
                                    'Dev Evangelist/Advocate', 'DevOps/SysAdmin', 'Support', 'Designer', 'One-person shop', 'Sales', 'HR']]
            
            df_graf_2 = df_graf_2.sum().reset_index()
            df_graf_2.columns = ['Cargo', 'Quantidade']

            # Dicionário com os nomes antigos e os novos nomes desejados
            rename_dict = {'Back-end Developer': 'Back-end',
                        'Front-end Developer': 'Front-end',
                        'Supervisor/Team Lead': 'Líder de Equipe',
                        'Executive Leadership': 'Liderança Executiva',
                        'Dev Evangelist/Advocate': 'Advogado Dev',
                        'DevOps/SysAdmin': 'DevOps',
                        'Support': 'Suporte',
                        'Designer': 'Designer',
                        'One-person shop': 'Autônomo',
                        'Sales': 'Vendas',
                            'HR': 'Recursos Humanos'}

            df_graf_2['Cargo'] = df_graf_2['Cargo'].replace(rename_dict)

            # Criar o gráfico de barras
            fig2 = px.bar(df_graf_2, x='Cargo', y='Quantidade',
                        labels={'Cargo': 'Cargo', 'Quantidade': 'Quantidade'},
                        color_discrete_sequence=['#4CAF50'])

            fig2.update_layout(
                    title={
                        'text': 'Distribuição de Cargos',
                        'font': {'size': 24, 'color': 'white'},
                        'x': 0.03,  # Pequena margem da esquerda
                        'xanchor': 'left'
                    },

                    paper_bgcolor='#0d2e4d',  # Cor de fundo ao redor do gráfico
                    plot_bgcolor='rgba(0,0,0,0)',  # Fundo transparente
                    font=dict(color='white'),      # Texto em branco para contraste
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                    margin=dict(l=50, r=50, t=80, b=50),  # Ajuste equilibrado das margens

                    width=900, # Largura do gráfico

                    hoverlabel=dict(font_size=16)

            )

            fig2.update_traces(
                hovertemplate=(
                    "<b>%{label}</b><br>"  # Nome do cargo em negrito
                    "Quantidade: %{customdata}"  # Valor específico
                ),
                customdata=df_graf_2['Quantidade']  # Dados para exibir
            )

            # Exibir o gráfico
            st.plotly_chart(fig2, use_container_width=False)



        with col2:
            df_graf_1 = df_raw["Qual é o seu gênero?"].value_counts().reset_index()
            df_graf_1.columns = ["Gênero", "Quantidade"]
            
            # Criar um gráfico de pizza
            fig1 = px.pie(df_graf_1, values='Quantidade', names='Gênero',
                        color_discrete_sequence=['#4CAF50', '#c44d4d', '#2196F3']) # Cores personalizadas

            fig1.update_layout(
                    title={
                        'text': 'Distribuição de Gênero',
                        'font': {'size': 24, 'color': 'white'},
                        'x': 0.03,  # Pequena margem da esquerda
                        'xanchor': 'left'
                    },

                    paper_bgcolor='#0d2e4d',  # Cor de fundo ao redor do gráfico
                    plot_bgcolor='rgba(0,0,0,0)',  # Fundo transparente
                    font=dict(color='white'),      # Texto em branco para contraste
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                    margin=dict(l=50, r=50, t=80, b=10),  # Ajuste equilibrado das margens

                    width=500, # Largura do gráfico
                    legend_title='Gêneros', # Título da legenda

                    hoverlabel=dict(font_color='white', font_size=16)
                )

            fig1.update_traces(
                textfont=dict(size=16, family='Arial, bold', color='white'),  # Ajusta o tamanho e cor do texto
                textposition='inside',  # Mantém os números dentro das fatias
                texttemplate='%{percent:.0%}',  # Formata para arredondar
                hovertemplate="<b>%{label}</b><br>Quantidade: %{value}"  # Texto ao dar hover
                )
            
            # Exibir o gráfico
            st.plotly_chart(fig1, use_container_width=False)

        # Adicionar o mapa ao dashboard
        with st.container():
            st.markdown("### 🌍 Distribuição Geográfica dos Dados")
            
            # Criando um DataFrame com países e valores
            df_graf_3 = df_mapa['What country do you work in?'].value_counts().reset_index()
            df_graf_3.columns = ['País', 'Quantidade']
            df_graf_3 = df_graf_3[df_graf_3['Quantidade'] >= 9]

            # Definir os pontos de quebra e criar escala de cores personalizada
            thresholds = [9, 14, 20, 30, 45, 55, 70, 180, 850]
            cores = [
                '#e0f2e9',   # Verde água claro
                '#c8e4d5',   # Verde pastel
                '#a3d9c2',   # Verde menta suave
                '#7accaf',   # Verde médio-claro
                '#4fb89b',   # Verde jade
                '#2a9d8f',   # Verde tropical
                '#1a7f6e',   # Verde floresta claro
                '#0d5b4c',   # Verde petróleo
                '#083c32'    # Verde floresta escuro
            ]

            # Calcular posições normalizadas (0 a 1) baseadas nos thresholds
            min_val = df_graf_3['Quantidade'].min()
            max_val = df_graf_3['Quantidade'].max()
            posicoes = [(t - min_val) / (max_val - min_val) for t in thresholds]

            # Construir a escala de cores personalizada
            escala_personalizada = []
            for i in range(len(thresholds)):
                escala_personalizada.append([posicoes[i], cores[i]])

            # Adicionar o último segmento até o valor máximo
            escala_personalizada.append([1.0, cores[-1]])

            # Criando o gráfico de mapa-múndi
            fig3 = px.choropleth(
                df_graf_3,
                locations="País",
                locationmode="country names",  # Indica que estamos usando nomes de países
                color="Quantidade",
                color_continuous_scale=escala_personalizada,
                range_color=[min_val, max_val],  # Força a escala de 9 a 851
            )

            # Aplicar customizações de layout
            fig3.update_layout(
            title={
                    'text': 'Dados Coletados por País',
                    'font': {'size': 24, 'color': 'white'},
                    'x': 0.5,  # Centraliza o título horizontalmente
                    'y': 0.95,  # Ajusta a posição vertical do título para cima
                    'xanchor': 'center',  # Alinha o título ao centro
                    'yanchor': 'top'  # Alinha o título ao topo
            },

            paper_bgcolor='#0d2e4d',       # Fundo escuro ao redor do mapa ###################################################
            font=dict(color='white'),      # Texto branco
            margin=dict(l=55, r=50, t=50, b=0), ###############################################################################
            height=600, ##################################################
            width=800, ####################################################
            coloraxis_showscale=False,  # Remove a barra de cores

            hoverlabel=dict(bgcolor='white',
                            font_size=15)
            )

            fig3.update_traces(
                hovertemplate=(
                    "<b>%{location}</b><br>"  # Nome do país em negrito
                    "Quantidade = %{customdata}"  # Valor específico
                ),
                customdata=df_graf_3['Quantidade']  # Dados extras para exibir
            )

            # Ajustar a projeção e limites para esconder a Antártica
            fig3.update_geos(

                projection=dict(rotation=dict(lon=1, lat=1, roll=0.1)),

                lataxis_range=[-58, 86],  # Limita a latitude entre -55° e 90°
                visible=False,  # Remove linhas de grade e fundo
                showcountries=False,  # Removem as fronteiras dos países
                showocean=True,  # Adiciona cor ao oceano para melhor contraste
                oceancolor='lightblue'
            )

            # Exibir o gráfico
            st.plotly_chart(fig3, use_container_width=True)
if st.session_state.pagina == 'Página 2': ##############################################################
    st.subheader("Análise Estatística do Dataset")

        # Percentual de trabalhadores com problemas de saúde mental
    mental_health_issues = df_processed["Você atualmente tem um distúrbio de saúde mental?"].value_counts(normalize=True) * 100
    mental_health_issues.index = mental_health_issues.index.map({2: 'Sim', 1: 'Não sabe', -1: 'Não'})
    fig1 = px.pie(values=mental_health_issues, names=mental_health_issues.index, title='Percentual de trabalhadores com problemas de saúde mental')

        # Contar o número total de respostas à pergunta
    total_respostas = df_processed['Você acha que discutir um transtorno de saúde mental com seu empregador teria consequências negativas?'].count()

    # Contar as respostas:
    # 2 => indica que há consequências negativas
    # -1 => indica que não há consequências
    respostas_negativas = df_processed[
        df_processed['Você acha que discutir um transtorno de saúde mental com seu empregador teria consequências negativas?'] == 2
    ].shape[0]
    respostas_positivas = df_processed[
        df_processed['Você acha que discutir um transtorno de saúde mental com seu empregador teria consequências negativas?'] == -1
    ].shape[0]

    # Percentuais
    percentual_negativo = (respostas_negativas / total_respostas) * 100
    percentual_positivo = (respostas_positivas / total_respostas) * 100
    percentual_total = total_respostas*100

    # Filtramos os respondentes que indicaram consequências negativas:
    df_neg = df_processed[
        df_processed['Você acha que discutir um transtorno de saúde mental com seu empregador teria consequências negativas?'] == 2]
    df_sem= df_processed[
        df_processed['Você acha que discutir um transtorno de saúde mental com seu empregador teria consequências negativas?'] == -1]
    # Contar quantos, dentre os que têm consequências negativas, possuem problemas mentais
    count_com_problemas = df_neg[df_neg['Você atualmente tem um distúrbio de saúde mental?'] == 2].shape[0]
    count_sem_problemas = df_neg[df_neg['Você atualmente tem um distúrbio de saúde mental?'] != 2].shape[0]

    count_com_problemas_sem = df_sem[df_sem['Você atualmente tem um distúrbio de saúde mental?'] == -1].shape[0]
    count_sem_problemas_sem = df_sem[df_sem['Você atualmente tem um distúrbio de saúde mental?'] != -1].shape[0]

    # Calcula os totais para cada categoria
    total_consequencias_negativas = count_com_problemas + count_sem_problemas
    total_sem_consequencias = count_com_problemas_sem + count_sem_problemas_sem

    # Calcula os percentuais para cada barra em relação ao total de cada categoria
    # Calcula os totais gerais
    total_respostas = df_processed.shape[0]

    # Calcula os percentuais em relação ao total geral
    percent_com_problemas_neg = (count_com_problemas / total_respostas) * 100 if total_respostas > 0 else 0
    percent_sem_problemas_neg = (count_sem_problemas / total_respostas) * 100 if total_respostas > 0 else 0

    percent_com_problemas_sem = (count_com_problemas_sem / total_respostas) * 100 if total_respostas > 0 else 0
    percent_sem_problemas_sem = (count_sem_problemas_sem / total_respostas) * 100 if total_respostas > 0 else 0

    # --- Passo 3: Criar gráfico de barras empilhadas com Plotly ---

    # Atualiza o gráfico para usar percentuais e exibir valores aproximados
    fig2 = go.Figure()

    # Adiciona barra empilhada para "Consequências Negativas"
    fig2.add_trace(
        go.Bar(
            name='Com Problemas Mentais',
            x=['Consequências Negativas'],
            y=[percent_com_problemas_neg],
            marker_color='indianred',
            text=[round(percent_com_problemas_neg)],  # Adiciona o valor arredondado
            texttemplate='%{text}%',  # Formato do texto
            textposition='auto'  # Exibe o texto diretamente na barra
        )
    )
    fig2.add_trace(
        go.Bar(
            name='Sem Problemas Mentais',
            x=['Consequências Negativas'],
            y=[percent_sem_problemas_neg],
            marker_color='lightsalmon',
            text=[round(percent_sem_problemas_neg)],  # Adiciona o valor arredondado
            texttemplate='%{text}%',  # Formato do texto
            textposition='auto'  # Exibe o texto diretamente na barra
        )
    )

    # Adiciona barra para "Sem consequências"
    fig2.add_trace(
        go.Bar(
            name='Com Problemas Mentais',
            x=['Sem Consequências'],
            y=[percent_com_problemas_sem],
            marker_color='green',
            text=[round(percent_com_problemas_sem)],  # Adiciona o valor arredondado
            texttemplate='%{text}%',  # Formato do texto
            textposition='auto'  # Exibe o texto diretamente na barra
        )
    )
    fig2.add_trace(
        go.Bar(
            name='Sem Problemas Mentais',
            x=['Sem Consequências'],
            y=[percent_sem_problemas_sem],
            marker_color='limegreen',
            text=[round(percent_sem_problemas_sem)],  # Adiciona o valor arredondado
            texttemplate='%{text}%',  # Formato do texto
            textposition='auto'  # Exibe o texto diretamente na barra
        )
    )

    # Configura o layout do gráfico
    fig2.update_layout(
        barmode='stack',
        title='Percentual que discute problemas mentais com o empregador acarretando consequências negativas.',
        xaxis_title='Categoria',
        yaxis_title='Percentual de Respondentes (%)',
        legend_title='Detalhamento',
        yaxis=dict(tickmode='linear', tick0=0, dtick=10, range=[0, 50])  # Garante que o eixo Y vá de 0 a 100
    )

    # Exibir os gráficos lado a lado
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

        # Nome da coluna que contém a resposta à pergunta
    coluna_saude_mental = "Você conhece as opções de saúde mental disponíveis sob a cobertura de saúde do seu empregador?"

    # Garantir que a coluna existe no dataset
    if coluna_saude_mental in df_raw.columns:
        df_raw['conhecimento_saude_mental'] = df_raw[coluna_saude_mental].map({'Sim': 2, 'Não': -1})

    # Criar um agrupamento por empresa, setor ou outra variável relevante
    df_agrupado = df_raw.groupby("Quantos funcionários sua empresa ou organização tem?")['conhecimento_saude_mental'].mean().reset_index()
    df_agrupado.rename(columns={'conhecimento_saude_mental': 'percentual_conhecimento'}, inplace=True)

    # Multiplicar por 100 para converter em porcentagem
    df_agrupado['percentual_conhecimento'] *= 100

    # --- Exibir no Streamlit ---
    st.title("Dashboard: Conhecimento das Opções de Saúde Mental")

    # Criar o gráfico de barras laterais
    st.plotly_chart(px.bar(df_agrupado, 
                        x='percentual_conhecimento', 
                        y='Quantos funcionários sua empresa ou organização tem?', 
                        orientation='h',
                        labels={'Quantos funcionários sua empresa ou organização tem?': 'Tamanho da Empresa', 
                                'percentual_conhecimento': 'Percentual de Conhecimento (%)'},
                        title='Distribuição do Percentual de Funcionários que Conhecem as Opções de Saúde Mental por Tamanho da Empresa'),
                    use_container_width=True)
    
    # Criar o dataset com base nos dados principais
    coluna_cargo = "Qual das opções a seguir melhor descreve sua posição de trabalho?"
    coluna_disturbio = "Em caso afirmativo, com qual(is) condição(ões) você foi diagnosticado?"
    coluna_tamanho_empresa = "Quantos funcionários sua empresa ou organização tem?"

    # Filtrar apenas os respondentes que possuem alguma doença mental
    df_mental_health = df_raw[df_raw[coluna_disturbio].notna()]

    # Dividir os cargos que estão separados por "/" ou "|"
    df_mental_health = df_mental_health.assign(
        Cargos_Separados=df_mental_health[coluna_cargo].str.split(r'[\/|]')
    ).explode('Cargos_Separados')

    # Remover espaços extras nos cargos
    df_mental_health['Cargos_Separados'] = df_mental_health['Cargos_Separados'].str.strip()

    # Agrupar por cargo
    df_cargos = df_mental_health.groupby('Cargos_Separados').agg(
        Quantidade_Com_Doenca_Mental=(coluna_disturbio, 'count'),  # Contar respondentes com doença mental
        Doenca_Mais_Comum=(coluna_disturbio, lambda x: x.value_counts().idxmax() if not x.empty else "Desconhecido"),  # Doença mais comum
        Tamanho_Empresa=(coluna_tamanho_empresa, lambda x: x.mode()[0] if not x.mode().empty else "Desconhecido")  # Tamanho mais comum
    ).reset_index()

    # Renomear as colunas para exibição
    df_cargos.rename(columns={
        'Cargos_Separados': "Tipo de Cargo",
        "Quantidade_Com_Doenca_Mental": "Quantidade com Doença Mental",
        "Doenca_Mais_Comum": "Doença Mental Mais Comum",
        "Tamanho_Empresa": "Tamanho da Empresa"
    }, inplace=True)

    # Exibir o dataset no Streamlit
    st.write("### Dataset de Cargos e Saúde Mental")
    st.dataframe(df_cargos)

if st.session_state.pagina == 'Página 3': ##############################################################
    st.title('Questionário de Saúde Mental')
    st.write('exemplo de texto')

    # Separando todas as valores 
    verificar_unicos = ['Você já teve um distúrbio de saúde mental no passado?',
                        'Você já procurou tratamento para um problema de saúde mental de um profissional de saúde mental?',
                        'Você foi diagnosticado com uma condição de saúde mental por um profissional médico?',
                        'Você tem histórico familiar de doença mental?',
                        'Se você tem um problema de saúde mental, sente que isso interfere no seu trabalho ao ser tratado de forma eficaz?',
                        'Você acha que discutir um distúrbio de saúde mental com empregadores anteriores teria consequências negativas?',
                        'Você conhece as opções de saúde mental disponíveis sob a cobertura de saúde do seu empregador?',
                        'Você observou ou experimentou uma resposta sem apoio ou mal tratada a um problema de saúde mental em seu local de trabalho atual ou anterior?',
                        'Você ouviu falar ou observou consequências negativas para colegas de trabalho com problemas de saúde mental em seus locais de trabalho anteriores?',
                        'Suas observações de como outro indivíduo que discutiu um transtorno de saúde mental o tornaram menos propenso a revelar um problema de saúde mental em seu local de trabalho atual?',
                        'Você levantaria um problema de saúde mental com um empregador em potencial em uma entrevista?',
                        'Você sentiu que seus empregadores anteriores levavam a saúde mental tão a sério quanto a saúde física?',
                        'Seus empregadores anteriores forneceram benefícios de saúde mental?',
                        'Você conhecia as opções de cuidados de saúde mental fornecidas por seus empregadores anteriores?',
                        'Você estaria disposto a discutir um problema de saúde mental com seu(s) supervisor(es) direto(s)?',
                        'Quão disposto você estaria a compartilhar com amigos e familiares que tem uma doença mental?',
                        'Você já ouviu falar ou observou consequências negativas para colegas de trabalho que foram abertos sobre problemas de saúde mental em seu local de trabalho?',
                        'Você acha que os membros da equipe/colegas de trabalho o veriam de forma mais negativa se soubessem que você sofre de um problema de saúde mental?',
                        'Se um problema de saúde mental o levou a solicitar uma licença médica do trabalho, pedir essa licença seria:']

    perguntas_alternativas = {}
    for col in verificar_unicos:
        perguntas_alternativas[col] = df_raw[col].unique().tolist()

    # Mapeamento para parafrasear as perguntas e alternativas do formulário
    parafrasear_questoes = {
        # QUESTÃO 1
        'Você já teve um distúrbio de saúde mental no passado?': {
            'pergunta': 'Você já experimentou algum distúrbio de saúde mental anteriormente?',
            'alternativas': {
                'Talvez': 'Talvez, eu não me lembro'
            }
        },
        # QUESTÃO 2
        'Você já procurou tratamento para um problema de saúde mental de um profissional de saúde mental?': {
            'pergunta': 'Você já buscou ajuda profissional para tratar algum problema de saúde mental?',
            'alternativas': {
                1: 'Sim',
                0: 'Não',
            }
        },
        # QUESTÃO 3
        'Você foi diagnosticado com uma condição de saúde mental por um profissional médico?': {
            'pergunta': 'Você já foi diagnosticado por um médico profissional com alguma condição de saúde mental?'
        },
        # QUESTÃO 4
        'Você tem histórico familiar de doença mental?': {
            'pergunta': 'Há casos de doenças mentais na sua família?'
        },
        # QUESTÃO 5
        'Se você tem um problema de saúde mental, sente que isso interfere no seu trabalho ao ser tratado de forma eficaz?': {
            'pergunta': 'Se você tiver um problema de saúde mental, com que frequência o tratamento adequado iria interferir no seu desempenho no trabalho?',
            'alternativas': {
                'Não se aplica a mim': 'Não tenho problemas de saúde mental'
            }
        },
        # QUESTÃO 6
        'Você acha que discutir um distúrbio de saúde mental com empregadores anteriores teria consequências negativas?': {
            'pergunta': 'Em relação a todos os seus empregadores até o momento, quantos deles você acha que ao discutir sobre um distúrbio de saúde mental poderia trazer consequências negativas?',
            'alternativas': {
                'Sim, todos eles': 'Todos eles'
            }
        },
        # QUESTÃO 7
        'Você conhece as opções de saúde mental disponíveis sob a cobertura de saúde do seu empregador?': {
            'pergunta': 'Você sabe quais são as opções de tratamento para saúde mental oferecidas pelo plano de saúde do seu empregador?',
            'alternativas': {
                'Não sabe': 'Esse tipo de benefício não é oferecido pelo meu empregador'
            }
        },
        # QUESTÃO 8
        'Você observou ou experimentou uma resposta sem apoio ou mal tratada a um problema de saúde mental em seu local de trabalho atual ou anterior?': {
            'pergunta': 'Você já percebeu ou viveu uma situação em que problemas de saúde mental foram ignorados ou tratados de forma inadequada no seu trabalho atual ou anterior?'
        },
        # QUESTÃO 9
        'Você ouviu falar ou observou consequências negativas para colegas de trabalho com problemas de saúde mental em seus locais de trabalho anteriores?': {
            'pergunta': 'Você soube de casos ou presenciou consequências negativas para colegas de trabalho com problemas de saúde mental em empregos anteriores ou atual?',
            'alternativas': {
                'Alguns deles': 'Somente em alguns empregos',
                'Sim, todos eles': 'Sim, em todos os empregos',
                'Nenhum deles': 'Não, em nenhum'
            }
        },
        # QUESTÃO 10
        'Suas observações de como outro indivíduo que discutiu um transtorno de saúde mental o tornaram menos propenso a revelar um problema de saúde mental em seu local de trabalho atual?': {
            'pergunta': 'As atitudes de colegas de trabalho que discutiram problemas de saúde mental fizeram com que você ficasse menos disposto a compartilhar um problema semelhante no seu local de trabalho atual?'
        },
        # QUESTÃO 11
        'Você levantaria um problema de saúde mental com um empregador em potencial em uma entrevista?': {
            'pergunta': 'Você consideraria abordar um problema de saúde mental durante uma entrevista de emprego?'
        },
        # QUESTÃO 12
        'Você sentiu que seus empregadores anteriores levavam a saúde mental tão a sério quanto a saúde física?': {
            'pergunta': 'Você sentiu que os empregadores anteriores/atual tratavam questões de saúde mental com a mesma seriedade que questões de saúde física?',
            'alternativas': {
                'Alguns fizeram': 'Alguns somente',
                'Sim, todos eles fizeram': 'Sim, todos eles',
                'Nenhum fez': 'Não, nenhum deles' 
            }
        },
        # QUESTÃO 13
        'Seus empregadores anteriores forneceram benefícios de saúde mental?': {
            'pergunta': 'Seus empregadores anteriores ofereciam benefícios relacionados à saúde mental?'
        },
        # QUESTÃO 14
        'Você conhecia as opções de cuidados de saúde mental fornecidas por seus empregadores anteriores?': {
            'pergunta': 'Levando em consideração os empregos passados que você já teve, você conhecia as opções de cuidados com a saúde mental que seus empregadores ofereciam?',
            'alternativas': {
                'Eu estava ciente de alguns': 'Conheço somente algumas',
                'Sim, eu estava ciente de todos eles': 'Sim, conheço a maioria/todas as opções',
                'Não estou ciente no momento': 'Não sei quais são até hoje',
            }
        },
        # QUESTÃO 15
        'Você estaria disposto a discutir um problema de saúde mental com seu(s) supervisor(es) direto(s)?': {
            'pergunta': 'Você se sentiria confortável em falar sobre um problema de saúde mental com seu(s) supervisor(es)?',
            'alternativas': {
                'Não sabe': 'Não tenho certeza',
                'Alguns dos meus empregadores anteriores': 'Somente com alguns',
                'Sim, em todos os meus empregadores anteriores': 'Sim, com a maioria pelo menos',
                'Não, em nenhum dos meus empregadores anteriores': 'Não, com nenhum deles'
            }  
        },
        # QUESTÃO 16
        'Quão disposto você estaria a compartilhar com amigos e familiares que tem uma doença mental?': {
            'pergunta': 'Quão disposto você se estaria para contar aos seus amigos e familiares sobre um problema de saúde mental?'
        },
        # QUESTÃO 17
        'Você já ouviu falar ou observou consequências negativas para colegas de trabalho que foram abertos sobre problemas de saúde mental em seu local de trabalho?': {
            'pergunta': 'Você já ouviu falar de colegas de trabalho que enfrentaram consequências negativas por serem abertos sobre problemas de saúde mental no local de trabalho?',
            'alternativas': {
                'Não sabe': 'Meus colegas de trabalho não possuem problemas de saúde mental'
            }
        },
        # QUESTÃO 18
        'Você acha que os membros da equipe/colegas de trabalho o veriam de forma mais negativa se soubessem que você sofre de um problema de saúde mental?': {
            'pergunta': 'Você acredita que seus colegas de trabalho veriam você de forma mais negativa se soubessem que você tem um problema de saúde mental?',
            'alternativas': {
                'Talvez': 'Talvez, eu não tenho certeza quem os meus colegas são',
                'Sim, eu acho que eles fariam': 'Sim, eu acredito que eles fariam isso comigo',
                'Não, eu não acho que eles fariam': 'Não, eu não acho que iriam fazer isso comigo',
                'Sim, eles fazem': 'Sim, eu já vi isso acontecer',
                'Não, eles não fazem': 'Conheço os meus colegas o suficiente para saber que isso não irá ocorrer'
            }
        },
        # QUESTÃO 19
        'Se um problema de saúde mental o levou a solicitar uma licença médica do trabalho, pedir essa licença seria:': {
            'pergunta': 'Se você precisasse pedir uma licença médica devido a um problema de saúde mental, como seria esse processo?',
            'alternativas': {
                'Very easy': 'Muito fácil',
                'Somewhat easy': 'Um pouco fácil',
                'Neither easy nor difficult': 'Nem fácil nem difícil',
                'Somewhat difficult': 'Um pouco difícil',
                'Very difficult': 'Muito difícil'
            }
        }
    }

    def parafrasear_questao(pergunta, alters, dic):
        """
        Substitui strings de acordo com o dicionário inserido, se aplicável.

        Args:
            pergunta (str): pergunta original.
            alters (list): lista de alternativas originais.
            dic (dict): dicionário contendo as parafrases das perguntas e alternativas.

        Returns:
            Uma tupla contendo a pergunta parafraseada (ou original) e as alternativas parafraseadas (ou originais).
        """
        
        if pergunta in dic:
            # Armazenando a pergunta original
            pergunta_original = pergunta
            # Parafraseamento das perguntas 
            pergunta = dic[pergunta_original]['pergunta']
            # Parafraseamento das alternativas 
            if 'alternativas' in dic[pergunta_original]:
                alters = [dic[pergunta_original]['alternativas'].get(alternativa, alternativa)
                        for alternativa in alters]
        return pergunta, alters
        

    # Questionário de múltiplas alternativas usando st.selectbox()
    st.write('### Questionário de Saúde Mental')

    # Dicionário para armazenar as respostas do formulário
    dict_respostas_form = {}

    # Loop para exibir as perguntas e alternativas
    for pergunta, alternativas in perguntas_alternativas.items():
        pergunta_parafraseada, alternativas_parafraseadas = parafrasear_questao(pergunta, alternativas, parafrasear_questoes)
        resposta = st.selectbox(pergunta_parafraseada, alternativas_parafraseadas)
        # Revertendo a resposta para o valor original, se aplicável
        if pergunta in parafrasear_questoes and 'alternativas' in parafrasear_questoes[pergunta]:
            alternativa_revertida = {v: k for k, v in parafrasear_questoes[pergunta]['alternativas'].items()}
            resposta = alternativa_revertida.get(resposta, resposta)
        dict_respostas_form[pergunta] = resposta

    # Convertendo o dicionário com as respostas em um DataFrame
    df_form_respondido = pd.DataFrame([dict_respostas_form])

    # Definindo valores numéricos para respostas comuns no formulário
    dict_substituir_valores = {
            # Neutro
            'Não aplicável': 0, 'Não sabe': 0,
            # Negativo
            'Não': -1, 'Não, nenhum forneceu': -1, 'Nenhum fez': -1, 'Nenhum deles': -1, 'Não, em nenhum dos meus empregadores anteriores': -1,
            # Meio-termo
            'Talvez': 1, 'Alguns forneceram': 1, 'Alguns fizeram': 1, 'Às vezes': 1, 'Alguns deles': 1, 'Alguns dos meus empregadores anteriores': 1,
            # Positivo
            'Sim': 2, 'Sim, todos eles forneceram': 2, 'Sim, todos eles fizeram': 2, 'Sim, sempre': 2, 'Sim, todos eles': 2,
            'Sim, em todos os meus empregadores anteriores': 2
    }

    # Em colunas binárias, substuitui o valor 0 para -1, para ficar igual ao que foi estabalecido no dicionário "dic_substituir_linhas"
    df_form_respondido = df_form_respondido.replace(0, -1)

    # Mapeando as colunas com dados categóricos ordinais
    dict_ordinais_mapping = {
        'Se um problema de saúde mental o levou a solicitar uma licença médica do trabalho, pedir essa licença seria:': {
            'Não sabe': 0,
            'Very easy': 1,
            'Somewhat easy': 2,
            'Neither easy nor difficult': 3,
            'Somewhat difficult': 4,
            'Very difficult': 5,
        },
        'Você conhecia as opções de cuidados de saúde mental fornecidas por seus empregadores anteriores?': {
            'Não estou ciente no momento': -2,
            'Não, só tomei conhecimento mais tarde': -1,
            'Eu estava ciente de alguns': 1,
            'Sim, eu estava ciente de todos eles': 2
        },
        'Você acha que os membros da equipe/colegas de trabalho o veriam de forma mais negativa se soubessem que você sofre de um problema de saúde mental?': {
            'Não, eles não fazem': -2,
            'Não, eu não acho que eles fariam': -1,
            'Talvez': 1,
            'Sim, eu acho que eles fariam': 2,
            'Sim, eles fazem': 3
        },
        'Quão disposto você estaria a compartilhar com amigos e familiares que tem uma doença mental?': {
            'Não se aplica a mim (não tenho doença mental)': 0,
            'Não aberto': -2,
            'Um pouco não aberto': -1,
            'Neutro': 1,
            'Um pouco aberto': 2,
            'Muito aberto': 3
        },
        'Você observou ou experimentou uma resposta sem apoio ou mal tratada a um problema de saúde mental em seu local de trabalho atual ou anterior?': {
            'Não': -1,
            'Talvez/Sem certeza': 1,
            'Sim, eu observei': 2,
            'Sim, eu experimentei': 3
        },
        'Se você tem um problema de saúde mental, sente que isso interfere no seu trabalho ao ser tratado de forma eficaz?': {
            'Não se aplica a mim': 0,
            'Nunca': -2,
            'Raramente': -1,
            'Às vezes': 1,
            'Frequentemente': 2
        },
    }

    # Substituindo as respostas por valores numéricos 
    df_form_respondido.replace(dict_substituir_valores, inplace=True)
    for coluna, mapeamento in dict_ordinais_mapping.items():
        if coluna in df_form_respondido.columns:
            df_form_respondido[coluna] = df_form_respondido[coluna].replace(mapeamento)

    # Convertendo todas as colunas para tipo numérico
    df_form_respondido = df_form_respondido.apply(pd.to_numeric, errors='coerce')

    # Exibindo o DataFrame do formulário respondido
    st.write('### Resultados do Questionário')
    st.dataframe(df_form_respondido)

    # Caminho do diretório onde o modelo de floresta aleatória para classificação está salvo
    caminho = 'https://github.com/LOUMERIM/Dashboard-DSS/raw/refs/heads/main/modeloRF_treinado.pkl'

    # Fazer o download do arquivo usando requests
    response = requests.get(caminho)
    response.raise_for_status()  # Levanta um erro se o download falhar

    # Carregar o modelo já treinado a partir do conteúdo baixado
    modelo_carregado = pickle.load(io.BytesIO(response.content))

    # Realizando a previsão 
    previsao = modelo_carregado.predict(df_form_respondido)

    # Substituindo a saída de previsão do modelo por strings
    resultado_previsao = ['Não possui distúrbio mental' if p == -1 else 'Possui distúrbio mental' for p in previsao]

    st.write('### Previsão do Modelo')
    st.write(resultado_previsao[0])