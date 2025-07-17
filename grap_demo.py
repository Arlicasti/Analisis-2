import pandas as pd
import matplotlib.pyplot as plt
import os

def cargar_datos():
    """Carga archivos Excel desde la carpeta del proyecto."""
    try:
        # Ruta absoluta automática (independiente del sistema operativo)
        ruta_base = os.path.dirname(os.path.abspath(__file__))
        
        # Combinar rutas para los archivos
        df_alcohol = pd.read_excel(os.path.join(ruta_base, 'dataset_alcohol.xlsx'))
        df_control = pd.read_excel(os.path.join(ruta_base, 'dataset_control.xlsx'))
        
        print("✓ Archivos cargados correctamente")
        return df_control, df_alcohol

    except Exception as e:
        print(f"✗ Error al cargar archivos: {str(e)}")
        print("Verifica que:")
        print("- Los archivos estén en la misma carpeta que el script.")
        print("- Los nombres coincidan exactamente (incluyendo mayúsculas).")
        return None, None

# Ejemplo de uso
if __name__ == "__main__":
    df_control, df_alcohol = cargar_datos()
    
    if df_control is not None:
        print("\nDatos de control:")
        print(df_control.head())  # Muestra las primeras filas
        
        # ---- MODIFICACIÓN ÚNICA: Ajuste de nombres de columnas ----
        colores = ['#b19cd9', '#77dd77']  # Lila y verde
        
        # Cambio aquí: 'Centro' → 'center', 'Género' → 'sex'
        datos_agrupados = df_control.groupby(['center', 'sex']).size().unstack()
        
        ax = datos_agrupados.plot(kind='bar', color=colores, width=0.8)
        plt.title("Distribución por centro y sexo (Grupo Control)")
        plt.xlabel("Centro")
        plt.ylabel("Número de participantes")
        plt.legend(title='Sexo')  # Cambiado de 'Género' a 'Sexo'
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    
    if df_alcohol is not None:
        print("\nDatos de alcohol:")
        print(df_alcohol.head())
        
        # ---- MISMO AJUSTE PARA DATOS DE ALCOHOL ----
        datos_agrupados = df_alcohol.groupby(['center', 'sex']).size().unstack()
        
        ax = datos_agrupados.plot(kind='bar', color=colores, width=0.8)
        plt.title("Distribución por centro y sexo (Grupo Alcohol)")
        plt.xlabel("Centro")
        plt.ylabel("Número de participantes")
        plt.legend(title='Sexo')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

        #Agregar en las 'y' que corresponde al número de participantes y ajustar con respecto a que 
        # ahora serán 100 participantes, no 104