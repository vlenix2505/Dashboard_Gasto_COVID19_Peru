# COVID-19 Public Spending Analysis in Peru (2020-2025)

_Vista de la Página Principal_

![1-Principal](https://github.com/user-attachments/assets/9f828e43-79b2-44d5-bee0-2d1780862b04)



## 📌 Project Background
Este proyecto tiene como objetivo analizar la ejecución del gasto relacionado con el COVID-19 en el Perú desde el año 2020 hasta 2025. Utiliza datos abiertos del **Ministerio de Economía y Finanzas (MEF)**, extraídos desde archivos CSV disponibles en línea, mediante un código en **PySpark**.

Se desarrolló un modelo de datos en estrella, almacenado en **OneLake**, para facilitar la generación de reportes dinámicos en **Power BI**. Además, se utiliza el historial de versiones de la **Delta Table Hechos** para resguardar la información histórica antes de cada actualización.

El informe está compuesto por 5 páginas:

- [Principal](paginasPowerBI/1-Principal.jpg): Página que muestra un resumen general de la Ejecución pública del Gasto de COVID 19.
- [Temporal](paginasPowerBI/2-Temporal.jpg): Página que muestra la evolución temporal del Gasto de COVID 19, analizando la variación porcentual mensual y un resumen de los montos efectuados.
- [Regional](paginasPowerBI/3-Regional.jpg): Página que muestra la distribución del gasto ejecutado por departamento, resaltando las regiones con mayor inversión y visualizando el volumen del porcentaje ejecutado en un mapa interactivo.
- [Sectores](paginasPowerBI/4-Sectores.jpg): Página que muestra la distribución del gasto COVID-19 por sector, destacando a Salud y Desarrollo e Inclusión Social como los principales ejecutores de recursos.
- [Actividad](paginasPowerBI/5-Actividad.jpg): Página que analiza el gasto según programas y actividades, resaltando donde se efectuaron las mayores inversiones.

Puedes acceder al dashboard online en [este link](https://app.powerbi.com/view?r=eyJrIjoiMjcwZTgzNTktZWE0NS00NzI4LTljMzAtNWMxY2E4MGYwZDE1IiwidCI6IjBlMGNiMDYwLTA5YWQtNDlmNS1hMDA1LTY4YjliNDlhYTFmNiIsImMiOjR9&pageName=458373886d0d88309990)

## 🏗️ Data Structure
La estructura de los datos se encuentra profundamente detallada en el archivo de [documentación del datamart](Documentación%20datamart%20-%20GastoCovidReport.pdf). 

Como resumen, el modelo estrella está compuesto por las siguientes tablas:

### 🔹 Tablas de Dimensión:
- **DimTiempo:** Contiene información de año y mes de ejecución.
- **DimUbicacion:** Contiene información geográfica de los registros (departamento, provincia y distrito).
- **DimEntidad:** Identifica el nivel de gobierno, sector, pliego y ejecutora.
- **DimActividad:** Incluye programas presupuestales, tipo de actividad, producto/proyecto y actividad específica.

### 🔹 Tabla de Hechos:
- **Hechos:** Contiene los montos financieros asociados a la ejecución del gasto, incluyendo:
  - **MONTO_PIA** (Presupuesto Inicial de Apertura)
  - **MONTO_PIM** (Presupuesto Institucional Modificado)
  - **MONTO_CERTIFICADO** (Es el dinero que se ha reservado para gastar)
  - **MONTO_COMPROMETIDO** (Monto comprometido para ejecución, en contratos)
  - **MONTO_DEVENGADO** (Gasto efectivamente ejecutado)
  - **MONTO_GIRADO** (Monto pagado a proveedores)

Además, se almacena una tabla update_log que registra la última fecha y hora de actualización (se modificó el código para que use la zona horaria de Lima UTC-5 en lugar de UTC, la cual es la zona predeterminada por Fabric).

   ![image](https://github.com/user-attachments/assets/a55427f7-3fc1-4148-97a6-04f6b2284118)


Por otro lado, en Power BI se utilizaron tablas adicionales como una tabla de Calendario para la gestión de fechas de la dimensión tiempo (DimTiempo), tabla de medidas (Medidas) para calcular métricas clave de manera eficiente y otra tabla para almacenar la fecha de actualización del reporte (Actualización).

### 🔹 Medidas DAX Implementadas:

A continuación, se detallan algunas de las medidas DAX utilizadas en el análisis, las cuales fueron separadas por carpetas para mantener un orden general en la estructura del informe:

- **Eficiencia del Pago (%)**: Mide la relación entre el monto girado y el ejecutado, expresado en porcentaje.  
- **Porcentaje de Ejecución**: Calcula el porcentaje del presupuesto ejecutado con respecto al PIM.  
- **Porcentaje Contratado**: Se obtiene dividiendo el **Monto Comprometido** entre el **PIM**, indicando el nivel de contratación del presupuesto.  
- **Porcentaje Habilitado**: Calcula la relación entre el **Monto Certificado** y el **PIM**, reflejando cuánto del presupuesto ha sido habilitado formalmente.   
- **Promedio Mensual Ejecutado**: Calcula el promedio mensual del gasto ejecutado a lo largo del periodo analizado.  
- **Ranking de Departamentos por Ejecutado**: Ordena los departamentos según su nivel de ejecución del presupuesto.  

     ![image](https://github.com/user-attachments/assets/7308ddb4-e641-48f6-9997-8fbd206ff840)



## 📊 Executive Summary
El análisis realizado en **Power BI** permitió atender los requisitos de negocio planteados para el caso de investigación, el cual se detalla en la [documentación del datamart](Documentación%20datamart%20-%20GastoCovidReport.pdf), respondiendo preguntas clave como las siguientes (resultados al 16/03/2025) :

1️⃣ **¿Cómo ha evolucionado el gasto en COVID-19 a lo largo de los años (2020-2025)?**
   - Se observó un pico de inversión en 2020 y 2021, con una disminución progresiva en los años siguientes.

2️⃣ **¿Cómo se distribuye el gasto entre los niveles de gobierno?**
   - El **Gobierno Nacional** ejecutó el mayor porcentaje del gasto, representando el 80.34% del gasto ejecutado anual, seguido por los **Gobiernos Regionales** (18.05%) y **Locales**(1.61%).

3️⃣ **¿Qué actividades, obras o acciones de inversión han sido prioritarias?**
   - Programas como **Asignaciones Presupuestarias que No Resultan en Productos** y **Reducción de Vulnerabilidad y Atención de Emergencias** recibieron la mayor cantidad de fondos.

4️⃣ **¿Qué sectores y pliegos han ejecutado más recursos?**
   - **Desarrollo e Inclusión Social**, **Salud** y **Trabajo y Promoción del Empleo** lideraron el TOP 3 en la ejecución de gasto. Por otro lado, el **Ministerio de Desarrollo e Inclusión Social**, **M. de Trabajo y Promoción del Empleo y M. De Salud** encabezaron el ranking de Pliegos por gasto ejecutado 

5️⃣ **¿Cómo se compara el presupuesto inicial (MONTO_PIM) con el gasto ejecutado (MONTO_DEVENGADO)?**
   - Se logró un alto porcentaje de ejecución (91.55% en promedio), con variaciones entre sectores y años.

6️⃣ **¿Qué productos o proyectos han recibido más recursos?**
   - **Asignaciones Presupuestarias que no resultan en proyectos** fue el Programa Presupuestal con mayor presupuesto inicial y gasto ejecutado, alcanzando un %ejecutado del 91.59%.

7️⃣ **¿Cómo se distribuye el gasto por departamentos?**
   - **Lima, La Libertad y Piura** fueron los departamentos con mayor ejecución de recursos.
   - Los departamentos amazónicos y con menor infraestructura presentaron menor ejecución presupuestaria.
   - El TOP 3 de departamentos con mayor cantidad de Proyectos únicos fueron **Lima, Ancash** y **La Libertad**, en el orden respectivo. Sin embargo, pese a que Ancash está involucrado en 6 proyectos, ocupa el puesto 6 en el ranking de gasto ejecutado (aprox S/.522 mil), siendo el puesto 2 correspondiente a Piura, departamento con solo 11 proyectos (aprox S/.654 mil).

## 🛠️ Technical Implementation

### 🔹 Extracción de Datos
Se descargan los datos desde **archivos CSV en línea** del MEF y se procesan en **PySpark**, dentro de un Notebook en Fabric:
```python
# Definir periodo de tiempo
start_year = 2020
current_year = 2025
years = list(range(start_year, current_year + 1))
ANOS_ACTUALIZAR = [2023, 2024, 2025]

#Definir columnas de análisis
columnas_requeridas = [
    'ANO_EJE', 'MES_EJE', 'NIVEL_GOBIERNO_NOMBRE', 'SECTOR_NOMBRE',
    'PLIEGO_NOMBRE', 'EJECUTORA_NOMBRE', 'DEPARTAMENTO_EJECUTORA_NOMBRE',
    'PROVINCIA_EJECUTORA_NOMBRE', 'DISTRITO_EJECUTORA_NOMBRE',
    'PROGRAMA_PPTO_NOMBRE', 'TIPO_ACT_PROY_NOMBRE',
    'PRODUCTO_PROYECTO_NOMBRE', 'ACTIVIDAD_ACCION_OBRA_NOMBRE', 'MONTO_PIA',
    'MONTO_PIM', 'MONTO_CERTIFICADO', 'MONTO_COMPROMETIDO_ANUAL',
    'MONTO_COMPROMETIDO', 'MONTO_DEVENGADO', 'MONTO_GIRADO'
]

dfs = []

for year in years:
    url_csv = f'https://fs.datosabiertos.mef.gob.pe/datastorefiles/{year}-Gasto-COVID-19.csv'    
    try:
        response = requests.get(url_csv, verify=False, timeout=10)
        response.raise_for_status()        
        df_pandas = pd.read_csv(StringIO(response.text), usecols=columnas_requeridas, low_memory=False)
        df_spark = spark.createDataFrame(df_pandas)        
        dfs.append(df_spark)
        print(f"Datos de {year} descargados correctamente. Registros: {df_spark.count()}")
    except Exception as e:
        print(f"Error al descargar {year}: {e}")

if dfs:
    df = reduce(lambda df1, df2: df1.union(df2), dfs)
    print(f"Datos totales obtenidos: {df.count()} registros.")
```

### 🔹 Carga y Transformación
La información se almacena en **OneLake** en formato Delta Table, con historial de versiones:
```python
# Ruta de la Tabla Hechos
ruta_hechos = "Tables/Hechos"

# Insertar registros nuevos en la tabla Hechos
        df_hechos_nuevo.write.format("delta") \
            .mode("append") \
            .partitionBy("id_tiempo") \
            .save(ruta_hechos)

 # Ver historial después de la inserción/actualización
        print("📌 Historial de versiones de la tabla Hechos después de la actualización:")
        hechos_delta.history().select("version", "timestamp", "operation").show(5)
```

## 📌 Criterio de Actualización por Reemplazo  
Se eligió un criterio de actualización parcial por reemplazo basado en la variabilidad de los datos:
- Los datos de **2020 a 2022** no han cambiado desde su última actualización.
- Solo se eliminan y reemplazan los registros de **2023, 2024 y 2025**.
- Esto optimiza el procesamiento y evita cambios innecesarios en el historial de versiones.

En cada ejecución:
- Se eliminan registros de **2023, 2024 y 2025** en la Delta Table.
- Se insertan los datos actualizados para esos años.
- Se actualiza la tabla **update_log** para reflejar la nueva fecha de actualización en el informe de Power BI.

## 🔄 Flujo de Actualización en Data Factory
El proceso de actualización en **Data Factory** sigue una serie de pasos diseñados para garantizar la consistencia y confiabilidad de los datos. 

_Vista del Data Pipeline_

![image](https://github.com/user-attachments/assets/32630424-6f6f-47fa-a7a1-bee41bd18e57)


A continuación, se describe el flujo de datos **Actualizar_Covid_Report**:  
1. **Notebook de Actualización**  
   - Se ejecuta un **notebook en Fabric** llamado **Update_GastoCovid** que extrae y transforma los datos más recientes en OneLake.  
   - En caso de error, se captura un mensaje de error y se procede a restaurar la última versión válida al ejecutar el **Script_Restore**, el cual verifica que si hay suficientes versiones para restaurar y ha ocurrido una operación DELETE sin que sea seguida de un WRITE, procede a usar el versioning del Delta Table para restaurar la versión anterior.

```python
  if hubo_delete_sin_write:
        print(f"🚨 Se detectó un DELETE sin un posterior WRITE en la última ejecución.")
        print(f"🔄 Restaurando a la versión {version_anterior}...")

        # Restaurar tabla
        spark.sql(f"RESTORE TABLE delta.`{ruta_lakehouse}` TO VERSION AS OF {version_anterior}")

        print("✅ Restauración completada. Verificando datos...")
        spark.read.format("delta").load(ruta_lakehouse).show(10)
    else:
        print(f"✅ La última operación fue '{operacion_actual}', no se restaurará nada.")
```

2. **Actualización del Modelo Semántico**  
   - A pesar de que Power BI utiliza **DirectQuery**, el modelo semántico se actualiza para reflejar cambios en la estructura de datos o ajustes en medidas DAX.  
   - Si la actualización falla, se capturan los detalles del error en una variable establecida y se notifica por correo electrónico.  

3. **Notificación por Correo Electrónico**  
   - Se envían correos de confirmación cuando la actualización es exitosa a las cuentas establecidas en la configuración de la actividad.  
   - En caso de error en la ejecución del **notebook** o la actualización del modelo semántico, se notifica automáticamente con los detalles del fallo.  

![mensajeCorreo](https://github.com/user-attachments/assets/efcfc8c4-8729-4ed4-9ba0-5d0337016922)


4. **Programación**  
   - Se ha programado el pipeline para que se ejecute 3 veces por semana (Lunes, Miércoles y Viernes) a una determinada hora.
   - Considerar que la zona horaria varía según la región del usuario, en este caso, se escogió **(UTC-05:00) Bogotá, Lima, Quito**
     
![image](https://github.com/user-attachments/assets/08133deb-9a69-421a-9385-58543f0642ca)


## 📂 Additional Sections
### 🔹 Librerías Utilizadas
El código fue desarrollado en **PySpark**, con las siguientes librerías:
```python
import requests
import pandas as pd
import os
from pyspark.sql.functions import col, when, lit, to_date, concat, lpad
from io import StringIO
from pyspark.sql.functions import col
from functools import reduce
from delta.tables import DeltaTable
from pyspark.sql.window import Window
from pyspark.sql.utils import AnalysisException
from pyspark.sql.functions import row_number, monotonically_increasing_id, col, max as spark_max
import pytz
from datetime import datetime
```

### 🔹 Conclusiones
- Se implementó un datamart especializado en **SQL Server** para centralizar la información del gasto COVID-19, optimizando su consulta y análisis en **Power BI**.
- Se implementó una estrategia de actualización **automática y transaccional**, asegurando la integridad de los datos.
- Se habilitó un mecanismo de **backup en Google Drive** para proteger la información histórica.
- **Python** fue utilizado como herramienta principal para la extracción, transformación y carga (ETL) de los datos.
- Este proyecto proporciona una visión completa del impacto financiero del COVID-19 en el Perú, considerando factores clave como el tiempo, geografía, entidad y actividad realizada, lo cual facilita la toma de decisiones informadas en futuras crisis sanitarias.
