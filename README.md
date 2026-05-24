# Modelos estadísticos clásicos y de Deep Learning para proyección de ventas diarias

El entorno competitivo actual en el sector comercial exige que las organizaciones adopten enfoques analíticos avanzados
para optimizar la toma de decisiones estratégicas, particularmente en la gestión de inventarios y la planificación financiera.

En este contexto se sitúa Urvet de México, una organización dedicada a la distribución mayorista de productos farmacéuticos,
biológicos, alimenticios y accesorios especializados para el sector veterinario y de la salud animal.
Su operación comercial abarca una compleja red de suministro que atiende a clínicas, hospitales veterinarios y centros de distribución minoristas.
Esta dinámica comercial genera un flujo constante de datos transaccionales con un alto potencial de explotación para el desarrollo de ventajas competitivas.
Al enfrentarse a un mercado con demandas altamente variables, influenciadas por factores estacionales que afectan
la prevalencia de ciertas condiciones de salud animal, o campañas de abastecimiento clínico, la predictibilidad de sus ingresos se convierte en un pilar operativo crítico.

Este proyecto surge como un esfuerzo integrador de ciencia de datos aplicado a la infraestructura operativa de Urvet,
utilizando sus registros históricos de transacciones comerciales como la fuente primaria de información.

El núcleo técnico de la investigación se centra en la incorporación, entrenamiento y evaluación comparativa de tres arquitecturas
de modelado de series de tiempo de distinta naturaleza: el modelo estadístico lineal SARIMAX, el modelo aditivo basado en curvas de crecimiento Prophet,
y la red neuronal recurrente LSTM (Long Short-Term Memory).

La variable objetivo fundamental para este análisis es la proyección de las ventas netas, definida estrictamente como las ventas totales de la
organización tras deducir los descuentos comerciales y las devoluciones de producto, calculadas antes de la aplicación de cargas impositivas.
Si bien el horizonte de planeación y visualización estratégica se proyectará de manera mensual, el pipeline de datos está diseñado para procesar
la información y generar los pronósticos con una granularidad diaria. Este nivel de detalle analítico permitirá capturar patrones de estacionalidad intra-semanal,
días festivos y efectos de calendario que suelen diluirse en agregaciones macro, sentando las bases para un análisis profundo de la morfología y comportamiento
de los datos que se desglosará en las secciones subsecuentes de este documento.

## Objetivos específicos

* Extracción y Modelado.

    Diseñar e implementar un pipeline eficiente para la extracción, 
    limpieza y agregación de los datos transaccionales de Urvet, garantizando el cálculo preciso de las ventas netas diarias antes de impuestos.

* Tratamiento Estadístico.

    Desarrollar mecanismos automatizados para la identificación y el tratamiento de valores atípicos \textit{outliers}
    y anomalías en las series de tiempo mediante múltiples estrategias de imputación.

* Evaluación Comparativa.

    Evaluar el rendimiento de un modelo estadístico clásico \textit{SARIMAx}, un enfoque de descomposición estructural \textit{Prophet}
    y un modelo de aprendizaje profundo \textit{LSTM} utilizando métricas de error estandarizadas.

* Optimización Computacional.

    Analizar la complejidad algorítmica y el costo computacional de cada arquitectura
    para asegurar la viabilidad y escalabilidad del sistema en un entorno de producción.

## Stack
- Modelos Estadísticos Clásicos: Statsmodels y Prophet.
- Deep Learning: tensorflow.
- Data: Pandas, Sklearn, numpy.

## Metodología
El desarrollo del Proyecto JAPI se fundamentó en un enfoque metodológico de arquitectura modularizada,
diseñado bajo principios de alta cohesión y bajo acoplamiento.

Esta estructura no solo garantiza la escalabilidad del sistema predictivo, sino que aisla rigurosamente
cada etapa del ciclo de vida del dato, mitigando el riesgo de fuga de información y optimizando
la reproducibilidad de los experimentos. El flujo de trabajo se articuló mediante un pipeline secuencial
y robusto que transiciona orgánicamente desde la ingesta de las fuentes transaccionales crudas de Urvet de México
hasta el despliegue del motor de evaluación comparativa de los modelos.

La arquitectura del sistema se encuentra segmentada en tres grandes módulos interdependientes:

