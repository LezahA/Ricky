import os
import sys
import json

CONFIG_GLOBAL = {}

def cargarConfig():
    global CONFIG_GLOBAL
    # Cargar el archivo de configuracion config.json
    config_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(config_dir, "config.json")
    # Verificar si el archivo de configuracion existe
    if not os.path.exists(config_path):
        print(f"config.json no encontrado :/")
        return False
    # Cargar el archivo de configuracion
    with open(config_path, 'r') as f:
        datos = json.load(f)
        CONFIG_GLOBAL.clear()
        CONFIG_GLOBAL.update(datos)
        print("Config OK! :)")
    return True

# Funcion para obtener un valor de la configuracion (config.json)
def getConfig(key, default=None):
    return CONFIG_GLOBAL.get(key, default)