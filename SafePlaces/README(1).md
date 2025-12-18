# Proyecto de Análisis de Seguridad Urbana con K-Means y Mapa Interactivo en Tiempo Real

## Planteamiento del problema

La seguridad urbana es un factor clave para la calidad de vida de los ciudadanos. Sin embargo, analizar grandes volúmenes de datos relacionados con iluminación, comercios, reportes de incidentes y flujo de personas puede resultar complejo sin herramientas adecuadas y actualizadas.

Inicialmente, la recolección de datos se realizaba mediante encuestas estáticas, lo que limitaba la actualización de la información y la visualización en tiempo real. Por ello, este proyecto propone una solución dinámica basada en formularios y bases de datos en línea, combinada con técnicas de análisis de datos y Machine Learning, para identificar patrones de seguridad urbana y visualizarlos de manera interactiva y en tiempo real.

## Objetivos del proyecto

### Objetivo general
Analizar y clasificar zonas urbanas según sus características de seguridad utilizando el algoritmo K-Means y representar los resultados en un mapa interactivo accesible en tiempo real mediante una página web.

### Objetivos específicos
- Diseñar un sistema de recolección de datos en línea mediante formularios digitales.
- Almacenar la información recolectada en una base de datos en línea centralizada.
- Limpiar y estandarizar los datos automáticamente desde la fuente en tiempo real.
- Convertir variables cualitativas y cuantitativas a formato numérico.
- Agrupar zonas con características similares mediante Machine Learning no supervisado.
- Visualizar los clústeres obtenidos en un mapa interactivo accesible mediante un enlace web.
- Facilitar la interpretación visual del nivel de seguridad de cada zona en tiempo real.

## Descripción general del proyecto

Este proyecto permite analizar datos de seguridad urbana, agrupar zonas según sus características usando el algoritmo K-Means y visualizar los resultados en un mapa interactivo generado con la librería Folium.

La información se recolecta mediante un formulario de Google Forms, el cual se encuentra vinculado directamente a una hoja de cálculo de Google Sheets que actúa como base de datos en línea. El código del proyecto accede a esta base de datos mediante su URL pública, permitiendo que los datos se procesen y visualicen en tiempo real.

Al ejecutar el código, se genera automáticamente una **página HTML** que muestra el mapa interactivo. El enlace a esta página es proporcionado directamente en la ejecución del programa, permitiendo que cualquier usuario con acceso al enlace pueda visualizar el mapa actualizado sin necesidad de abrir archivos locales.

## Actualizaciones implementadas

Las principales actualizaciones realizadas al proyecto son las siguientes:

- Migración de la encuesta de recolección de datos desde **Microsoft Forms** a **Google Forms**.
- Vinculación directa del formulario a una base de datos en **Google Sheets en línea**.
- Implementación de la URL de la base de datos en el código Python.
- Procesamiento y análisis de datos en tiempo real.
- Generación dinámica de una página web con el mapa interactivo.
- Provisión automática de un enlace web al ejecutar el código.
- Acceso compartido al mapa en tiempo real para múltiples usuarios.

### Enlaces importantes

- **Formulario de recolección de datos (Google Forms):**  
  https://docs.google.com/forms/d/e/1FAIpQLSceGv1--VtlYTcpldOoufFSPRnrcdC9RqNfdgIu2h5Q6_lRog/viewform?usp=dialog

- **Base de datos en línea (Google Sheets):**  
  https://docs.google.com/spreadsheets/d/1cv1MLZeoHwdx3ijp0Sy6Jiu6P4M1W6FZrwpe4dfF7Ao/edit?usp=sharing

## Características principales

- ✔ Recolección de datos en línea mediante Google Forms  
- ✔ Base de datos centralizada en Google Sheets  
- ✔ Acceso a datos en tiempo real mediante URL pública  
- ✔ Limpieza y estandarización automática del dataset  
- ✔ Conversión de datos a formato numérico  
- ✔ Clasificación automática de zonas usando K-Means  
- ✔ Generación dinámica de una página HTML con el mapa  
- ✔ Enlace al mapa proporcionado al ejecutar el código  
- ✔ Actualización del mapa en tiempo real  
- ✔ Acceso compartido al mapa mediante un link web  
- ✔ Código desarrollado en Python, fácil de modificar o ampliar  

## ¿El proyecto utiliza Inteligencia Artificial?

Sí. El proyecto emplea un algoritmo de Machine Learning no supervisado llamado **K-Means**, el cual permite agrupar zonas urbanas según similitudes en variables como:

- Nivel de iluminación  
- Cantidad de comercios  
- Número de reportes de incidentes  
- Flujo de personas  
- Distancia al punto policial más cercano  

El sistema no predice eventos futuros, sino que **identifica patrones y clasifica zonas** de acuerdo con su nivel de similitud o riesgo relativo, utilizando datos actualizados en tiempo real.

## Estructura del proyecto

Proyecto-Seguridad/
│
├── main.py # Código principal del análisis en tiempo real
└── README.md # Documentación del proyecto


> La visualización del mapa no depende de un archivo HTML local, sino de una página web generada dinámicamente cuyo enlace se proporciona al ejecutar el código.

## Tecnologías y herramientas utilizadas

- **Python**: lenguaje principal del proyecto  
- **Pandas**: carga, limpieza y procesamiento de datos en tiempo real  
- **Scikit-learn**: implementación del algoritmo K-Means  
- **Folium**: creación de mapas interactivos  
- **MarkerCluster**: agrupación visual de marcadores  
- **Google Forms**: recolección de datos  
- **Google Sheets**: base de datos en línea  

## Interpretación de colores del mapa

| Clúster | Color      | Interpretación aproximada                  |
|--------:|------------|--------------------------------------------|
| 0       | 🟢 Verde   | Zonas con mejores indicadores de seguridad |
| 1       | 🟠 Naranja | Zonas intermedias o mixtas                  |
| 2       | 🔴 Rojo    | Zonas con mayor riesgo relativo            |

## Resultado final del proyecto

Como resultado, el proyecto genera una **página web interactiva en tiempo real**, cuyo enlace se proporciona directamente al ejecutar el código. Esta página presenta:

- Visualización geográfica dinámica
- Actualización automática al ingresar nuevos datos
- Clasificación por colores según el clúster asignado
- Información detallada de cada punto mediante ventanas emergentes (popups)
- Navegación intuitiva similar a Google Maps (zoom, desplazamiento)

Este enfoque permite analizar de manera visual, colaborativa y en tiempo real la distribución de la seguridad urbana en distintas zonas.

