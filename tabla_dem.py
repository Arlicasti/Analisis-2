import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, ttest_ind

# 1. Cargar datos
df_control = pd.read_excel('dataset_control_tabla.xlsx', sheet_name='demographics')
df_alcohol = pd.read_excel('dataset_alcohol_tabla.xlsx')

# 2. Normalizar nombres de columnas (convertir todo a minúsculas y eliminar espacios)
def normalizar_columnas(df):
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    return df

df_control = normalizar_columnas(df_control)
df_alcohol = normalizar_columnas(df_alcohol)

# 3. Mapeo de nombres de centros
centro_mapping = {
    'dresden': 'DRESDE',
    'dublin': 'DUBLÍN',
    'dublín': 'DUBLÍN',
    'berlin': 'BERLÍN',
    'berlín': 'BERLÍN',
    'nottingham': 'NOTTINGHAM',
    'mannheim': 'MANNHEIM',
    'hamburg': 'HAMBURGO',
    'paris': 'PARÍS',
    'london': 'LONDRES'
}

# 4. Estandarizar nombres de centros
def estandarizar_centro(nombre):
    nombre = str(nombre).lower().strip()
    for key in centro_mapping:
        if key.lower() == nombre:
            return centro_mapping[key]
    return nombre.title()  # Si no está en el mapeo, devolver con formato título

df_control['center'] = df_control['center'].apply(estandarizar_centro)
df_alcohol['center'] = df_alcohol['center'].apply(estandarizar_centro)

# 5. Lista de centros finales
centros_finales = ['DRESDE', 'DUBLÍN', 'BERLÍN', 'NOTTINGHAM', 
                  'MANNHEIM', 'HAMBURGO', 'PARÍS', 'LONDRES']

# 6. Variables a analizar (USANDO LOS NOMBRES NORMALIZADOS)
variables = {
    'sexo': {'hombres': 'm', 'mujeres': 'f'},
    'edad': {
        'control_cols': ['edad_en_días_(adni)', 'edad_en_días_(mid)'],
        'alcohol_col': 'edad_en_días'
    },
    'audit_child': 'numérica',
    'audit_fu3': 'numérica'
}

# 7. Función para calcular p-valor
def calcular_p_valor(control, alcohol, tipo):
    if tipo == 'numérica':
        _, p = ttest_ind(control.dropna(), alcohol.dropna(), equal_var=False)
    else:  # categórica
        tabla_contingencia = pd.crosstab(
            np.concatenate([control, alcohol]),
            np.repeat(['Control', 'Alcohol'], [len(control), len(alcohol)])
        )
        _, p, _, _ = chi2_contingency(tabla_contingencia)
    return p

