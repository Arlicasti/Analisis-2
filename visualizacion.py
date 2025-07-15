import pandas as pd
import matplotlib.pyplot as plt
import os

# Configuración de rutas para TU estructura específica
def cargar_datos():
    """Carga los archivos Excel desde tu repositorio"""
    try:
        # No necesitas la carpeta 'datos/' porque tus archivos están en la raíz
        df_alcohol = pd.read_excel('dataset_alcohol.xlsx')
        df_control = pd.read_excel('dataset_control.xlsx')
        
        print("✅ Archivos cargados correctamente")
        return df_control, df_alcohol
    
    except Exception as e:
        print(f"❌ Error al cargar archivos: {str(e)}")
        print("Verifica que:")
        print("1. Los archivos están en la misma carpeta que tu script")
        print("2. Los nombres son EXACTAMENTE: dataset_alcohol.xlsx y dataset_control.xlsx")
        print("3. Tienen las columnas 'sex' y 'center'")
        return None, None

# Versión simplificada del gráfico de conteo absoluto
def grafico_simple(df, titulo):
    if df is not None:
        df = df[['sex', 'center']].dropna()
        conteo = df.groupby(['center', 'sex']).size().unstack()
        
        ax = conteo.plot(kind='bar', stacked=True, 
                        color=['#4e79a7', '#e15759'], 
                        figsize=(10,6), title=titulo)
        plt.xticks(rotation=45)
        plt.show()

# Cargar y visualizar
df_control, df_alcohol = cargar_datos()

if df_control is not None:
    grafico_simple(df_control, "Grupo Control")
    
if df_alcohol is not None:
    grafico_simple(df_alcohol, "Grupo Alcohol")