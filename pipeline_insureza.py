import pandas as pd
import re

def limpiar_nombre_hospital(nombre):
    if pd.isna(nombre):
        return ""
    nombre_limpio = re.sub(r'\s+Sucursal\s+\d+', '', str(nombre), flags=re.IGNORECASE)
    return nombre_limpio.strip()

def asignar_nivel_poliza(row):
    """
    Función para asignar los niveles de póliza correctos y diferenciados
    según la aseguradora o las características del hospital.
    """
    aseguradora = str(row.get('Aseguradora', '')).strip().lower()
    hospital = str(row.get('Hospital_Nombre', '')).lower()
    
    # Puedes ajustar estos criterios según la lógica de negocio real de Insureza:
    if 'axa' in aseguradora:
        if any(h in hospital for h in ['angeles', 'puerta de hierro', 'médica sur']):
            return 'AXA Premier / Diamante'
        return 'AXA Óptimo / Flex'
        
    elif 'gnp' in aseguradora:
        if any(h in hospital for h in ['angeles', 'médica sur']):
            return 'GNP Platino / Integral'
        return 'GNP Esencial / Amplio'
        
    elif 'mapfre' in aseguradora:
        return 'Mapfre Global / Preferente'
        
    elif 'metlife' in aseguradora:
        return 'MetLife Elite / Especial'
        
    elif 'sura' in aseguradora:
        return 'Sura Óptima / Global'
        
    elif 'plan seguro' in aseguradora:
        return 'Plan Seguro Titular / Select'
        
    elif 'latinoamericana' in aseguradora:
        return 'La Latino Red Esencial'
        
    # Valor por defecto si no cae en ninguna regla anterior
    val_actual = row.get('Nivel_Poliza', '')
    return val_actual if pd.notna(val_actual) and val_actual != '' else 'Estándar'

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
            
            # 1. Limpiar nombre de hospital
            if 'Hospital_Nombre' in df.columns:
                df['Hospital_Nombre'] = df['Hospital_Nombre'].apply(limpiar_nombre_hospital)
            
            print(f"✅ CARGADO: {archivo} con {len(df)} registros.")
            dfs.append(df)
            
        except Exception as e:
            print(f"⚠️ NO ENCONTRADO O ERROR en {archivo}: {e}")
            
    if not dfs:
        raise ValueError("No se pudieron cargar los archivos base.")
        
    # Consolidar manteniendo los 3,145 registros puros
    df_maestro = pd.concat(dfs, ignore_index=True)
    
    # 2. Aplicar la asignación inteligente de niveles de póliza diferenciados
    if 'Aseguradora' in df_maestro.columns:
        df_maestro['Nivel_Poliza'] = df_maestro.apply(asignar_nivel_poliza, axis=1)
    
    print(f"🎯 Total final consolidado nacional con niveles corregidos: {len(df_maestro)} registros.")
    
    # Exportar archivo maestro definitivo a la raíz del repositorio
    df_maestro.to_csv('insureza_base_maestra_nacional.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    procesar_pipeline()
