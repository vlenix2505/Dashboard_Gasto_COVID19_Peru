import pandas as pd
import pyodbc
import requests
from datetime import datetime
from sqlalchemy import create_engine
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from io import StringIO
import os
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials


# Columnas requeridas
columnas_requeridas = [
    'ANO_EJE', 'MES_EJE', 'NIVEL_GOBIERNO_NOMBRE', 'SECTOR_NOMBRE',
    'PLIEGO_NOMBRE', 'EJECUTORA_NOMBRE', 'DEPARTAMENTO_EJECUTORA_NOMBRE',
    'PROVINCIA_EJECUTORA_NOMBRE', 'DISTRITO_EJECUTORA_NOMBRE',
    'PROGRAMA_PPTO_NOMBRE', 'TIPO_ACT_PROY_NOMBRE',
    'PRODUCTO_PROYECTO_NOMBRE', 'ACTIVIDAD_ACCION_OBRA_NOMBRE', 'MONTO_PIA',
    'MONTO_PIM', 'MONTO_CERTIFICADO', 'MONTO_COMPROMETIDO_ANUAL',
    'MONTO_COMPROMETIDO', 'MONTO_DEVENGADO', 'MONTO_GIRADO'
]

requests.packages.urllib3.disable_warnings()

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

if not dfs:
    print("No se descargaron datos. Finalizando ejecución.")
    exit()

df = pd.concat(dfs, ignore_index=True).drop_duplicates()
print(f"Datos totales obtenidos: {len(df)} registros.")
print(df.head())

# Cargar variables del archivo .env
load_dotenv()

conn_str = (
    f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"Trusted_Connection={os.getenv('DB_TRUSTED')};"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={conn_str}")
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("""
IF OBJECT_ID('dbo.Hechos', 'U') IS NOT NULL
    SELECT COUNT(*) FROM Hechos
ELSE
    SELECT -1
""")
num_registros = cursor.fetchone()[0]

fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"backup_hechos_{fecha_actual}.csv"
folder_id = os.getenv('FOLDER_ID')

if num_registros > 0:
    df_backup = pd.read_sql("SELECT * FROM Hechos", engine)
    df_backup.to_csv(backup_file, index=False, encoding="utf-8-sig")

    # Cargar credenciales de la cuenta de servicio
    gauth = GoogleAuth()
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "service_account.json",
        ["https://www.googleapis.com/auth/drive"]
    )

    drive = GoogleDrive(gauth)
    # Subir archivo a Google Drive
    file_drive = drive.CreateFile({
        'title': backup_file,
        'parents': [{'id': folder_id}]
    })

    file_drive.SetContentFile(backup_file)
    file_drive.Upload()
    print(f"Backup subido a Google Drive en la carpeta con ID: {folder_id}")

    # Forzar cierre del archivo antes de eliminarlo
    file_drive = None  

    # Ahora podemos eliminar el archivo sin problemas
    os.remove(backup_file)
    print(f"Archivo local eliminado: {backup_file}")


elif num_registros == -1:
    print("No se hizo backup, la tabla Hechos aún no existe.")
else:
    print("No se hizo backup, la tabla Hechos está vacía.")

