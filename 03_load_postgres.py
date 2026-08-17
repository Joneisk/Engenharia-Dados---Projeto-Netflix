import os
import pandas as pd
from dotenv import load_dotenv
from db import DB

load_dotenv()

# Instanciando o banco de dados
db = DB(
    host=os.getenv("DB_HOST"), 
    database=os.getenv("DB_NAME"), 
    user=os.getenv("DB_USER"), 
    password=os.getenv("DB_PASSWORD")
)

for file in os.listdir("gold"):
    # Ignora arquivos que não sejam parquet
    if not file.endswith(".parquet"):
        continue

    # Lendo o dataframe
    df = pd.read_parquet(os.path.join("gold", file))
    table_name = file.replace(".parquet", "")
    
    # 1. MAPEAMENTO: Transformando as colunas do Pandas em um Dicionário pro DB
    columns_dict = {}
    for col, dtype in df.dtypes.items():
        # Descobre o tipo no Pandas e converte para o tipo do PostgreSQL
        if "int" in str(dtype):
            columns_dict[col] = "INT"
        elif "float" in str(dtype):
            columns_dict[col] = "FLOAT"
        elif "bool" in str(dtype):
            columns_dict[col] = "BOOLEAN"
        else:
            columns_dict[col] = "TEXT"  # TEXT é melhor que VARCHAR pois não tem limite
    
    # Criando a tabela no banco (Agora o .items() vai funcionar!)
    db.create_table(
        table_name,
        columns_dict
    )
    
    # 2. INSERÇÃO: Transformando o DataFrame em dicionários (um por linha)
    records = df.to_dict(orient="records")
    for record in records:
        # Envia uma linha de cada vez, exatamente como o db.py espera
        db.insert_data(table_name, record)

    print(f"Tabela {table_name} criada e populada com sucesso!")

# Fechar a conexão
db.close_connection()