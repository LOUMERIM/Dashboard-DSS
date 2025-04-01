import pandas as pd
import numpy as np
import gdown
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.tree import plot_tree
from sklearn.model_selection import RandomizedSearchCV
import geopandas as gpd 
import streamlit as st
import plotly.graph_objects as go

url = 'https://drive.google.com/uc?id=19KHp0jH5v8fq_Kj8t6ybKNgriQyARfA5'
output = 'DB-SaudeMental-Tech_processed.csv'
gdown.download(url, output, quiet=False)
df_processed = pd.read_csv(output)

# --- Preparação dos Dados ---
# Supondo que exista uma coluna que indique diagnósticos. 
# Por exemplo, vamos assumir que a coluna 'Já recebeu diagnóstico de transtorno' possui:
# 1 para "sim" e 0 para "não". 
# Se houver colunas separadas para cada diagnóstico, você pode criar uma coluna agregada.
# Aqui, vamos criar uma coluna 'diagnostico' que seja 1 se o respondente recebeu qualquer diagnóstico (pode ajustar conforme necessário).
# Se os diagnósticos estiverem em várias colunas, você pode fazer:
diagnosticos = ['Mood Disorder (Depression, Bipolar Disorder, etc)',
                'Stress Response Syndromes', 'Substance Use Disorder',
                'Obsessive-Compulsive Disorder', 'Eating Disorder (Anorexia, Bulimia, etc)',
                'Personality Disorder (Borderline, Antisocial, Paranoid, etc)',
                'Addictive Disorder', 'Seasonal Affective Disorder', 'Burn out',
                'Dissociative Disorder', 'Depression', 'Traumatic Brain Injury',
                'Gender Dysphoria', 'Psychotic Disorder (Schizophrenia, Schizoaffective, etc)',
                'Sexual addiction', 'Sleeping Disorder', 'Transgender',
                'Intimate Disorder', 'Schizotypal Personality Disorder',
                'Autism Spectrum Disorder (ASD)', 'Anxiety Disorder', 'Attention Deficit (ADHD)',
                'Pervasive Developmental Disorder (PDD-NOS)', 'PTSD']  
# Caso os diagnósticos estejam codificados com 1 para sim, 0 para não:
# Cria uma coluna que indica se houve diagnóstico (pode ser a soma ou a presença de 1 em qualquer coluna)
if all(col in df_processed.columns for col in diagnosticos):
    df_processed['diagnostico'] = df_processed[diagnosticos].sum(axis=1).apply(lambda x: 2 if x > -1 else 0)
else:
    # Se houver apenas uma coluna agregada, por exemplo:
    df_processed['diagnostico'] = df_processed['Já recebeu diagnóstico de transtorno']

# Agora, escolha se quer agrupar por "tamanho da empresa" ou "setor".
# Exemplo 1: Agrupar por tamanho da empresa.
# Supondo que a coluna de tamanho seja "Quantos funcionários sua empresa ou organização tem?"
df_processed['tamanho_empresa'] = df_processed["Quantos funcionários sua empresa ou organização tem?"]

# Agrupamento: calcular a incidência de diagnósticos por tamanho da empresa.
# Contar o total de respondentes por tamanho
total_por_tamanho = df_processed.groupby('tamanho_empresa').size().reset_index(name='total')
# Contar os diagnósticos positivos
diagnostico_por_tamanho = df_processed[df_processed['diagnostico'] == 1].groupby('tamanho_empresa').size().reset_index(name='diagnostico_positivo')

# Unir os dados
df_tamanho = pd.merge(total_por_tamanho, diagnostico_por_tamanho, on='tamanho_empresa', how='left')
df_tamanho['diagnostico_positivo'] = df_tamanho['diagnostico_positivo'].fillna(0)
df_tamanho['percentual_diagnostico'] = (df_tamanho['diagnostico_positivo'] / df_tamanho['total']) * 100

# Exemplo 2: Agrupar por setor (exemplo: empresas de tecnologia vs. outros)
# Supondo que exista a coluna "Sua empresa é focada no ramo da tecnologia/organização?"
df_processed['setor'] = df_processed["Sua empresa é focada no ramo da tecnologia/organização?"]
# Por exemplo, 1 para empresas de tecnologia e -1 para outras (ajuste conforme seus dados)
total_por_setor = df_processed.groupby('setor').size().reset_index(name='total')
diagnostico_por_setor = df_processed[df_processed['diagnostico'] == 1   ].groupby('setor').size().reset_index(name='diagnostico_positivo')
df_setor = pd.merge(total_por_setor, diagnostico_por_setor, on='setor', how='left')
df_setor['diagnostico_positivo'] = df_setor['diagnostico_positivo'].fillna(0)
df_setor['percentual_diagnostico'] = (df_setor['diagnostico_positivo'] / df_setor['total']) * 100

# --- Visualização com Boxplot ---

# Se você quiser analisar a distribuição individual das respostas (caso tenha valores contínuos, por exemplo),
# pode criar um boxplot que compare os grupos com diagnóstico vs. sem diagnóstico para o tamanho ou setor.

# Exemplo: Boxplot da variável "tamanho da empresa" para quem tem diagnóstico versus não
fig_box = px.box(df_processed, x='diagnostico', 
                 y="Quantos funcionários sua empresa ou organização tem?",
                 points="all",
                 labels={
                     'diagnostico': 'Diagnóstico (1=Sim, 0=Não)',
                     "Quantos funcionários sua empresa ou organização tem?": "Tamanho da Empresa"
                 },
                 title="Distribuição do Tamanho da Empresa por Diagnóstico de Transtornos")

# Se preferir usar os dados agregados e criar um boxplot do percentual de diagnósticos,
# talvez um gráfico de barras ou scatter seja mais adequado para o KPI.
# Mas se você tiver respostas individuais (por exemplo, escalas), o boxplot ajuda a visualizar a dispersão.

# --- Exibir no Streamlit ---
st.title("Dashboard: Incidência de Diagnósticos vs. Tamanho/Setor")
st.subheader("Agrupado por Tamanho da Empresa")
st.dataframe(df_tamanho)
st.plotly_chart(px.bar(df_tamanho, 
                       x='tamanho_empresa', 
                       y='percentual_diagnostico',
                       labels={'tamanho_empresa': 'Tamanho da Empresa', 'percentual_diagnostico': 'Percentual de Diagnósticos'},
                       title='Percentual de Diagnósticos por Tamanho da Empresa'),
               use_container_width=True)

st.subheader("Agrupado por Setor (Tecnologia vs. Outros)")
st.dataframe(df_setor)
st.plotly_chart(px.bar(df_setor, 
                       x='setor', 
                       y='percentual_diagnostico',
                       labels={'setor': 'Setor', 'percentual_diagnostico': 'Percentual de Diagnósticos'},
                       title='Percentual de Diagnósticos por Setor'),
               use_container_width=True)

st.subheader("Boxplot: Tamanho da Empresa por Diagnóstico")
st.plotly_chart(fig_box, use_container_width=True)