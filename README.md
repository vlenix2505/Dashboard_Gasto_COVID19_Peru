# Gasto COVID-19 en Perú (2020-2025)

_Vista de la Página Principal_

![image](https://github.com/user-attachments/assets/3e0e01c5-df30-43c6-aaeb-4db6b03e166d)

## 📌 Project Background
Este proyecto tiene como objetivo analizar la ejecución del gasto relacionado con el COVID-19 en el Perú desde el año 2020 hasta 2025. Utiliza datos abiertos del **Ministerio de Economía y Finanzas (MEF)**, extraídos desde archivos CSV disponibles en línea.

Se desarrolló un modelo de datos en **estrella**, almacenado en una base de datos **SQL Server**, para facilitar la generación de reportes dinámicos en **Power BI**. Además, se implementó un mecanismo de **backup en Google Drive** para resguardar la información histórica antes de cada actualización.

El informe está compuesto por 5 páginas:

- [Principal](paginasPowerBI/1-Principal.jpg): Página que muestra un resumen general de la Ejecución pública del Gasto de COVID 19.
- [Temporal](paginasPowerBI/2-Temporal.jpg): Página que muestra la evolución temporal del Gasto de COVID 19, analizando la variación porcentual mensual y un resumen de los montos efectuados.
- [Regional](paginasPowerBI/3-Regional.jpg): Página que muestra la distribución del gasto ejecutado por departamento, resaltando las regiones con mayor inversión y visualizando el volumen del porcentaje ejecutado en un mapa interactivo.
- [Sectores](paginasPowerBI/4-Sectores.jpg): Página que muestra la distribución del gasto COVID-19 por sector, destacando a Salud y Desarrollo e Inclusión Social como los principales ejecutores de recursos.
- [Actividad](paginasPowerBI/5-Actividad.jpg): Página que analiza el gasto según programas y actividades, resaltando donde se efectuaron las mayores inversiones.


## 🏗️ Data Structure
El modelo estrella está compuesto por las siguientes tablas:

### 🔹 Tablas de Dimensión:
- **DimTiempo:** Contiene información de año y mes de ejecución.
- **DimUbicacion:** Contiene información geográfica de los registros (departamento, provincia y distrito).
- **DimEntidad:** Identifica el nivel de gobierno, sector, pliego y ejecutora.
- **DimActividad:** Incluye programas presupuestales, tipo de actividad, producto/proyecto y actividad específica.

### 🔹 Tabla de Hechos:
- **Hechos:** Contiene los montos financieros asociados a la ejecución del gasto, incluyendo:
  - **MONTO_PIA** (Presupuesto Inicial de Apertura)
  - **MONTO_PIM** (Presupuesto Institucional Modificado)
  - **MONTO_CERTIFICADO** (Certificaciones Presupuestarias emitidas)
  - **MONTO_COMPROMETIDO** (Monto comprometido para ejecución)
  - **MONTO_DEVENGADO** (Monto efectivamente ejecutado)
  - **MONTO_GIRADO** (Monto pagado a proveedores)

    ![image](https://github.com/user-attachments/assets/676644c6-786b-4150-8acf-b3be68091cc4)

Además, en Power BI se utilizaron tablas adicionales como una tabla de Calendario para la gestión de fechas de la dimensión tiempo (DimTiempo), tabla de medidas (Medidas) para calcular métricas clave de manera eficiente y otra tabla para almacenar la fecha de actualización del reporte (Actualización).

   ![image](https://github.com/user-attachments/assets/5eb93f94-d9df-4912-8e98-0322071c8b68)


## 📊 Executive Summary
El análisis realizado en **Power BI** permitió responder las siguientes preguntas clave:

1️⃣ **¿Cómo ha evolucionado el gasto en COVID-19 a lo largo de los años (2020-2025)?**
   - Se observó un pico de inversión en 2020 y 2021, con una disminución progresiva en los años siguientes.

2️⃣ **¿Cómo se distribuye el gasto entre los niveles de gobierno?**
   - El **Gobierno Nacional** ejecutó el mayor porcentaje del gasto, seguido por los **Gobiernos Regionales** y **Locales**.

3️⃣ **¿Qué actividades, obras o acciones de inversión han sido prioritarias?**
   - Programas como **Asignaciones Presupuestarias que No Resultan en Productos** y **Reducción de Vulnerabilidad y Atención de Emergencias** recibieron la mayor cantidad de fondos.

4️⃣ **¿Qué sectores y pliegos han ejecutado más recursos?**
   - **Desarrollo e Inclusión Social**, **Salud** y **Trabajo y Promoción del Empleo** lideraron la ejecución de gasto.

5️⃣ **¿Cómo se compara el presupuesto inicial (MONTO_PIA) con el gasto ejecutado (MONTO_DEVENGADO)?**
   - Se logró un alto porcentaje de ejecución (91.74% en promedio), con variaciones entre sectores y años.

6️⃣ **¿Qué productos o proyectos han recibido más recursos?**
   - **Programas de atención en salud** y **proyectos de infraestructura hospitalaria** fueron prioritarios en la distribución del presupuesto.

7️⃣ **¿Cómo se distribuye el gasto por departamentos?**
   - **Lima, Piura, La Libertad y Cusco** fueron los departamentos con mayor ejecución de recursos.
   - Los departamentos amazónicos y con menor infraestructura presentaron menor ejecución presupuestaria.


## 🛠️ Technical Implementation

### 🔹 Extracción de Datos
Los datos se obtienen desde archivos **CSV en línea** proporcionados por el MEF. Cada año tiene un archivo específico:
```python
start_year = 2020
current_year = datetime.now().year
years = list(range(start_year, current_year + 1))

dfs = []
for year in years:
    url = f'https://fs.datosabiertos.mef.gob.pe/datastorefiles/{year}-Gasto-COVID-19.csv'
    
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        df_year = pd.read_csv(StringIO(response.text))
        df_year = df_year[columnas_requeridas]
        dfs.append(df_year)
        print(f"Datos de {year} descargados correctamente. Registros: {len(df_year)}")
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar {year}: {e}")
```
Los datos extraídos se almacenan en **SQL Server** utilizando **PyODBC** y **SQLAlchemy**.

### 🔹 Carga y Transformación
Se utiliza un esquema **transaccional (BEGIN, COMMIT, ROLLBACK)** para evitar inconsistencias en la base de datos. Además, se eliminan los datos previos en cada actualización:
```python
cursor.execute("BEGIN TRANSACTION")
cursor.execute("DELETE FROM Hechos")
conn.commit()
```

### 🔹 Backup en Google Drive
Antes de eliminar registros antiguos, se realiza un **backup automático** y se sube a Google Drive:
```python
df_backup = pd.read_sql("SELECT * FROM Hechos", engine)
df_backup.to_csv(backup_file, index=False, encoding="utf-8-sig")
gauth = GoogleAuth()
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "service_account.json",
        ["https://www.googleapis.com/auth/drive"]
    )
drive = GoogleDrive(gauth)
file_drive = drive.CreateFile({
        'title': backup_file,
        'parents': [{'id': folder_id}]
    })
file_drive.SetContentFile(backup_file)
file_drive.Upload()
```

## 📂 Additional Sections
### 🔹 Librerías Utilizadas
El código fue desarrollado en **Python**, con las siguientes librerías:
```python
import pandas as pd
import pyodbc
import requests
from datetime import datetime
from sqlalchemy import create_engine
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from io import StringIO
import os
from oauth2client.service_account import ServiceAccountCredentials
```

### 🔹 Conclusiones
- Se logró centralizar la información del gasto COVID-19 en **SQL Server**, optimizando el análisis en **Power BI**.
- Se implementó una estrategia de actualización **automática y transaccional**, asegurando la integridad de los datos.
- Se habilitó un mecanismo de **backup en Google Drive** para proteger la información histórica.
- **Python** fue utilizado como herramienta principal para la extracción, transformación y carga (ETL) de los datos.

📌 **Este proyecto proporciona una visión completa del impacto financiero del COVID-19 en el Perú, facilitando la toma de decisiones informadas en futuras crisis sanitarias.**
