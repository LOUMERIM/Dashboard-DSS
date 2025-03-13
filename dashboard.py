# streamlit run c:/Users/Alunos/Downloads/dashboard.py

import pandas as pd
import numpy as np
import streamlit as st


df_processed = pd.read_csv("D:/ATVS PROGRAMACAO/DSS/Hand's-On/DB-SaudeMental-Tech_processed.csv")

df_raw = pd.read_csv("D:/ATVS PROGRAMACAO/DSS/Hand's-On/df_raw.csv")

# Título e texto
st.title('Meu Dashboard')
st.write('exemplo de texto')

# Exemplo de gráfico (placeholder)
df = pd.DataFrame(np.random.randn(10, 2), columns=['X', 'Y'])
st.line_chart(df)

# exemplo de formulário (placeholder)
st.write('Barra de seleção a seguir:')
x = st.slider('x')
st.write('Valor de x:', x)

# Questionário de múltiplas alternativas
verificar_unicos = ['Você já teve um distúrbio de saúde mental no passado?',
                     'Você já procurou tratamento para um problema de saúde mental de um profissional de saúde mental?',
                     'Você foi diagnosticado com uma condição de saúde mental por um profissional médico?',
                     'Você tem histórico familiar de doença mental?',
                     'Se você tem um problema de saúde mental, sente que isso interfere no seu trabalho ao ser tratado de forma eficaz?',
                     'Você acha que discutir um distúrbio de saúde mental com empregadores anteriores teria consequências negativas?',# 1 #====#
                     'Você conhece as opções de saúde mental disponíveis sob a cobertura de saúde do seu empregador?',
                     'Você observou ou experimentou uma resposta sem apoio ou mal tratada a um problema de saúde mental em seu local de trabalho atual ou anterior?',# 2, 4
                     'Você ouviu falar ou observou consequências negativas para colegas de trabalho com problemas de saúde mental em seus locais de trabalho anteriores?',### 1, 2
                     'Suas observações de como outro indivíduo que discutiu um transtorno de saúde mental o tornaram menos propenso a revelar um problema de saúde mental em seu local de trabalho atual?',
                     'Você levantaria um problema de saúde mental com um empregador em potencial em uma entrevista?',
                     'Você sentiu que seus empregadores anteriores levavam a saúde mental tão a sério quanto a saúde física?',
                     'Seus empregadores anteriores forneceram benefícios de saúde mental?',### 3
                     'Você conhecia as opções de cuidados de saúde mental fornecidas por seus empregadores anteriores?',### 3
                     'Você estaria disposto a discutir um problema de saúde mental com seu(s) supervisor(es) direto(s)?',
                     'Quão disposto você estaria a compartilhar com amigos e familiares que tem uma doença mental?',
                     'Você já ouviu falar ou observou consequências negativas para colegas de trabalho que foram abertos sobre problemas de saúde mental em seu local de trabalho?',### 4
                     'Você acha que os membros da equipe/colegas de trabalho o veriam de forma mais negativa se soubessem que você sofre de um problema de saúde mental?', ###
                     'Se um problema de saúde mental o levou a solicitar uma licença médica do trabalho, pedir essa licença seria:']

perguntas_alternativas = {}
for col in verificar_unicos:
    perguntas_alternativas[col] = df_raw[col].unique().tolist()

# Mapeamento de questões e alternativas para parafrasear
parafrasear_questoes = {
     # QUESTÃO 2
    'Você já procurou tratamento para um problema de saúde mental de um profissional de saúde mental?': {
        'pergunta': 'Você já buscou ajuda profissional para um problema de saúde mental?',
        'alternativas': {
            1: 'Sim',
            0: 'Não',
        }
    },
    # QUESTÃO 19
    'Se um problema de saúde mental o levou a solicitar uma licença médica do trabalho, pedir essa licença seria:': {
        'pergunta': 'Se um problema de saúde mental o levou a solicitar uma licença médica, como seria pedir essa licença?',
        'alternativas': {
            'Very easy': 'Muito fácil',
            'Somewhat easy': 'Um pouco fácil',
            'Neither easy nor difficult': 'Nem fácil nem difícil',
            'Somewhat difficult': 'Um pouco difícil',
            'Very difficult': 'Muito difícil'
        }
    }
}


# Questionário de múltiplas alternativas usando st.selectbox()
st.write('### Questionário de Saúde Mental')

for pergunta, alternativas in perguntas_alternativas.items():
    # Parafrasear alternativas se necessário
    #if pergunta in parafrasear_respostas:
        #alternativas = [parafrasear_respostas[pergunta].get(alternativa, alternativa) for alternativa in alternativas]
    
    #resposta = st.selectbox(pergunta, alternativas)
    #st.write(f'Você selecionou: {resposta}')

    pergunta_parafraseada = pergunta
    alternativas_parafraseadas = alternativas
    
    if pergunta, alternativas in parafrasear_questoes.items():
        pergunta_parafraseada = parafrasear_questoes[pergunta]['pergunta']
        
        alternativas_parafraseadas = [
            parafrasear_questoes[pergunta]['alternativas'].get(alternativa, alternativa)
            for alternativa in alternativas
        ]
    
    resposta = st.selectbox(pergunta_parafraseada, alternativas_parafraseadas)
    #st.write(f'Você selecionou: {resposta}')