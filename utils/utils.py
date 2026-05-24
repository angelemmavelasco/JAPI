"""
Añade aquí tus funciones de utilidad que pueden ser utilizadas en diferentes partes del proyecto.

Antes de agregar una función, asegúrate de que no exista ya en este archivo o en otro módulo de utilidades. Esto ayudará a mantener el código limpio y organizado.
"""


from datetime import datetime



def get_current_timestamp(timer=True):
    """
    Devuelve la marca de tiempo actual en formato legible.
    Si el timer es True, también incluye la hora. De lo contrario, solo devuelve la fecha.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") if timer else datetime.now().strftime("%Y-%m-%d")

def parse_date(date_input):
    """parses a YYYY-MM-DD string into a date object, or returns it if already a date object."""
    if isinstance(date_input, str):
        return datetime.strptime(date_input, '%Y-%m-%d').date()
    return date_input