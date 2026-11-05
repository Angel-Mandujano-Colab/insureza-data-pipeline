import pandas as pd
import re

def limpiar_nombre_hospital(nombre):
    if pd.isna(nombre):
        return ""
    nombre_limpio = re.sub(r'\s+Sucursal\s+\d+', '', str(nombre), flags=re.IGNORECASE)
    return nombre_limpio.strip()

def procesar_pipeline():
    archivos = [
        'insureza_red_axa_definitivo.csv',
        'insureza_red_gnp_definitivo.csv',
        'insureza_red_la_latinoamericana_seguros_definitivo.csv',
        'insureza_red_mapfre_definitivo.csv',
        'insureza_red_metlife_definitivo.csv',
        'insureza_red_plan_seguro_definitivo.csv',
        'insureza_red_sura_definitivo.csv'
    ]
    
    dfs = []
    
    for archivo in archivos:
        try:
            df = pd.read_csv(archivo)
            print(f"✅ CARGADO: {archivo} con {len(df)} registros.")
            dfs.append(df)
        except Exception as e:
            print(f"⚠️ NO ENCONTRADO O ERROR en {archivo}: {e}")
            
    if not dfs:
        raise ValueError("No se pudieron cargar los archivos base.")
        
    # Consolidar todas las aseguradoras
    df_maestro = pd.concat(dfs, ignore_index=True)
    print(f"📊 Total combinado de todas las aseguradoras: {len(df_maestro)} registros.")
    
    # 1. Limpiar nombres de hospitales
    if 'Hospital_Nombre' in df_maestro.columns:
        df_maestro['Hospital_Nombre'] = df_maestro['Hospital_Nombre'].apply(limpiar_nombre_hospital)
        
    # 2. Rellenar nulos para evitar colapsos
    for col in ['Hospital_Nombre', 'Direccion', 'Aseguradora']:
        if col in df_maestro.columns:
            df_maestro[col] = df_maestro[col].fillna('').astype(str).str.strip()

    # 3. Desduplicar
    columnas_clave = ['Hospital_Nombre', 'Direccion', 'Aseguradora']
    columnas_existentes = [col for col in columnas_clave if col in df_maestro.columns]
    
    df_maestro = df_maestro.drop_duplicates(subset=columnas_existentes, keep='first')
    print(f"🎯 Total final tras limpieza y desduplicación: {len(df_maestro)} registros.")
    
    # Exportar archivo limpio a la raíz
    df_maestro.to_csv('insureza_base_maestra_nacional.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    procesar_pipeline()
