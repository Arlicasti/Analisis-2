import pandas as pd
from scipy.stats import ttest_ind, chi2_contingency
from tabulate import tabulate
import os

# --- PASO 1: Cargar datos con nombres de columnas correctos ---
# Dataset Alcohol (sin ADNI/MID)
df_alcohol = pd.read_excel('dataset_alcohol_tabla.xlsx', usecols=['ID', 'sub', 'sex', 'center', 'Edad en días', 'audit child', 'audit FU3'])

# Dataset Control (con ADNI/MID)
df_control = pd.read_excel('dataset_control_tabla.xlsx')
df_control = df_control.rename(columns={
    'Edad en días (ADNI/MID)': 'Edad en días (ADNI)',
    'Unnamed: 6': 'Edad en días (MID)'  # Asumiendo que MID está en la columna 6
})

# --- PASO 2: Calcular edad promedio (solo para controles) ---
def calcular_edad_promedio(df):
    if 'Edad en días (ADNI)' in df.columns and 'Edad en días (MID)' in df.columns:
        df['Edad (días)'] = (df[['Edad en días (ADNI)', 'Edad en días (MID)']].mean(axis=1)).round().astype(int)
    else:
        df['Edad (días)'] = df['Edad en días']  # Para alcohol
    return df

df_control = calcular_edad_promedio(df_control)
df_alcohol['Edad (días)'] = df_alcohol['Edad en días']  # Alcohol usa una sola columna

# --- PASO 3: Función para p-valores (actualizada) ---
def calculate_pvalues(df_control, df_alcohol, center=None):
    if center:
        df_control = df_control[df_control["center"] == center]
        df_alcohol = df_alcohol[df_alcohol["center"] == center]
    
    # Tabla de contingencia para sexo
    contingency_table = pd.crosstab(
        index=pd.concat([df_alcohol["sex"], df_control["sex"]]),
        columns=pd.concat([
            pd.Series("Alcohol", index=df_alcohol.index),
            pd.Series("Control", index=df_control.index)
        ])
    )
    
    # Cálculo de p-valores
    _, p_sex, _, _ = chi2_contingency(contingency_table)
    _, p_age = ttest_ind(df_alcohol["Edad (días)"], df_control["Edad (días)"])
    _, p_audit_child = ttest_ind(df_alcohol["audit child"], df_control["audit child"])
    _, p_audit_fu3 = ttest_ind(df_alcohol["audit FU3"], df_control["audit FU3"])
    
    return {
        "p_sex": round(p_sex, 2),
        "p_age": round(p_age, 2),
        "p_audit_child": round(p_audit_child, 2),
        "p_audit_fu3": f"{p_audit_fu3:.3f}" if p_audit_fu3 < 0.001 else round(p_audit_fu3, 2)
    }

# --- PASO 4: Generar tabla por centro ---
centros = ["DRESDEN", "DUBLIN", "BERLIN", "NOTTINGHAM", "MANNHEIM", "LONDON", "HAMBURG", "PARIS"]
tabla = []

for centro in centros:
    control_center = df_control[df_control["center"].str.upper() == centro.upper()]
    alcohol_center = df_alcohol[df_alcohol["center"].str.upper() == centro.upper()]
    
    n_control = len(control_center)
    n_alcohol = len(alcohol_center)
    
    stats = {
        "Hombres (Control)": f"{sum(control_center['sex'].str.upper() == 'M')} ({sum(control_center['sex'].str.upper() == 'M') / n_control * 100:.0f}%)" if n_control > 0 else "0 (0%)",
        "Mujeres (Control)": f"{sum(control_center['sex'].str.upper() == 'F')} ({sum(control_center['sex'].str.upper() == 'F') / n_control * 100:.0f}%)" if n_control > 0 else "0 (0%)",
        "Hombres (Alcohol)": f"{sum(alcohol_center['sex'].str.upper() == 'M')} ({sum(alcohol_center['sex'].str.upper() == 'M') / n_alcohol * 100:.0f}%)" if n_alcohol > 0 else "0 (0%)",
        "Mujeres (Alcohol)": f"{sum(alcohol_center['sex'].str.upper() == 'F')} ({sum(alcohol_center['sex'].str.upper() == 'F') / n_alcohol * 100:.0f}%)" if n_alcohol > 0 else "0 (0%)",
        "Edad (Control)": f"{control_center['Edad (días)'].mean():.0f} ± {control_center['Edad (días)'].std():.0f}" if n_control > 0 else "N/A",
        "Edad (Alcohol)": f"{alcohol_center['Edad (días)'].mean():.0f} ± {alcohol_center['Edad (días)'].std():.0f}" if n_alcohol > 0 else "N/A",
        "AUDIT Child (Control)": f"{control_center['audit child'].mean():.1f} ± {control_center['audit child'].std():.1f}" if n_control > 0 else "N/A",
        "AUDIT Child (Alcohol)": f"{alcohol_center['audit child'].mean():.1f} ± {alcohol_center['audit child'].std():.1f}" if n_alcohol > 0 else "N/A",
        "AUDIT FU3 (Control)": f"{control_center['audit FU3'].mean():.1f} ± {control_center['audit FU3'].std():.1f}" if n_control > 0 else "N/A",
        "AUDIT FU3 (Alcohol)": f"{alcohol_center['audit FU3'].mean():.1f} ± {alcohol_center['audit FU3'].std():.1f}" if n_alcohol > 0 else "N/A",
    }
    
    pvals = calculate_pvalues(control_center, alcohol_center) if n_control > 0 and n_alcohol > 0 else {
        "p_sex": "N/A", "p_age": "N/A", "p_audit_child": "N/A", "p_audit_fu3": "N/A"
    }
    
    tabla.extend([
        {"Centro": centro, "Variable": "Sexo, Hombres", "Control": stats["Hombres (Control)"], "Alcohol": stats["Hombres (Alcohol)"], "p-valor": ""},
        {"Centro": centro, "Variable": "Sexo, Mujeres", "Control": stats["Mujeres (Control)"], "Alcohol": stats["Mujeres (Alcohol)"], "p-valor": pvals["p_sex"]},
        {"Centro": centro, "Variable": "Edad (días)", "Control": stats["Edad (Control)"], "Alcohol": stats["Edad (Alcohol)"], "p-valor": pvals["p_age"]},
        {"Centro": centro, "Variable": "AUDIT Child", "Control": stats["AUDIT Child (Control)"], "Alcohol": stats["AUDIT Child (Alcohol)"], "p-valor": pvals["p_audit_child"]},
        {"Centro": centro, "Variable": "AUDIT FU3", "Control": stats["AUDIT FU3 (Control)"], "Alcohol": stats["AUDIT FU3 (Alcohol)"], "p-valor": pvals["p_audit_fu3"]}
    ])

# --- Resultados ---
df_tabla = pd.DataFrame(tabla)
print(tabulate(df_tabla, headers="keys", tablefmt="grid", showindex=False))

# Exportar
df_tabla.to_excel("tabla_final.xlsx", index=False)
df_tabla.to_latex("tabla_final.tex", index=False)