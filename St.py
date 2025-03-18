import streamlit as st
import pandas as pd
import numpy as np
import gdown
import plotly.express as px
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.tree import plot_tree
from sklearn.model_selection import RandomizedSearchCV
import geopandas as gpd

st.title("Análise dos impactos do excesso de trabalho na saúde dos trabalhadores em empresas de tecnologia")

st.header("Banco de dados consultado")
st.write("Dataset: OSMI Mental Health in Tech Survey 2016")
st.write("Link para acesso: https://www.kaggle.com/datasets/osmi/mental-health-in-tech-2016")
st.write("""Descrição: O dataset contém respostas de uma pesquisa sobre saúde mental no ambiente de trabalho,
 realizada em 2016 com funcionários de empresas de tecnologia. O banco de dados conta com 63 colunas e um 
 pouco mais de 1400 dados.""")


url = 'https://drive.google.com/uc?id=19KHp0jH5v8fq_Kj8t6ybKNgriQyARfA5'
output = 'DB-SaudeMental-Tech_processed.csv'
gdown.download(url, output, quiet=False)
df_processed = pd.read_csv(output)

#######################################################################
#Random Forest
#######################################################################
target_col = 'Você atualmente tem um distúrbio de saúde mental?'
df_processed_randfor = df_processed[df_processed[target_col] != 1]
amostra_validacao = df_processed_randfor.sample(n=20, random_state=1)
df_processed_randfor = df_processed_randfor.drop(amostra_validacao.index).reset_index(drop=True)
target = df_processed_randfor[target_col]
features = df_processed_randfor.drop(columns=[target_col])
feat_train, feat_test, targ_train, targ_test = train_test_split(features, target, test_size=0.3, random_state=1)
randfor = RandomForestClassifier(oob_score=True, max_depth=5, min_samples_leaf=50, random_state=1)
randfor_trained = randfor.fit(feat_train, targ_train)
randfor_targ_predicted = randfor_trained.predict(feat_test)

#################################################
#KPIs
#################################################


# Percentual de trabalhadores com problemas de saúde mental
mental_health_issues = df_processed[target_col].value_counts(normalize=True) * 100
mental_health_issues.index = mental_health_issues.index.map({2: 'Sim', 1: 'Não sabe', -1: 'Não'})
fig = px.pie(values=mental_health_issues, names=mental_health_issues.index, title='Percentual de trabalhadores com problemas de saúde mental')
st.plotly_chart(fig)
st.write("No gráfico acima, é possível observar que mais de 40% dos trabalhadores possuem problemas de saúde mental, o que reflete uma realidade preocupante e mostra como essa questão afeta uma parte significativa da força de trabalho.")

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
    continent_treatment_percentage = pd.concat([continent_treatment_percentage, treatment_percentage], ignore_index=True)

@st.cache_data
def load_shapefile():
    return gpd.read_file("D:/ATVS PROGRAMACAO/DSS/Hand's-On/Geodados/World_Continents.shp")

gdf = load_shapefile()
mapeamento = {
    "North America": "America",
    "South America": "America",
    "Antarctica": "Outros",
    # Adicione outras correções
}
continent_treatment_percentage["Continent"] = continent_treatment_percentage["Continent"].replace(mapeamento)

# Mesclar os dados de tratamento com os polígonos dos continentes
gdf = gdf.merge(continent_treatment_percentage, left_on='CONTINENT', right_on='Continent')

# Mapear os valores de tratamento
continent_treatment_percentage['Treatment'] = continent_treatment_percentage['Treatment'].map({1: 'Procurou Tratamento', 0: 'Não Procurou Tratamento'})

# Criar o mapa de calor
'''fig = px.choropleth(gdf, geojson=gdf.geometry, locations=gdf.index, color='Percentage',
                    hover_name='Continent', animation_frame='Treatment', 
                    title='Porcentagem de funcionários que procuraram tratamento por continente')'''

fig.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(fig)

# Impacto da cultura organizacional na busca por tratamento
culture_col = 'Você acha que discutir um distúrbio de saúde mental com empregadores anteriores teria consequências negativas?'
culture_impact = df_processed[[treatment_col, culture_col]].corr().iloc[0, 1]
st.subheader(f"Impacto da cultura organizacional na busca por tratamento: {culture_impact:.2f}")

# Nível de conscientização sobre os benefícios de saúde mental oferecidos pela empresa
awareness_col = 'Você conhece as opções de saúde mental disponíveis sob a cobertura de saúde do seu empregador?'
awareness_mapping = {
    'Não sabe': 0,
    'Não': -1,
    'Sim': 2
}
df_processed[awareness_col] = df_processed[awareness_col].map(awareness_mapping)
awareness_percentage = df_processed[awareness_col].value_counts(normalize=True) * 100

# Gráfico de Colunas
fig = px.bar(awareness_percentage, x=awareness_percentage.index, y=awareness_percentage.values,
             labels={'x': 'Conhece os Benefícios', 'y': 'Porcentagem'},
             title='Nível de Conscientização sobre os Benefícios de Saúde Mental Oferecidos pela Empresa')

