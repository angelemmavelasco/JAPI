"""
Añade aquí tus funciones de utilidad que pueden ser utilizadas en diferentes partes del proyecto.

Antes de agregar una función, asegúrate de que no exista ya en este archivo o en otro módulo de utilidades. Esto ayudará a mantener el código limpio y organizado.
"""
from datetime import datetime
import pandas as pd
import glob
import openpyxl

import sys
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import config.settings as settings



def get_current_timestamp(timer=True):
    """
    Devuelve la marca de tiempo actual en formato legible.
    Si el timer es True, también incluye la hora. De lo contrario, solo devuelve la fecha.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") if timer else datetime.now().strftime("%Y-%m-%d")

def list_files_in_directory(directory) -> list:
    """
    Devuelve una lista de archivos en el directorio especificado.
    """
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def load_and_concatenate_data(*, pattern="*.xlsx", format='.xlsx', directory=None):
    """
    Consolida archivos de formato .csv o .xlsx. 
    Soporta Path objects y evita errores de strings en rutas.
    """
    
    if directory is None:
        directory = settings.DATA_DIR
    else:
        directory = Path(directory)

    search_path = str(directory / pattern)
    files = glob.glob(search_path)
    files.sort()
    
    if not files:
        print(f"No se encontraron archivos con el patrón '{pattern}' en: {directory}")
        return None

    all_data = []

    for file in files:
        try:
            if format == '.csv':
                df_temp = pd.read_csv(file)
            else:
                df_temp = pd.read_excel(file)

            if not df_temp.empty:
                df_temp['source_file'] = Path(file).name
                all_data.append(df_temp)
        except Exception as e:
            print(f"Error al leer {file}: {e}")
    
    if not all_data:
        return None

    df_final = pd.concat(all_data, ignore_index=True)
    
    print(f"Consolidación completada. Registros totales: {len(df_final)}")
    return df_final