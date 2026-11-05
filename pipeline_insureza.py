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
    
    # TRUCO DE INGENIERÍA: Rellenar temporalmente las direcciones vacías con un ID único por fila
    # para que Pandas no fusione erróneamente los hospitales sin dirección registrada.
    if 'Direccion' in df_maestro.columns:
        df_maestro['Direccion_Clean'] = df_maestro['Direccion'].fillna('').astype(str).str.strip()
        mask_vacios = df_maestro['Direccion_Clean'] == ''
        df_maestro.loc[mask_vacios, 'Direccion_Clean'] = 'SIN_DIR_' + df_maestro.index.astype(str)
    else:
        df_maestro['Direccion_Clean'] = 'SIN_DIR_' + df_maestro.index.astype(str)

    # Desduplicación segura utilizando la dirección limpia
    columnas_seguras = ['Hospital_Nombre', 'Direccion_Clean', 'Aseguradora']
    columnas_existentes = [col for col in columnas_seguras if col in df_maestro.columns]
    
    df_maestro = df_maestro.drop_duplicates(subset=columnas_existentes, keep='first')
    
    # Eliminar la columna temporal antes de exportar
    df_maestro = df_maestro.drop(columns=['Direccion_Clean'])

    print(f"🎯 Total final consolidado, limpio y protegido: {len(df_maestro)} registros.")
    
    # Exportar archivo limpio a la raíz
    df_maestro.to_csv('insureza_base_maestra_nacional.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    procesar_pipeline()
