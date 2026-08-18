import os
import pandas as pd
from dotenv import load_dotenv
from db import DB

load_dotenv()

db = DB(
    host=os.getenv("DB_HOST"), 
    database=os.getenv("DB_NAME"), 
    user=os.getenv("DB_USER"), 
    password=os.getenv("DB_PASSWORD")
)

# CRIAMOS UM MAPA DAS CHAVES PRIMÁRIAS DE CADA TABELA
primary_keys = {
    "fato_titulos": "show_id",
    "dim_diretor": "id_diretor",
    "dim_pais": "id_pais",
    "dim_classificacao": "id_classificacao",
    "dim_tipo": "id_tipo"
}

for file in os.listdir("gold"):
    if not file.endswith(".parquet"):
        continue

    df = pd.read_parquet(os.path.join("gold", file))
    table_name = file.replace(".parquet", "")
    
    pk_col = primary_keys.get(table_name)
    
    columns_dict = {}
    for col, dtype in df.dtypes.items():
        if "int" in str(dtype):
            columns_dict[col] = "INT"
        elif "float" in str(dtype):
            columns_dict[col] = "FLOAT"
        elif "bool" in str(dtype):
            columns_dict[col] = "BOOLEAN"
        else:
            columns_dict[col] = "TEXT"
    
    db.create_table(
        table_name=table_name,
        columns=columns_dict,
        pk_column=pk_col
    )
    
    records = df.to_dict(orient="records")
    for record in records:
        # Em vez de insert_data, agora chamamos upsert_data passando a chave
        db.upsert_data(table_name, record, pk_col)

    print(f"Tabela {table_name} criada e populada com sucesso (via Upsert)!")

db.close_connection()