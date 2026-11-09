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
            
            # 1. Limpiar el nombre del hospital (quitar "Sucursal X")
            if 'Hospital_Nombre' in df.columns:
                df['Hospital_Nombre'] = df['Hospital_Nombre'].apply(limpiar_nombre_hospital)
            
            # 2. Limpiar duplicados INTERNOS de este archivo específico (adiós a la basura repetida de origen)
            df_limpio = df.drop_duplicates(keep='first')
            
            print(f"✅ CARGADO Y LIMPIO: {archivo} (Original: {len(df)} | Sin duplicados internos: {len(df_limpio)})")
            dfs.append(df_limpio)
            
        except Exception as e:
            print(f"⚠️ NO ENCONTRADO O ERROR en {archivo}: {e}")
            
    if not dfs:
        raise ValueError("No se pudieron cargar los archivos base.")
        
    # Consolidar todas las aseguradoras ya limpias individualmente
    df_maestro = pd.concat(dfs, ignore_index=True)
    
    print(f"🎯 Total final consolidado nacional sin duplicados basura: {len(df_maestro)} registros.")
    
    # Exportar archivo maestro definitivo a la raíz
    df_maestro.to_csv('insureza_base_maestra_nacional.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    procesar_pipeline()