# 8. Construir la tabla de resultados
resultados = []
for centro in centros_finales:
    control_centro = df_control[df_control['center'].str.lower() == centro.lower()]
    alcohol_centro = df_alcohol[df_alcohol['center'].str.lower() == centro.lower()]
    
    if len(alcohol_centro) == 0:
        print(f"Advertencia: No hay datos de Alcohol para {centro}")
        continue
    
    for variable, config in variables.items():
        if variable == 'sexo':
            for categoria, valor in config.items():
                n_control = sum(control_centro['sex'].str.lower() == valor) if len(control_centro) > 0 else 0
                n_alcohol = sum(alcohol_centro['sex'].str.lower() == valor)
                
                pct_control = f"{n_control} ({n_control/len(control_centro)*100:.0f}%)" if len(control_centro) > 0 else "N/A"
                pct_alcohol = f"{n_alcohol} ({n_alcohol/len(alcohol_centro)*100:.0f}%)"
                
                p_valor = calcular_p_valor(
                    control_centro['sex'].str.lower() == valor if len(control_centro) > 0 else [False]*len(alcohol_centro),
                    alcohol_centro['sex'].str.lower() == valor,
                    'categórica'
                )
                
                resultados.append([
                    centro,
                    f"Sexo, {categoria.capitalize()}",
                    pct_control,
                    pct_alcohol,
                    f"{p_valor:.2f}" if p_valor >= 0.001 else "<0.001"
                ])
        
        elif variable == 'edad':
            # Procesamiento especial para Edad
            if len(control_centro) > 0:
                edad_control = control_centro[variables['edad']['control_cols']].mean(axis=1)
                media_control = edad_control.mean()
                std_control = edad_control.std()
            else:
                media_control, std_control = np.nan, np.nan
            
            edad_alcohol = alcohol_centro[variables['edad']['alcohol_col']]
            media_alcohol = edad_alcohol.mean()
            std_alcohol = edad_alcohol.std()
            
            p_valor = calcular_p_valor(
                edad_control if len(control_centro) > 0 else edad_alcohol * np.nan,
                edad_alcohol,
                'numérica'
            )
            
            resultados.append([
                centro,
                'Edad (días)',
                f"{media_control:.1f} ± {std_control:.1f}" if not np.isnan(media_control) else "N/A",
                f"{media_alcohol:.1f} ± {std_alcohol:.1f}",
                f"{p_valor:.2f}" if p_valor >= 0.001 else "<0.001"
            ])
        
        else:  # Para audit_child y audit_fu3
            col_name = variable  # Usamos los nombres normalizados
            if len(control_centro) > 0:
                media_control = control_centro[col_name].mean()
                std_control = control_centro[col_name].std()
            else:
                media_control, std_control = np.nan, np.nan
            
            media_alcohol = alcohol_centro[col_name].mean()
            std_alcohol = alcohol_centro[col_name].std()
            
            p_valor = calcular_p_valor(
                control_centro[col_name] if len(control_centro) > 0 else alcohol_centro[col_name] * np.nan,
                alcohol_centro[col_name],
                'numérica'
            )
            
            # Mostrar el nombre original en la tabla final
            nombre_variable = 'AUDIT Child' if variable == 'audit_child' else 'AUDIT FU3'
            resultados.append([
                centro,
                nombre_variable,
                f"{media_control:.1f} ± {std_control:.1f}" if not np.isnan(media_control) else "N/A",
                f"{media_alcohol:.1f} ± {std_alcohol:.1f}",
                f"{p_valor:.2f}" if p_valor >= 0.001 else "<0.001"
            ])

# 9. Crear DataFrame final
df_resultados = pd.DataFrame(
    resultados,
    columns=['Centro', 'Variable', 'Control', 'Alcohol', 'p-valor']
)

# =============================================
# GENERACIÓN DE TABLA COMO IMAGEN (MATPLOTLIB) - VERSIÓN CORREGIDA
# =============================================
import matplotlib.pyplot as plt
from pandas.plotting import table

# 1. Configurar estilo profesional (USAR 'seaborn-v0_8' en vez de 'seaborn')
plt.style.use('seaborn-v0_8')  # 👈 Cambio clave aquí
fig, ax = plt.subplots(figsize=(14, 8))
ax.axis('off')

# 2. Crear tabla (el resto del código sigue igual)
tabla = table(ax, df_resultados.round(2), 
             loc='center', 
             cellLoc='center',
             colWidths=[0.18]*len(df_resultados.columns))

# 3. Diseño avanzado
tabla.auto_set_font_size(False)
tabla.set_fontsize(11)

# 4. Colores y formato
for (i, j), cell in tabla.get_celld().items():
    if i == 0:
        cell.set_facecolor('#1F77B4')
        cell.set_text_props(color='white', weight='bold')
    elif i%2 == 0:
        cell.set_facecolor('#F5F5F5')

# 5. Guardar imagen
plt.tight_layout()
plt.savefig('resultados_tabla.png', dpi=300, bbox_inches='tight')
print("\n✅ Tabla guardada como 'resultados_tabla.png'")

# Para exportar a PDF (para publicaciones científicas), cambiar la línea de guardado por:
# plt.savefig('resultados_tabla.pdf', bbox_inches='tight', format='pdf')

# 10. Guardar y mostrar resultados
df_resultados.to_excel("resultados_comparativos.xlsx", index=False)
print("\nTabla de Resultados:")
print(df_resultados.to_markdown(index=False, tablefmt="grid"))