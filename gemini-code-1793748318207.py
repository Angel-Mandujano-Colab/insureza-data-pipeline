import os
import pandas as pd
from datetime import datetime

def ejecutar_pipeline_insureza():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando Pipeline de Actualización Automática - Insureza...")
    
    # Mapeo de catálogos individuales por aseguradora
    archivos_aseguradoras = {
        'AXA': 'insureza_red_axa_definitivo.csv',
        'Mapfre': 'insureza_red_mapfre_definitivo.csv',
        'La Latinoamericana Seguros': 'insureza_red_latino_definitivo.csv',
        'Plan Seguro': 'insureza_red_planseguro_definitivo.csv',
        'GNP': 'insureza_red_gnp_definitivo.csv',
        'MetLife': 'insureza_red_metlife_definitivo.csv',
        'Sura': 'insureza_red_sura_definitivo.csv'
    }
    
    dfs_consolidados = []
    
    for aseguradora, ruta_csv in archivos_aseguradoras.items():
        if os.path.exists(ruta_csv):
            try:
                df = pd.read_csv(ruta_csv)
                # Validar y asegurar estrictamente las 6 columnas del estándar Insureza
                columnas_necesarias = ['Hospital_Nombre', 'Estado_Ciudad', 'Nivel_Poliza', 'Direccion', 'Telefono']
                for col in columnas_necesarias:
                    if col not in df.columns:
                        df[col] = 'No especificado'
                
                df = df[columnas_necesarias]
                df['Aseguradora'] = aseguradora
                dfs_consolidados.append(df)
                print(f" ✔ {aseguradora}: {len(df)} registros procesados e integrados.")
            except Exception as e:
                print(f" ✖ Error procesando el archivo de {aseguradora}: {e}")
        else:
            print(f" ⚠ Advertencia: No se encontró el archivo '{ruta_csv}' para {aseguradora}.")

    if not dfs_consolidados:
        print(" Error crítico: No se encontraron datasets para procesar. Abortando pipeline.")
        return

    # Consolidación final y control de duplicados
    df_maestro = pd.concat(dfs_consolidados, ignore_index=True)
    df_maestro.drop_duplicates(subset=['Hospital_Nombre', 'Aseguradora', 'Estado_Ciudad'], inplace=True)
    
    # Sobrescribir la base maestra nacional
    archivo_salida = 'insureza_base_maestra_nacional.csv'
    df_maestro.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
    
    print(f"\n Pipeline ejecutado exitosamente.")
    print(f" Total de registros en la Base Maestra: {len(df_maestro)}")
    print(f" Archivo actualizado: {os.path.abspath(archivo_salida)}")

if __name__ == "__main__":
    ejecutar_pipeline_insureza()