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

    def create_table(self, table_name, columns):
        cursor = self.conn.cursor()
        
        # Cria a string das colunas com aspas duplas em volta do nome (ex: "cast" TEXT)
        cols_str = ', '.join([f'"{col}" {dtype}' for col, dtype in columns.items()])
        
        # Coloca aspas também no nome da tabela para segurança
        cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({cols_str})')
        
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