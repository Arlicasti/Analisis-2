import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar ambos datasets
df_control = pd.read_excel('dataset_control_tabla.xlsx', sheet_name='demographics')
df_alcohol = pd.read_excel('dataset_alcohol_tabla.xlsx', sheet_name='demographics (final)')

# Función mejorada para preparar datos
def prepare_data(df, group_name):
    # Seleccionar columnas relevantes y limpiar
    df = df[['ID', 'sub', 'audit child', 'audit FU3']].dropna(how='all').copy()
    df = df[df['ID'].notna()].copy()
    
    # Resetear índice para evitar problemas
    df = df.reset_index(drop=True)
    
    # Derretir los datos
    melted = pd.melt(df, id_vars=['ID', 'sub'], 
                    value_vars=['audit child', 'audit FU3'],
                    var_name='AUDIT Type', 
                    value_name='Score')
    
    # Añadir columna de grupo
    melted['Group'] = group_name
    
    return melted

# Preparar datos de ambos grupos
control_data = prepare_data(df_control, 'Control')
alcohol_data = prepare_data(df_alcohol, 'Alcohol')

# Combinar datos asegurando índices únicos
combined_data = pd.concat([control_data, alcohol_data], ignore_index=True)

# Verificar que no hay duplicados en los índices
print("¿Hay índices duplicados?", combined_data.index.duplicated().any())

# Opción 1: Boxplots combinados
plt.figure(figsize=(14, 6))
sns.boxplot(x='AUDIT Type', y='Score', hue='Group', 
           data=combined_data, width=0.7, palette={'Control':'skyblue', 'Alcohol':'salmon'})

# Añadir puntos individuales
sns.stripplot(x='AUDIT Type', y='Score', hue='Group', data=combined_data,
             dodge=True, alpha=0.6, size=6, palette={'Control':'blue', 'Alcohol':'red'})

plt.title('Comparación de AUDIT CHILD vs AUDIT FU3 entre Grupos')
plt.ylabel('Puntuación AUDIT')
plt.xticks([0, 1], ['AUDIT CHILD', 'AUDIT FU3'])
plt.legend(title='Grupo', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Opción 2: Violin plots combinados
plt.figure(figsize=(14, 6))
sns.violinplot(x='AUDIT Type', y='Score', hue='Group', data=combined_data, 
              split=True, inner='quartile', palette={'Control':'skyblue', 'Alcohol':'salmon'})

sns.stripplot(x='AUDIT Type', y='Score', hue='Group', data=combined_data,
             dodge=True, alpha=0.6, size=6, palette={'Control':'blue', 'Alcohol':'red'})

plt.title('Distribución de puntuaciones AUDIT (Violín)')
plt.ylabel('Puntuación AUDIT')
plt.xticks([0, 1], ['AUDIT CHILD', 'AUDIT FU3'])
plt.legend(title='Grupo', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Estadísticas descriptivas
print("\nEstadísticas descriptivas por grupo:")
print(combined_data.groupby(['Group', 'AUDIT Type'])['Score'].describe())