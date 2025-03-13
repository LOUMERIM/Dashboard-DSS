import pandas as pd
url = 'https://drive.google.com/uc?id=19KHp0jH5v8fq_Kj8t6ybKNgriQyARfA5'
output = 'DB-SaudeMental-Tech_processed.csv'
gdown.download(url, output, quiet=False)
df_processed = pd.read_csv(output)


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
