import pandas as pd
import re

def limpiar_nombre_hospital(nombre):
    if pd.isna(nombre):
        return ""
    nombre_limpio = re.sub(r'\s+Sucursal\s+\ద+', '', str(nombre), flags=re.IGNORECASE)
    # Corrección de expresión regular segura para sufijos 'Sucursal X'
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
        
    # Consolidar todas las aseguradoras
    df_maestro = pd.concat(dfs, ignore_index=True)
    print(f"📊 Total combinado bruto: {len(df_maestro)} registros.")
    
    # Normalizar textos clave
    for col in ['Hospital_Nombre', 'Aseguradora']:
        if col in df_maestro.columns:
            df_maestro[col] = df_maestro[col].fillna('').astype(str).str.strip()

    # TRUCO DE ORO: Aislar filas con nombres vacíos para que Pandas NUNCA las borre en masa
    df_maestro['Hospital_Control'] = df_maestro['Hospital_Nombre']
    mask_vacios = df_maestro['Hospital_Control'] == ''
    df_maestro.loc[mask_vacios, 'Hospital_Control'] = 'HOSP_VACIO_' + df_maestro.index.astype(str)

    # Desduplicación quirúrgica: limpia duplicados reales por hospital y aseguradora sin tocar los vacíos
    df_maestro = df_maestro.drop_duplicates(subset=['Hospital_Control', 'Aseguradora'], keep='first')
    
    # Eliminar columna temporal de control
    df_maestro = df_maestro.drop(columns=['Hospital_Control'])
    
    print(f"🎯 Total final limpio y protegido: {len(df_maestro)} registros.")
    
    # Exportar archivo definitivo a la raíz
    df_maestro.to_csv('insureza_base_maestra_nacional.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    procesar_pipeline()
