import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv  

load_dotenv()

class DB:
    def __init__(self, host=None, database=None, user=None, password=None):
        self.host = host or os.getenv("DB_HOST")
        self.database = database or os.getenv("DB_NAME")
        self.user = user or os.getenv("DB_USER")
        self.password = password or os.getenv("DB_PASSWORD")

        self.conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )

    def create_table(self, table_name, columns, pk_column=None):
        cursor = self.conn.cursor()
        
        # Monta as colunas. Se for a coluna chave (pk_column), adiciona PRIMARY KEY
        cols_list = []
        for col, dtype in columns.items():
            if col == pk_column:
                cols_list.append(f'"{col}" {dtype} PRIMARY KEY')
            else:
                cols_list.append(f'"{col}" {dtype}')
                
        cols_str = ', '.join(cols_list)
        
        cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({cols_str})')
        self.conn.commit()
        cursor.close()

    def upsert_data(self, table_name, data, pk_column):
        cursor = self.conn.cursor()
        
        # 1. Prepara as colunas e os valores para o INSERT
        columns = ', '.join([f'"{k}"' for k in data.keys()])
        values = ', '.join(['%s'] * len(data))
        
        # 2. Prepara o que vai ser ATUALIZADO se o ID já existir (exclui a chave primária da atualização)
        update_cols = ', '.join([f'"{k}" = EXCLUDED."{k}"' for k in data.keys() if k != pk_column])
        
        # 3. Monta a query mágica de UPSERT do PostgreSQL
        sql = f'''
            INSERT INTO "{table_name}" ({columns}) 
            VALUES ({values})
            ON CONFLICT ("{pk_column}") 
            DO UPDATE SET {update_cols}
        '''
        
        cursor.execute(sql, list(data.values()))
        self.conn.commit()
        cursor.close()

    def insert_data(self, table_name, data):
        cursor = self.conn.cursor()
        
        # Coloca aspas duplas nas chaves (colunas) para o INSERT
        columns = ', '.join([f'"{k}"' for k in data.keys()])
        values = ', '.join(['%s'] * len(data))
        
        cursor.execute(f'INSERT INTO "{table_name}" ({columns}) VALUES ({values})', list(data.values()))
        
        self.conn.commit()
        cursor.close()
    
    def select_all_data_from_table(self, table_name, limit=100):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM "{table_name}" LIMIT {limit}')
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def close_connection(self):
        if self.conn:
            self.conn.close()
    
if __name__ == "__main__":
    db = DB()