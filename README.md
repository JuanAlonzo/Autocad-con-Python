# Herramientas de Automatización para AutoCAD

Este repositorio contiene una colección de scripts en Python desarrollados para automatizar tareas en AutoCAD utilizando la biblioteca `pyautocad`.
Las herramientas fueron diseñadas para facilitar la gestión de capas, numeración de elementos, extracción de información y dibujo automático en planos de ingeniería.

## Estructura del Proyecto

El proyecto está organizado en los siguientes directorios:

### 📂 drawing

Scripts para automatizar el dibujo de elementos en AutoCAD:

- `drawCircleNumber.py`: Dibuja círculos numerados en coordenadas específicas.
- `drawLine.py`: Crea líneas entre coordenadas especificadas.

### 📂 getData

Herramientas para extraer información de dibujos existentes:

- `getLayerbyNumber.py`: Asocia elementos de una capa con números de otra capa.
- `getName.py`: Obtiene el nombre del dibujo activo en AutoCAD.
- `getTextandCoord.py`: Extrae texto y coordenadas de elementos seleccionados.
- `numeracion_por_lineas.py`: Numera bloques siguiendo diferentes criterios de ordenamiento.

### 📂 layers

Funciones para gestionar capas en AutoCAD:

- `createLayer.py`: Crea nuevas capas con colores específicos.
- `deleteLayer.py`: Elimina capas no utilizadas.
- `listLayers.py`: Lista todas las capas existentes en el dibujo.

## Scripts Principales

### numeracionxTrayectoOptimized.py

Script optimizado de `numeracion_por_lineas.py` que permite numerar bloques de AutoCAD (como postes) siguiendo diferentes criterios:

- Ordenación por coordenada X o Y
- Ordenación por distancia desde un punto de referencia
- Ruta óptima usando algoritmo de "vecino más cercano"
- Seguimiento de un trayecto definido por líneas

### getLayerOptimized.py

Versión optimizada de `getLayerbyNumber.py` para extraer elementos de capas específicas y asociarlos con números de otra capa, utilizando un enfoque modular y funciones reutilizables.

## Requisitos

- AutoCAD instalado
- Python 3.6 o superior
- Biblioteca `pyautocad` (`pip install pyautocad`)

## Uso

1. Clone este repositorio o descargue los scripts necesarios
2. Asegúrese de tener AutoCAD abierto con un dibujo activo
3. Ejecute el script deseado desde la línea de comandos: `python nombre_script.py`
4. Siga las instrucciones en pantalla para interactuar con el script

## Características

- Interfaz de línea de comandos sencilla e intuitiva
- Validación de capas y elementos
- Manejo de errores robusto
- Visualización clara de resultados
- Algoritmos optimizados para procesamiento eficiente

## Notas

Estos scripts están diseñados para ser utilizados por profesionales familiarizados con AutoCAD en entornos de ingeniería y diseño técnico.