* Adquisición e Ingesta de Datos.
    Capa encargada de la conexión, extracción y modelado de las bases de datos transaccionales.
    Este módulo centraliza las reglas de negocio para la consolidación de la variable objetivo,
    automatizando la extracción de la base de datos central de la empresa, cuidando la integridad de la misma.

* Procesamiento y Tratamiento Estadístico.
    Bloque especializado en el análisis exploratorio y la sanitización de las series temporales.
    A través de componentes orientados a objetos, este módulo computa dinámicamente máscaras lógicas
    vectorizadas para la detección de anomalías y desacopla la lógica de imputación,
    permitiendo al sistema despachar múltiples estrategias de corrección (como interpolaciones lineales o medias móviles vecinas)
    según la morfología del dato.

* Modelado Predictivo y Evaluación.
    Motor analítico donde convergen las arquitecturas SARIMAX, Prophet y LSTM.
    Este módulo administra de manera agnóstica el entrenamiento de los algoritmos y expone
    una interfaz estandarizada para someter los pronósticos a un marco riguroso de validación cruzada
    y métricas de error estadístico, garantizando una comparación simétrica del rendimiento predictivo.


### Arquitectura del Repositorio y Estructura del Proyecto

Para dar soporte al enfoque modular propuesto, el sistema se organizó bajo una estructura de directorios estandarizada que separa las responsabilidades de configuración, experimentación, almacenamiento de artefactos y lógica productiva. A continuación se describe el propósito y contenido de cada componente del repositorio:

#### Capa de configuración y ejecución principal

