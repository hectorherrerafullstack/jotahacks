#!/usr/bin/env python
"""
Script para procesar y ofuscar archivos JavaScript en producción.
Este script automatiza la ofuscación y minificación de código JavaScript.
"""

import os
import subprocess
import shutil
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Directorios de JavaScript
JS_SRC_DIR = BASE_DIR / 'static' / 'js'
JS_OBFUSCATED_DIR = BASE_DIR / 'static' / 'js' / 'obfuscated'

def create_directories():
    """Asegura que los directorios necesarios existan."""
    os.makedirs(JS_OBFUSCATED_DIR, exist_ok=True)

def install_dependencies():
    """Instala las dependencias necesarias de Node.js."""
    print("Instalando dependencias...")
    subprocess.run(['npm', 'install'], check=True)

def build_and_obfuscate():
    """Construye y ofusca los archivos JavaScript."""
    print("Construyendo y ofuscando archivos JavaScript...")
    subprocess.run(['npm', 'run', 'build:prod'], check=True)

def update_templates():
    """
    Actualiza las plantillas para usar archivos ofuscados en producción.
    Esta función asume que estás en un entorno de producción.
    """
    # Copia los archivos ofuscados a la ubicación de producción
    for js_file in JS_OBFUSCATED_DIR.glob('*.js'):
        target_file = JS_SRC_DIR / js_file.name
        print(f"Copiando {js_file} a {target_file}")
        shutil.copy2(js_file, target_file)

def main():
    """Función principal que ejecuta todo el proceso."""
    print("=== Iniciando procesamiento de archivos JavaScript ===")
    
    create_directories()
    install_dependencies()
    build_and_obfuscate()
    update_templates()
    
    print("=== Procesamiento completado con éxito ===")

if __name__ == '__main__':
    main()