# Herramientas de Automatización para AutoCAD

Este repositorio contiene una colección de scripts en Python desarrollados para automatizar tareas en AutoCAD utilizando la biblioteca `pyautocad`.
Las herramientas fueron diseñadas para facilitar la gestión de capas, numeración de elementos, extracción de información y dibujo automático en planos de ingeniería.

## Estructura del Proyecto

El proyecto está organizado en los siguientes directorios:

### 📂 getData

Herramientas para extraer información de dibujos existentes:

- `getLayerbyNumber.py`: Asocia elementos de una capa con números de otra capa.
- `getName.py`: Obtiene el nombre del dibujo activo en AutoCAD.
- `getTextandCoord.py`: Extrae texto y coordenadas de elementos seleccionados.
- `numeracion_por_lineas.py`: Numera bloques siguiendo diferentes criterios de ordenamiento.

### 📂 layers

Funciones para gestionar capas en AutoCAD:

- `layersCreate.py`: Crea nuevas capas con colores específicos.
- `layersDelete.py`: Elimina capas que no estes utilizando.
- `layersList.py`: Lista las capas existentes tanto en uso como las que no en el dibujo.

### 📂 utilities

Aqui se almacenan la mayoria de funciones que se encuentran en los principales scripts.

- `acad_common.py`: Funciones como inicializar, obtener datos o validar entradas.
- `acad_layers.py`: Todo lo relacionado con los scripts para manipular layers del dibujo.

## Scripts Principales

### numeracionxTrayectoOptimized.py

Script optimizado de `numeraciondeBloques.py` que permite numerar bloques de AutoCAD (como postes) siguiendo diferentes criterios:

- Ordenación por coordenada X o Y
- Ordenación por distancia desde un punto de referencia
- Ruta óptima usando algoritmo de "vecino más cercano"
- Seguimiento de un trayecto definido por líneas

### getLayerOptimized.py

Versión optimizada de `obtenerCapaSegunNumeracion.py` para extraer elementos de capas específicas y asociarlos con números de otra capa, utilizando un enfoque modular y funciones reutilizables.

## Requisitos

- AutoCAD instalado
- Python 3.6 o superior
- Bibliotecas en archivo `requirements.txt` (`pip install **`)

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