* *config/*
* *core/*

El directorio de configuración centraliza los parámetros estáticos y las credenciales operativas del sistema, evitando la persistencia de variables rígidas dentro del código fuente. Este espacio gestiona las cadenas de conexión a los servidores de bases de datos y define las variables de entorno necesarias para el despliegue del proyecto. Por otro lado, la sección del núcleo operativo funge como el centro de control de la ejecución, alojando las rutinas principales que importan los módulos reutilizables y coordinan secuencialmente las fases del pipeline completo.

#### Capa de datos y artefactos de modelado

El almacenamiento de información y persistencia de conocimiento se divide en dos repositorios específicos:

* *data/*

    Este espacio está destinado al almacenamiento de las fuentes transaccionales en formatos crudos tales como archivos de valores separados por comas o hojas de cálculo electrónicas, sirviendo además como repositorio para los conjuntos de datos que ya han sido sometidos a los procesos de limpieza y normalización.
* *models/*

    Funciona como un repositorio cerrado para la preservación de los modelos finales entrenados y las definiciones estructurales de datos, resguardando archivos de extensión h5 para la red neuronal recurrente, serializaciones numéricas para el modelo estadístico lineal o formatos de intercambio de datos tipo json para configuraciones específicas de los algoritmos.

#### Entorno de experimentación y desarrollo

La fase de investigación y descubrimiento de insights se aisla por completo de la producción mediante un espacio exclusivo para libretas interactivas *notebooks/*. Este directorio contiene únicamente archivos de extensión ipynb o reportes exportados en lenguaje de marcado de hipertexto que documentan los análisis visuales de tendencias, correlaciones y detección de anomalías. Bajo ninguna circunstancia este módulo provee lógica al flujo productivo del sistema.

#### Capa de lógica reutilizable y utilidades

El motor del proyecto reside en la sección de código fuente denominada *src/*, la cual se subdivide en componentes especializados que encapsulan la lógica interna del sistema:

* *db_conn.py*

    Archivo que implementa de forma exclusiva la clase encargada de gestionar el ciclo de vida de la conexión y las consultas hacia la base de datos de la organización.
* *cleaner.py*

    Componente que agrupa las funciones de transformación y el despacho de algoritmos de corrección estadística una vez validada su funcionalidad operativa.
* *models.py*

    Módulo orientado a objetos cuyas clases administran de manera unificada los procesos de reentrenamiento, optimización de hiperparámetros, evaluación simétrica y generación de predicciones.

#### Capa de resultados

Para mantener la lógica detrás de la estructura modularizada, se implementó un directorio exclusivo para el resguarde de datos predichos.

* *forecast/*

    El tipo de datos almacenados continua con la accesibilidad a través de archivos de formato valores separados por comas, con el objetivo de que sean almacenados de forma fácil y ligera.

Finalmente, el módulo de utilidades *utils/utils.py* centraliza funciones de carácter universal que, por su naturaleza transversal, no pertenecen a una clase de negocio específica, proveyendo herramientas genéricas para la lectura de sistemas de archivos, la asignación estricta de tipos de datos o el formateo de marcas de tiempo.

### Flujo de Ejecución del Modelo Predictivo

#### Alcance Actual del Sistema

Es importante destacar que, por motivos prácticos y de alcance inmediato, el orquestador principal del repositorio actualmente ejecuta de forma exclusiva el modelo estadístico lineal *SARIMAX*. Aunque la capa de persistencia de artefactos (*models/*) y los módulos lógicos están diseñados para albergar múltiples estructuras en el futuro, todo el pipeline actual de extracción, limpieza y generación de variables exógenas está acoplado a la dinámica de este componente predictivo.

La evaluación y entrenamiento de los demás modelos en su análisis completo se encuentran en el *notebooks/model_testing*

---

#### Prerrequisitos para la Ejecución

Antes de iniciar el flujo, el sistema requiere la existencia y correcta configuración de dos elementos esenciales:

* *Variables de entorno* 
    
    Los parámetros de autenticación para la base de datos transaccional y el túnel SSH deben estar definidos en la configuración del sistema para que *DatabaseConnection* pueda inicializarse.
* *Calendario de días no laborables*

    Debe existir el archivo *models/non_business_days/non_business_days.json* con la estructura de festividades anuales, el cual sirve para alimentar la matriz de variables exógenas del modelo.

---

#### Fases del Proceso de Orquestación

El script principal coordina el flujo de datos de extremo a extremo a través de los siguientes pasos secuenciales:

##### Extracción y Almacenamiento Crudo

El sistema abre una conexión segura a la base de datos empleando las credenciales de entorno. Ejecuta una consulta sobre la tabla de transacciones de ventas para extraer las fechas, los precios netos y las rutas, guardando el resultado directamente como un archivo plano en *data/sales.csv* para evitar llamadas redundantes al servidor.

##### Procesamiento y Limpieza Estadística

Utilizando el módulo de utilidades de limpieza, el flujo realiza las siguientes transformaciones sobre los datos en memoria:

* Filtra y remueve las observaciones pertenecientes a rutas de prueba o no deseadas (parámetros solicitados a través de input por terminal).
* Agrupa los montos financieros de manera diaria en función de la fecha de venta para consolidar una serie de tiempo univariada.
* Detecta valores atípicos mediante máscaras lógicas (valores negativos) y los corrige aplicando un método de interpolación lineal o el que el usuario seleccione a través de terminal.
* Segmenta la serie temporal limitando su alcance hasta la fecha de corte de entrenamiento definida.

##### Generación de Matrices Exógenas y Ajuste

El modelo extrae la lista de días festivos del archivo de configuración e interactúa con el generador de características para construir una matriz exógena alineada con las fechas de entrenamiento. El proceso restringe la atención a las señales de fin de mes y zonas de cierre de mes. Con esto, se ejecuta el entrenamiento del algoritmo *SARIMAX*, retornando el objeto ajustado y sus respectivos metadatos de control.

##### Generación de Pronósticos y Persistencia

El sistema proyecta las predicciones utilizando la lógica del modelo para el periodo futuro especificado a través de los argumentos de ejecución. Una vez calculado el pronóstico, la terminal solicita una interacción con el usuario mediante una entrada de texto para definir el nombre del archivo final. Los resultados se guardan de manera estructurada en formato de valores separados por comas dentro del directorio *forecast/*.

#### Ejemplo de ejecución

* Clonar el repo e instalar dependencias

``` bash

# Clonar el repositorio
git clone git@github.com:angelemmavelasco/JAPI.git
cd JAPI

# Activar el entorno virtual
source venv/bin/activate

# Instalar las librerías necesarias
pip install -r requirements.txt

```

* Configurar variables de entorno (opcional)
``` bash
nano .env

```

``` bash
DB_HOST=el_host_de_la_base_de_datos
DB_PASSWORD=contraseña_de_la_base_de_datos
DB_NAME=nombre_de_la_base_de_datos
DB_PORT=puerto_de_acceso_de_la_base
DB_USER=usuario_de_ingreso_a_la_base

SSH_IP=ip_de_instancia_tunel
SSH_PRIVATE_KEY=directorio_de_la_clave_privada
SSH_USERNAME=usuario_de_la_instancia
SSH_PORT=puerto_de_acceso_a_la_instancia


```

* Correr el programa principal

Para iniciar el pipeline de extracción, entrenamiento y pronóstico, ejecuta el script principal desde la raíz del proyecto:

```bash
python core/main.py

```



El programa está diseñado para ser 100% autoguiado. Una vez ejecutado el comando anterior, la terminal interactuará contigo paso a paso. En la mayoría de los casos, puedes simplemente presionar Enter para aceptar los valores por defecto recomendados.

El flujo de configuración te pedirá lo siguiente:

* Conexión a Base de Datos.
    * Presiona `Enter` o `1` si configuraste tu archivo `.env` para extraer datos en tiempo real.
    * Presiona `0` para activar el modo local (usará un archivo `sales.csv` previamente descargado).


* Filtrado de Rutas (Opcional).
    * Podrás excluir o incluir rutas de venta específicas escribiéndolas separadas por comas (ejemplo: `90, 95`).

* Selección de Variables.
    * Te pedirá confirmar cuál es tu columna objetivo (por defecto `net_price`) y tu columna de tiempo (por defecto `sale_date`).
* Manejo de Outliers.
    * Elegirás un método estadístico para limpiar valores atípicos o negativos (recomendado y por defecto: `linear`).
* Rango de Entrenamiento.
    * Definirás las fechas límite para que el modelo SARIMAX aprenda del comportamiento histórico.
* Rango de Pronóstico.
    * Establecerás el periodo futuro que deseas predecir.
> Nota: Por regla matemática del modelo, la fecha de inicio del pronóstico debe ser estrictamente posterior al final del entrenamiento.


* Exportación de Resultados.
    * Tras evaluar el modelo y generar la predicción, el sistema te mostrará el volumen total pronosticado y te pedirá un nombre para guardar el archivo de salida `.csv` dentro del directorio de pronósticos.

#### Ejemplo de una sesión en la terminal

A continuación se muestra un ejemplo real de cómo se visualiza la interacción en la consola al correr el script. En este caso, el usuario elige el modo local, excluye la ruta 90, usa las variables por defecto y pronostica un mes de ventas:

```text
((venv) ) angelvelasco@Mac-mini-de-Angel JAPI % python core/main.py

Credentials Configuration

Did you configure an environment variables file?
 (This is necessary to connect to the database. If you don't have them,
 the system will only allow you to use existing local csv records).

 [Enter] or [1] if you have them
 [0] to use local files only
 > 0

-> Local mode activated. Existing csv records will be used.

Cleaner object was instanced successfully

exclude routes (separated by comma, e.g.: 90, 95) [press enter for none]: 90
include routes (separated by comma, e.g.: 90, 95) [press enter for all]: 

prepare_data method was applied on base Dataframe

please enter the target column name (y) [enter for "net_price"]: 
please enter the date column name (index) [enter for "sale_date"]: 

net_price as pd.Series object was created successfully

available methods: set_nan, drop, linear, neighbor_average, zero, ffill
select a method to remove outliers [press enter for "linear"]: 

outliers was removed from pd.Series using method: linear

training range dates
start training from [Enter for 2024-01-01]: 
end training on [Enter for 2026-05-22]: 

Data was converted into pd.Series (Range: 2024-01-01 a 2026-05-22)
sale_date
2024-01-01    125000.50
2024-01-02    132450.00
2024-01-03    128900.25
2024-01-04    141000.00
2024-01-05    145000.80
Name: net_price, dtype: float64

Non business days to use
['2026-01-01', '2026-02-02', '2026-03-16', ...]

                               SARIMAX Results                                
==============================================================================
Dep. Variable:              net_price   No. Observations:                  873
Model:             SARIMAX(1, 0, 0)x(0, 1, 1, 7)   Log Likelihood       -1205.4
Date:                Sun, 24 May 2026   AIC                             2416.8
...
==============================================================================

 Forecast Date Ranges Configuration 
In order to get a correct forecast, setting a date after the end training date is mandatory.
In this case: 2026-05-22 < start_forecast_date

Start forecast from [Enter for 2026-05-24]:
End forecast on [Enter for 2026-06-24]:

Confirmed range From 2026-05-24 to 2026-06-24

Generating exogenous matrix for forecast from 2026-05-24 to 2026-06-24...
forecast made successful
Forecast for period 2026-05-24 - 2026-06-24: 36.25048998977715
Save file output with predictions as: forecast_junio_2026

```

>Como nota adicional, el resultado esta escalado para mejores resultados del modelo. El resultado 36.25048998977715 está en millones, por lo que realmente significa 36,250,489.98 pesos mexicanos.

## Referencias

* Amat Rodrigo, J. (s. f.). *Modelos ARIMA y SARIMAX con Python*. Ciencia de Datos. [https://cienciadedatos.net/documentos/py51-modelos-arima-sarimax-python](https://cienciadedatos.net/documentos/py51-modelos-arima-sarimax-python)
* Ecevit, A., Öztürk, İ., Dağ, M., & Özcan, T. (2023). Short-term sales forecasting using LSTM and Prophet based models in e-commerce. *Acta Infologica*, *7*(1), 59–70. [https://doi.org/10.26650/acin.1259067](https://doi.org/10.26650/acin.1259067)
* Fonseca, M. (s. f.). *Notas de clase: Series de tiempo*. Instituto de Investigaciones en Matemáticas Aplicadas y en Sistemas (IIMAS), UNAM. [http://www.dpye.iimas.unam.mx/miguel/st_CNSF/notas_28_junio.pdf](http://www.dpye.iimas.unam.mx/miguel/st_CNSF/notas_28_junio.pdf)
* González E. (s. f.). *Análisis de series de tiempo* [Documento de RPubs]. RPubs. [https://rpubs.com/ElianElian/1171469](https://rpubs.com/ElianElian/1171469)
* IBM. (s. f.). *¿Qué son las redes neuronales recurrentes?*. IBM Think. [https://www.ibm.com/mx-es/think/topics/recurrent-neural-networks](https://www.ibm.com/mx-es/think/topics/recurrent-neural-networks)
* Prophet. (s. f.). *Quick Start*. Recuperado el 18 de mayo de 2026 de [https://facebook.github.io/prophet/docs/quick_start.html#python-api](https://facebook.github.io/prophet/docs/quick_start.html#python-api)
* Prophet Project. (2026, 2 de febrero). *Quick start*. Prophet Documentation. [https://facebook.github.io/prophet/docs/quick_start.html](https://facebook.github.io/prophet/docs/quick_start.html)
* Psycopg. (s. f.). *Basic module usage*. Recuperado el 18 de mayo de 2026 de [https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries](https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries)
* Python Package Index. (s. f.). *sshtunnel*. Recuperado el 18 de mayo de 2026 de [https://pypi.org/project/sshtunnel/](https://pypi.org/project/sshtunnel/)
* Seaborn. (s. f.). *seaborn.boxplot*. Recuperado el 18 de mayo de 2026 de [https://seaborn.pydata.org/generated/seaborn.boxplot.html](https://seaborn.pydata.org/generated/seaborn.boxplot.html)
* Sotaquirá, M. (s. f.). *La función de activación en las Redes Neuronales*. Codificando Bits. [https://codificandobits.com/blog/funcion-de-activacion/](https://codificandobits.com/blog/funcion-de-activacion/)
* Sotaquirá, M. (s. f.). *Redes LSTM: Introducción práctica*. Codificando Bits. [https://codificandobits.com/blog/redes-lstm/](https://codificandobits.com/blog/redes-lstm/)
* Statsmodels. (s. f.). *statsmodels.tsa.statespace.sarimax.SARIMAX*. Recuperado el 18 de mayo de 2026 de [https://www.statsmodels.org/dev/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html](https://www.statsmodels.org/dev/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html)
* Taylor, S. J., & Letham, B. (2018). Forecasting at scale. *The American Statistician*, *72*(1), 37–45. [https://peerj.com/preprints/3190/](https://peerj.com/preprints/3190/)
* TensorFlow. (s. f.). *tf.keras.layers.LSTM*. Recuperado el 18 de mayo de 2026 de [https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM](https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM)
* Toledano, I. [IvTole]. (s. f.). *MachineLearning_InferenciaBayesiana_CUGDL* [Repositorio de GitHub]. GitHub. [https://github.com/IvTole/MachineLearning_InferenciaBayesiana_CUGDL/tree/main]()