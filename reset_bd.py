from db import DB

db = DB()
cursor = db.conn.cursor()

tabelas = ["fato_titulos", "dim_diretor", "dim_pais", "dim_classificacao", "dim_tipo"]

print("Apagando as tabelas antigas (sem Chave Primária)...")
for tabela in tabelas:
    cursor.execute(f'DROP TABLE IF EXISTS "{tabela}" CASCADE')

db.conn.commit()
db.close_connection()
print("Tabelas apagadas com sucesso! O banco está limpo.")