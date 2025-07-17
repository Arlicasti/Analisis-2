import pandas as pd
from scipy.stats import ttest_ind, chi2_contingency
from tabulate import tabulate

# Cargar datos
df_control = pd.read_excel("dataset_control.xlsx")  # Reemplaza con tu ruta
df_alcohol = pd.read_excel("dataset_alcohol.xlsx")  # Reemplaza con tu ruta

# --- PASO 1: Calcular edad promedio (solo para controles con dos valores) ---
def calcular_edad_promedio(df):
    if 'Edad en días (ADNI)' in df.columns and 'Edad en días (MID)' in df.columns:
        # Calcular promedio solo si hay dos columnas de edad
        df['Edad (días)'] = (df[['Edad en días (ADNI)', 'Edad en días (MID)']].mean(axis=1)).round().astype(int)
    else:
        # Si solo hay una columna, usarla directamente
        df['Edad (días)'] = df['Edad en días (ADNI/MID)']
    return df

df_control = calcular_edad_promedio(df_control)
df_alcohol['Edad (días)'] = df_alcohol['Edad en días (ADNI/MID)']  # Alcohol usa un solo valor

# --- PASO 2: Función para calcular p-valores (igual que antes) ---
def calculate_pvalues(df_control, df_alcohol, center=None):
    if center:
        df_control = df_control[df_control["center"] == center]
        df_alcohol = df_alcohol[df_alcohol["center"] == center]
    
    _, p_sex = chi2_contingency(pd.crosstab(
        pd.concat([df_control["sex"], df_alcohol["sex"]]),
        pd.concat([pd.Series(["Control"]*len(df_control)), pd.Series(["Alcohol"]*len(df_alcohol))]))[1]
    
    _, p_age = ttest_ind(df_control["Edad (días)"], df_alcohol["Edad (días)"])
    _, p_audit_child = ttest_ind(df_control["audit child"], df_alcohol["audit child"])
    _, p_audit_fu3 = ttest_ind(df_control["audit FU3"], df_alcohol["audit FU3"])
    
    return {
        "p_sex": round(p_sex, 2),
        "p_age": round(p_age, 2),
        "p_audit_child": round(p_audit_child, 2),
        "p_audit_fu3": f"{p_audit_fu3:.3f}" if p_audit_fu3 < 0.001 else round(p_audit_fu3, 2)
    }

# --- PASO 3: Generar tabla por centro ---
centros = ["DRESDEN", "DUBLIN", "BERLIN", "NOTTINGHAM", "MANNHEIM", "LONDON", "HAMBURG", "PARIS"]
tabla = []

for centro in centros:
    control_center = df_control[df_control["center"] == centro]
    alcohol_center = df_alcohol[df_alcohol["center"] == centro]
    
    n_control = len(control_center)
    n_alcohol = len(alcohol_center)
    
    stats = {
        "Hombres (Control)": f"{sum(control_center['sex'] == 'Male')} ({sum(control_center['sex'] == 'Male') / n_control * 100:.0f}%)",
        "Mujeres (Control)": f"{sum(control_center['sex'] == 'Female')} ({sum(control_center['sex'] == 'Female') / n_control * 100:.0f}%)",
        "Hombres (Alcohol)": f"{sum(alcohol_center['sex'] == 'Male')} ({sum(alcohol_center['sex'] == 'Male') / n_alcohol * 100:.0f}%)",
        "Mujeres (Alcohol)": f"{sum(alcohol_center['sex'] == 'Female')} ({sum(alcohol_center['sex'] == 'Female') / n_alcohol * 100:.0f}%)",
        "Edad (Control)": f"{control_center['Edad (días)'].mean():.0f} ± {control_center['Edad (días)'].std():.0f}",
        "Edad (Alcohol)": f"{alcohol_center['Edad (días)'].mean():.0f} ± {alcohol_center['Edad (días)'].std():.0f}",
        "AUDIT Child (Control)": f"{control_center['audit child'].mean():.1f} ± {control_center['audit child'].std():.1f}",
        "AUDIT Child (Alcohol)": f"{alcohol_center['audit child'].mean():.1f} ± {alcohol_center['audit child'].std():.1f}",
        "AUDIT FU3 (Control)": f"{control_center['audit FU3'].mean():.1f} ± {control_center['audit FU3'].std():.1f}",
        "AUDIT FU3 (Alcohol)": f"{alcohol_center['audit FU3'].mean():.1f} ± {alcohol_center['audit FU3'].std():.1f}",
    }
    
    pvals = calculate_pvalues(control_center, alcohol_center)
    
    tabla.extend([
        {"Centro": centro, "Variable": "Sexo, Hombres", "Control": stats["Hombres (Control)"], "Alcohol": stats["Hombres (Alcohol)"], "p-valor": ""},
        {"Centro": centro, "Variable": "Sexo, Mujeres", "Control": stats["Mujeres (Control)"], "Alcohol": stats["Mujeres (Alcohol)"], "p-valor": pvals["p_sex"]},
        {"Centro": centro, "Variable": "Edad (días)", "Control": stats["Edad (Control)"], "Alcohol": stats["Edad (Alcohol)"], "p-valor": pvals["p_age"]},
        {"Centro": centro, "Variable": "AUDIT Child", "Control": stats["AUDIT Child (Control)"], "Alcohol": stats["AUDIT Child (Alcohol)"], "p-valor": pvals["p_audit_child"]},
        {"Centro": centro, "Variable": "AUDIT FU3", "Control": stats["AUDIT FU3 (Control)"], "Alcohol": stats["AUDIT FU3 (Alcohol)"], "p-valor": pvals["p_audit_fu3"]}
    ])

# Convertir a DataFrame y mostrar
df_tabla = pd.DataFrame(tabla)
print(tabulate(df_tabla, headers="keys", tablefmt="grid", showindex=False))

# Exportar a Excel/LaTeX
df_tabla.to_excel("tabla_final.xlsx", index=False)
df_tabla.to_latex("tabla_final.tex", index=False)