st.plotly_chart(fig)

st.header("Relatório de Classificação")
st.text(classification_report(targ_test, randfor_targ_predicted))

erro_out_of_bag = 1 - randfor_trained.oob_score_
st.write('Erro OOB:', round(erro_out_of_bag * 100, 2))
st.write('Acurácia:', round(accuracy_score(targ_test, randfor_targ_predicted) * 100, 2))

scores = cross_val_score(randfor_trained, feat_train, targ_train, cv=5)
st.write("Acurácia média usando validação cruzada:", round(scores.mean() * 100, 2))

relevant_features_cols = ['Você já teve um distúrbio de saúde mental no passado?',
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
                          'Você sentiu que seus empregadores anteriores levavam a saúde mental tão a sério quanto a saúde física?', 'Seus empregadores anteriores forneceram benefícios de saúde mental?', 
                          'Você conhecia as opções de cuidados de saúde mental fornecidas por seus empregadores anteriores?', 
                          'Você estaria disposto a discutir um problema de saúde mental com seu(s) supervisor(es) direto(s)?', 
                          'Quão disposto você estaria a compartilhar com amigos e familiares que tem uma doença mental?', 
                          'Você já ouviu falar ou observou consequências negativas para colegas de trabalho que foram abertos sobre problemas de saúde mental em seu local de trabalho?', 
                          'Você acha que os membros da equipe/colegas de trabalho o veriam de forma mais negativa se soubessem que você sofre de um problema de saúde mental?', 
                          'Se um problema de saúde mental o levou a solicitar uma licença médica do trabalho, pedir essa licença seria:']
relevant_features = df_processed_randfor[relevant_features_cols]
X_train, X_test, y_train, y_test = train_test_split(relevant_features, target, test_size=0.3, random_state=1)

#param_dist = {'n_estimators': [1000], 'max_depth': list(range(3, 11)), 'min_samples_split': [2, 5, 10, 20, 50], 'min_samples_leaf': list(range(1, 6)), 'bootstrap': [True], 'oob_score': [True], 'max_features': ['sqrt']}
#rf = RandomForestClassifier()
#random_search = RandomizedSearchCV(estimator=rf, param_distributions=param_dist, n_iter=50, cv=5, verbose=2, scoring='accuracy', n_jobs=-1, random_state=42)
#random_search.fit(X_train, y_train)
#best_params = random_search.best_params_
#st.write('Melhores parâmetros:', best_params)

#st.header("Treinamento do modelo com os melhores hiperparâmetros")
#best_model = random_search.best_estimator_
#randfor_targ_predicted = best_model.predict(X_test)
#plot_matriz_confusao(y_test, randfor_targ_predicted, classes=['Não', 'Sim'])
#st.write("Relatório de Classificação")
#st.text(classification_report(y_test, randfor_targ_predicted))
#erro_out_of_bag = 1 - best_model.oob_score_
#st.write('Erro OOB:', round(erro_out_of_bag * 100, 2))
#st.write('Acurácia:', round(accuracy_score(y_test, randfor_targ_predicted) * 100, 2))
#scores = cross_val_score(best_model, X_train, y_train, cv=5)
#st.write("Acurácia média usando validação cruzada:", round(scores.mean() * 100, 2))
#plota_melhores_arvores(relevant_features, target, best_model, 160)

st.header("Demonstração de uso do modelo com um dado novo")
st.write("Por favor, preencha o questionário abaixo para prever se você tem um distúrbio de saúde mental.")


    ###########################################################################
    #GABRIEL CODES
    ###########################################################################
"""st.title('Meu Dashboard')
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

# Mapeamento de respostas para parafrasear
parafrasear_respostas = {
     # PERGUNTA 2
    'Você já procurou tratamento para um problema de saúde mental de um profissional de saúde mental?': {
        1: 'Sim',
        0: 'Não',
    },
     # PERGUNTA 19
    'Se um problema de saúde mental o levou a solicitar uma licença médica do trabalho, pedir essa licença seria:': {
        'Very easy': 'Muito fácil',
        'Somewhat easy': 'Um pouco fácil',
        'Neither easy nor difficult': 'Nem fácil nem difícil',
        'Somewhat difficult': 'Um pouco difícil',
        'Very difficult': 'Muito difícil'
    }
    # Adicionar mais parafraseamentos aqui
#}

# Questionário de múltiplas alternativas usando st.selectbox()
st.write('### Questionário de Saúde Mental')

for pergunta, alternativas in perguntas_alternativas.items():
    # Parafrasear alternativas se necessário
    if pergunta in parafrasear_respostas:
        alternativas = [parafrasear_respostas[pergunta].get(alternativa, alternativa) for alternativa in alternativas]
    
    resposta = st.selectbox(pergunta, alternativas)
    st.write(f'Você selecionou: {resposta}')

st.write(df_processed.collums())"""