try:
    cursor.execute("BEGIN TRANSACTION")

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimTiempo')
    CREATE TABLE DimTiempo (
        id_tiempo INT IDENTITY(1,1) PRIMARY KEY,
        ANO_EJE INT NOT NULL,
        MES_EJE INT NOT NULL
    );
    """)

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimUbicacion')
    CREATE TABLE DimUbicacion (
        id_ubicacion INT IDENTITY(1,1) PRIMARY KEY,
        DEPARTAMENTO_EJECUTORA_NOMBRE NVARCHAR(255) NOT NULL,
        PROVINCIA_EJECUTORA_NOMBRE NVARCHAR(255) NOT NULL,
        DISTRITO_EJECUTORA_NOMBRE NVARCHAR(255) NOT NULL
    );
    """)

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimEntidad')
    CREATE TABLE DimEntidad (
        id_entidad INT IDENTITY(1,1) PRIMARY KEY,
        NIVEL_GOBIERNO_NOMBRE NVARCHAR(255) NOT NULL,
        SECTOR_NOMBRE NVARCHAR(255) NOT NULL,
        PLIEGO_NOMBRE NVARCHAR(255) NOT NULL,
        EJECUTORA_NOMBRE NVARCHAR(255) NOT NULL
    );
    """)

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimActividad')
    CREATE TABLE DimActividad (
        id_actividad INT IDENTITY(1,1) PRIMARY KEY,
        PROGRAMA_PPTO_NOMBRE NVARCHAR(255) NOT NULL,
        TIPO_ACT_PROY_NOMBRE NVARCHAR(255) NOT NULL,
        PRODUCTO_PROYECTO_NOMBRE NVARCHAR(MAX) NOT NULL,
        ACTIVIDAD_ACCION_OBRA_NOMBRE NVARCHAR(255) NOT NULL
    );
    """)

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Hechos')
    CREATE TABLE Hechos (
        id_hecho INT IDENTITY(1,1) PRIMARY KEY,
        id_tiempo INT FOREIGN KEY REFERENCES DimTiempo(id_tiempo),
        id_ubicacion INT FOREIGN KEY REFERENCES DimUbicacion(id_ubicacion),
        id_entidad INT FOREIGN KEY REFERENCES DimEntidad(id_entidad),
        id_actividad INT FOREIGN KEY REFERENCES DimActividad(id_actividad),
        MONTO_PIA FLOAT NOT NULL,
        MONTO_PIM FLOAT NOT NULL,
        MONTO_CERTIFICADO FLOAT NOT NULL,
        MONTO_COMPROMETIDO FLOAT NOT NULL,
        MONTO_DEVENGADO FLOAT NOT NULL,
        MONTO_GIRADO FLOAT NOT NULL
    );
    """)

    conn.commit()

    def insertar_dimension(df, tabla, columnas):
        valores_unicos = df[columnas].drop_duplicates().values.tolist()
        query_check = f"SELECT 1 FROM {tabla} WHERE " + " AND ".join([f"{col} = ?" for col in columnas])
        query_insert = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({', '.join(['?' for _ in columnas])})"

        for valores in valores_unicos:
            cursor.execute(query_check, valores)
            if not cursor.fetchone():
                cursor.execute(query_insert, valores)

        conn.commit()
    
    cursor.execute("DELETE FROM Hechos")

    insertar_dimension(df, 'DimTiempo', ['ANO_EJE', 'MES_EJE'])
    insertar_dimension(df, 'DimUbicacion', ['DEPARTAMENTO_EJECUTORA_NOMBRE', 'PROVINCIA_EJECUTORA_NOMBRE', 'DISTRITO_EJECUTORA_NOMBRE'])
    insertar_dimension(df, 'DimEntidad', ['NIVEL_GOBIERNO_NOMBRE', 'SECTOR_NOMBRE', 'PLIEGO_NOMBRE', 'EJECUTORA_NOMBRE'])
    insertar_dimension(df, 'DimActividad', ['PROGRAMA_PPTO_NOMBRE', 'TIPO_ACT_PROY_NOMBRE', 'PRODUCTO_PROYECTO_NOMBRE', 'ACTIVIDAD_ACCION_OBRA_NOMBRE'])

    
    df_dim_tiempo = pd.read_sql("SELECT * FROM DimTiempo", engine)
    df_dim_ubicacion = pd.read_sql("SELECT * FROM DimUbicacion", engine)
    df_dim_entidad = pd.read_sql("SELECT * FROM DimEntidad", engine)
    df_dim_actividad = pd.read_sql("SELECT * FROM DimActividad", engine)

    df_hechos = df.merge(df_dim_tiempo, on=['ANO_EJE', 'MES_EJE'], how='left')
    df_hechos = df_hechos.merge(df_dim_ubicacion, on=['DEPARTAMENTO_EJECUTORA_NOMBRE', 'PROVINCIA_EJECUTORA_NOMBRE', 'DISTRITO_EJECUTORA_NOMBRE'], how='left')
    df_hechos = df_hechos.merge(df_dim_entidad, on=['NIVEL_GOBIERNO_NOMBRE', 'SECTOR_NOMBRE', 'PLIEGO_NOMBRE', 'EJECUTORA_NOMBRE'], how='left')
    df_hechos = df_hechos.merge(df_dim_actividad, on=['PROGRAMA_PPTO_NOMBRE', 'TIPO_ACT_PROY_NOMBRE', 'PRODUCTO_PROYECTO_NOMBRE', 'ACTIVIDAD_ACCION_OBRA_NOMBRE'], how='left')

    df_hechos.dropna(subset=['id_tiempo', 'id_ubicacion', 'id_entidad', 'id_actividad'], inplace=True)

    columnas_hechos = ['id_tiempo', 'id_ubicacion', 'id_entidad', 'id_actividad', 'MONTO_PIA', 'MONTO_PIM', 'MONTO_CERTIFICADO', 'MONTO_COMPROMETIDO', 'MONTO_DEVENGADO', 'MONTO_GIRADO']
    valores_hechos = [tuple(row) for _, row in df_hechos[columnas_hechos].iterrows()]

    cursor.executemany(f"INSERT INTO Hechos ({', '.join(columnas_hechos)}) VALUES ({', '.join(['?' for _ in columnas_hechos])})", valores_hechos)
    conn.commit()

    cursor.execute("COMMIT TRANSACTION")
    print("Datos insertados correctamente.")

except Exception as e:
    cursor.execute("ROLLBACK")
    print(f"Error detectado. Transacción revertida: {e}")

finally:
    cursor.close()
    conn.close()
