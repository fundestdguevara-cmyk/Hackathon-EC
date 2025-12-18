SISTEMA DE MONITOREO BIOMETRICO Y REGISTRO DE EVENTOS - SISTEMA DE DETECCION DE SOMNOLENCIA

ESPECIFICACIONES DEL SISTEMA El proyecto implementa una arquitectura de inspección ocular y postural mediante redes neuronales convolucionales ligeras. El objetivo es la mitigación de riesgos operativos en la conducción mediante el análisis de fatiga y la gestion de un registro forense de incidentes en tiempo real.

ARQUITECTURA TECNICA El sistema opera bajo cuatro pilares de procesamiento asíncrono:

Extracción de Características: Utiliza una malla facial de 468 puntos de referencia para obtener la geometría del rostro en tres dimensiones.

Análisis de Estados: Implementa algoritmos de clasificación para determinar la relación de aspecto ocular y la orientación de los ejes de la cabeza (Pitch, Yaw, Roll).

Modulo Forense (Caja Negra): Sistema de persistencia de datos que captura el estado del buffer de video al momento de una detección positiva, almacenando metadatos técnicos y telemetría.

Geolocalización por Red: Obtención de coordenadas geográficas mediante triangulación de red para el etiquetado de reportes de seguridad.

COMPONENTES DE SOFTWARE

Motor de Vision: MediaPipe Face Mesh para el seguimiento de alta fidelidad con bajo consumo de CPU.

Logica de Clasificación: Scikit-learn (SVM) para la adaptación del umbral de parpadeo según la fisionomía del usuario.

Procesamiento de Imagen: OpenCV para la manipulación de matrices de pixeles y visualización de telemetría en tiempo real.

Interfaz de Red: Protocolos HTTP para la captura de geoposicionamiento.

REQUISITOS DE INSTALACION El entorno requiere Python 3.10 y las siguientes dependencias base:

opencv-python

mediapipe

numpy

scikit-learn

scipy

requests

PARAMETROS DE OPERACION Y UMBRALES

EAR (Eye Aspect Ratio): Valor de referencia para la apertura ocular.

Persistencia Temporal: Limite de fotogramas consecutivos para la validación de perdida de alerta.

Head Pose Estimation: Ángulos de desviación cervical para detección de cabeceo.

Logging: Formato de salida en archivos de texto plano y captura de imágenes en formato JPG.

ESTRUCTURA DE ARCHIVOS

/main.py: Punto de entrada y gestion del ciclo principal de captura.

/models: Scripts de calibración y modelos entrenados.

/blackbox: Directorio de almacenamiento de evidencias y logs de incidentes.

/utils: Funciones de calculo geométrico y peticiones de geolocalización.

PROCEDIMIENTO DE EJECUCION

Inicializar el entorno virtual.

Ejecutar la fase de calibración para establecer la línea base del conductor.

Iniciar el script principal para el monitoreo activo y la generación de registros.
