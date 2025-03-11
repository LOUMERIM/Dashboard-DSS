import streamlit as st
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

st.title("Análise dos impactos do excesso de trabalho na saúde dos trabalhadores em empresas de tecnologia")

st.header("Banco de dados consultado")
st.write("Dataset: OSMI Mental Health in Tech Survey 2016")
st.write("Link para acesso: https://www.kaggle.com/datasets/osmi/mental-health-in-tech-2016")

st.header("Banco de dados utilizado")
st.write("Dataset pré-processado: https://drive.google.com/file/d/19KHp0jH5v8fq_Kj8t6ybKNgriQyARfA5/view?usp=sharing")

st.header("Importação do banco de dados")
url = 'https://drive.google.com/uc?id=19KHp0jH5v8fq_Kj8t6ybKNgriQyARfA5'
output = 'DB-SaudeMental-Tech_processed.csv'
gdown.download(url, output, quiet=False)
df_processed = pd.read_csv(output)
st.write(df_processed.head())

st.header("Informações gerais sobre o dataset")
st.write(df_processed.info())

st.header("Separação do dataframe em dados de teste e de treino")
target_col = 'Você atualmente tem um distúrbio de saúde mental?'
df_processed_randfor = df_processed[df_processed[target_col] != 1]
amostra_validacao = df_processed_randfor.sample(n=20, random_state=1)
df_processed_randfor = df_processed_randfor.drop(amostra_validacao.index).reset_index(drop=True)
target = df_processed_randfor[target_col]
features = df_processed_randfor.drop(columns=[target_col])
feat_train, feat_test, targ_train, targ_test = train_test_split(features, target, test_size=0.3, random_state=1)

st.write(f'Dimensão de "feat_train": {feat_train.shape}')
st.write(f'Dimensão de "feat_test": {feat_test.shape}')
st.write(f'Dimensão de "targ_train": {targ_train.shape}')
st.write(f'Dimensão de "targ_test": {targ_test.shape}')

st.header("Criação do modelo de IA")
randfor = RandomForestClassifier(oob_score=True, max_depth=5, min_samples_leaf=50, random_state=1)
randfor_trained = randfor.fit(feat_train, targ_train)
randfor_targ_predicted = randfor_trained.predict(feat_test)

def plot_matriz_confusao(target_test, target_predicted, classes):
    randfor_conf_mtrx = confusion_matrix(target_test, target_predicted)
    fig = px.imshow(randfor_conf_mtrx, labels=dict(x='Predito', y='Valor Real'), x=classes, y=classes, color_continuous_scale=['#FF9999', '#99FF99'], text_auto=True)
    fig.update_traces(textfont_size=25, textfont_color='black')
    fig.update_layout(title={'text': '<b>Matriz de Confusão (Floresta Aleatória)</b>', 'x': 0.5, 'font': dict(size=30)}, font=dict(size=20, family='Arial', color='black'), width=700, height=650, coloraxis_showscale=False)
    st.plotly_chart(fig)

plot_matriz_confusao(targ_test, randfor_targ_predicted, classes=['Não', 'Sim'])

st.write("Relatório de Classificação")
st.text(classification_report(targ_test, randfor_targ_predicted))

erro_out_of_bag = 1 - randfor_trained.oob_score_
st.write('Erro OOB:', round(erro_out_of_bag * 100, 2))
st.write('Acurácia:', round(accuracy_score(targ_test, randfor_targ_predicted) * 100, 2))

scores = cross_val_score(randfor_trained, feat_train, targ_train, cv=5)
st.write("Acurácia média usando validação cruzada:", round(scores.mean() * 100, 2))

def plota_melhores_arvores(f, t, model, wideness):
    X_eval = f.to_numpy()
    y_eval = t.to_numpy()
    y_eval_mapped = np.where(y_eval == -1, 0, 1)
    tree_scores = [tree.score(X_eval, y_eval_mapped) for tree in model.estimators_]
    mean_score = np.mean(tree_scores)
    st.write(f'Média de acurácia de todas as árvores: {mean_score:.3f}')
    best_trees_idx = np.argsort(tree_scores)[-5:]
    best_scores = np.array(tree_scores)[best_trees_idx]
    df_trees = pd.DataFrame({'Tree_Index': best_trees_idx, 'Score': best_scores})
    st.write(df_trees.sort_values(by="Score", ascending=False))
    for idx in best_trees_idx:
        tree = model.estimators_[idx]
        fig, ax = plt.subplots(figsize=(wideness, 10))
        plot_tree(tree, feature_names=features.columns, filled=True, ax=ax, rounded=True, fontsize=10)
        ax.set_title(f"Árvore {idx}\nScore: {tree_scores[idx]:.3f}", fontsize=16)
        plt.tight_layout()
        st.pyplot(fig)

plota_melhores_arvores(features, target, randfor_trained, 30)

st.header("Identificação dos melhores hiperparâmetros")
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

# Criação do formulário interativo
df_raw=pd.read_csv("D:/ATVS PROGRAMACAO/DSS/Hand's-On/df_raw (3).csv")
st.write(df_raw.head())
perguntas_alternativas = {}
for col in relevant_features_cols:
    if col in df_raw.columns:
        perguntas_alternativas[col] = df_raw[col].unique().tolist()

#Perguntas
for i in relevant_features_cols.columns:
    st.write(df_raw[i].unique())

with st.form(key='user_input_form'):
    user_input = {}
    for col in relevant_features_cols:
        user_input[col] = st.selectbox(col, options=['Sim', 'Não'])
    
    submit_button = st.form_submit_button(label='Submeter')

if submit_button:
    # Conversão das respostas do usuário para o formato esperado pelo modelo
    user_input_df = pd.DataFrame([user_input])
    user_input_df = user_input_df.replace({'Sim': 2, 'Não': -1})
    
    # Previsão com o modelo treinado
    user_prediction = best_model.predict(user_input_df)
    
    st.write("Resultado da previsão:")
    st.write("Você tem um distúrbio de saúde mental?" if user_prediction[-1] == 1 else "Você não tem um distúrbio de saúde mental.")