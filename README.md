# Proyecto JAPI para forecasting
- **J**uan Pablo Estrada Aragon
- **A**ngel Emmanuel Moreno Velasco
- **P**aulo Andrés Jiménez Jiménez
- **I**rving Gael Robles Ventura

Este proyecto tiene como objetivo predecir las ventas netas (monto total - devoluciones - descuentos) para la empresa **Urvet de México**. Se utiliza un enfoque de ensamble híbrido que integra modelos estadísticos, de aprendizaje profundo y algoritmos de clasificación/regresión.

## Stack
- **Forecasting:** SARIMAX, Prophet.
- **Deep Learning:** LSTM (TensorFlow/Keras).
- **Machine Learning:** Logistic Regression, KNN.
- **Data:** Pandas, Sklearn, Statsmodels.

## Estructura del Proyecto

A continuación se detalla la función de cada directorio para mantener la modularidad y el orden del código:

---

### `config/`
* **¿Para qué sirve?** Almacenar toda la configuración estática y parámetros que no deben estar "hardcodeados" en el código.
* **¿Qué va aquí?**
    * Configuraciones de conexión a bases de datos o rutas de archivos.
    * Variables de entorno específicas del proyecto (ej. `settings.py`).

---

### `core/`
* **¿Para qué sirve?** Es el cerebro de la ejecución. Aquí reside la lógica que manda a llamar a las demás funciones para completar un proceso.
* **¿Qué va aquí?:** Scripts que ejecutan el pipeline completo.
    * **Servicios:** Clases que coordinan el flujo entre la carga de datos, el procesamiento y la predicción final.

---

### `data/`
* **¿Para qué sirve?** Directorio que almacena todos los datos crudos.
* **¿Qué va aquí?:** Archivos `.csv` o `.xlsx`, todo lo relacionado a formatos crudos.

---

### `models/`
* **¿Para qué sirve?** Repositorio de artefactos finales y definiciones de estructura de datos.
* **¿Qué va aquí?:** Archivos `.pkl`, `.h5`, `.json` o `.bst` (pesos de LSTM, modelos SARIMAX entrenados).

---

### `notebooks/`
* **¿Para qué sirve?** Espacio exclusivo para la investigación y descubrimiento de insights antes de pasar a producción.
* **¿Qué va aquí?:** Análisis de tendencias, correlaciones, detección de outliers y visualizaciones de ventas históricas, además de pruebas en diferentes modelos.
    * **Nota:** Solo debe contener archivos `.ipynb` o reportes en `.html`. No debe haber código productivo aquí.

---

### `src/`
* **¿Para qué sirve?** Contiene la lógica interna, modular y reutilizable. Es el "motor" del proyecto. Se divide en:
    * `features/`: Scripts para transformar datos crudos en variables (ventas netas, estacionalidades).
    * `predictors/`: La implementación técnica de cada algoritmo (la lógica de SARIMAX, Prophet, LSTM, etc.).
    * `utils/`: Funciones genéricas (lectura de Excel/SQL, cálculo de métricas de error, logging).

---

### `utils/`
* **¿Para qué sirve?** Sirve para centralizar funciones que si bien, pueden ser incluidas como métodos de clases en otros scripts, tienden a ser más universales, como por ejemplo, la extración y lectura de archivos, establecimiento correcto de tipo de datos, timestamps específicos, etc.
* **¿Qué va aquí?:** Archivos `.py`.

---