import pandas as pd
import streamlit as st
import numpy as np
import gdown
import plotly.express as px
import geopandas as gpd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.tree import plot_tree
from sklearn.model_selection import RandomizedSearchCV

# Baixar e carregar o dataset processado
url = 'https://drive.google.com/uc?id=19KHp0jH5v8fq_Kj8t6ybKNgriQyARfA5'
output = 'DB-SaudeMental-Tech_processed.csv'
gdown.download(url, output, quiet=False)
df_processed = pd.read_csv(output)

# Porcentagem de funcionários que procuraram tratamento
treatment_col = 'Você já procurou tratamento para um problema de saúde mental de um profissional de saúde mental?'
treatment_percentage = df_processed[treatment_col].value_counts(normalize=True) * 100
st.subheader(f"Porcentagem de funcionários que procuraram tratamento: {treatment_percentage[1]:.2f}%")

# Agregar os dados por continente
continents = ['Africa', 'America', 'Asia', 'Europe', 'Oceania', 'Outros']
continent_cols = [f'Continente que trabalha_{continent}' for continent in continents]

continent_treatment_percentage = pd.DataFrame(columns=['Continent', 'Treatment', 'Percentage'])

for continent in continents:
    continent_col = f'Continente que trabalha_{continent}'
    treatment_percentage = df_processed[df_processed[continent_col] == 1][treatment_col].value_counts(normalize=True) * 100
    treatment_percentage = treatment_percentage.reset_index()
    treatment_percentage.columns = ['Treatment', 'Percentage']
    treatment_percentage['Continent'] = continent
    continent_treatment_percentage = pd.concat([continent_treatment_percentage, treatment_percentage])

# Carregar o arquivo SHP
shapefile_path = "D:/ATVS PROGRAMACAO/DSS/Hand's-On/Geodados/World_Continents.shp"
gdf = gpd.read_file(shapefile_path)

# Verificar as colunas do GeoDataFrame
st.write(gdf.columns)

# Mesclar os dados de tratamento com os polígonos dos continentes
# Ajuste 'continent_name' para o nome correto da coluna
gdf = gdf.merge(continent_treatment_percentage, left_on='CONTINENT', right_on='Continent')

# Exibir os dados no Streamlit
st.write(gdf)

import json
import geopandas as gpd
import plotly.express as px

@st.cache_data
def load_geojson(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

geojson_data = load_geojson("World_Continents_simplified.geojson")
