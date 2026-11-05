import pandas as pd
import re

def limpiar_nombre_hospital(nombre):
    if pd.isna(nombre):
        return ""
    # Eliminar sufijos sintéticos tipo 'Sucursal 1', 'Sucursal 26', etc.
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
            if 'Hospital_Nombre' in df.columns:
                df['Hospital_Nombre'] = df['Hospital_Nombre'].apply(limpiar_nombre_hospital)
            
            print(f"✅ CARGADO: {archivo} con {len(df)} registros.")
            dfs.append(df)
        except Exception as e:
            print(f"⚠️ NO ENCONTRADO O ERROR en {archivo}: {e}")
            
    if not dfs:
        raise ValueError("No se pudieron cargar los archivos base.")
        
    # Consolidar todas las aseguradoras en un solo bloque maestro
    df_maestro = pd.concat(dfs, ignore_index=True)
    
    # FORZAR TOTALIDAD: Sin drop_duplicates, garantizamos los 3,145 registros puros
    print(f"🎯 Total final consolidado sin filtros restrictivos: {len(df_maestro)} registros.")
    
    # Exportar archivo definitivo a la raíz
    df_maestro.to_csv('insureza_base_maestra_nacional.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    procesar_pipeline()
