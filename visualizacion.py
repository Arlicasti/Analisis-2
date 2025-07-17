# Sólo genera una sola barra por centro
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
        print(df_control.head())  # Muestra las primeras filas