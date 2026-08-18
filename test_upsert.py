from db import DB

db = DB()
cursor = db.conn.cursor()

print("Iniciando o teste de stress do Upsert...\n")

cursor.execute('SELECT COUNT(*) FROM "fato_titulos"')
total_antes = cursor.fetchone()[0]
print(f"Total de linhas na Fato ANTES: {total_antes}")

#  Pega o primeiro filme da tabela para teste
cursor.execute('SELECT * FROM "fato_titulos" LIMIT 1')
col_names = [desc[0] for desc in cursor.description] # Pega o nome das colunas
row = cursor.fetchone()
filme_cobaia = dict(zip(col_names, row)) # Transforma em dicionário

print(f"Filme escolhido: '{filme_cobaia['title']}' | Ano original: {filme_cobaia['release_year']}")

# Vamos mudar o ano do filme para 3000 e tentar inserir de novo
filme_cobaia['release_year'] = 3000

print(f"\nTentando inserir '{filme_cobaia['title']}' novamente, mas agora com o ano 3000...")
# Passamos para o seu método upsert_data exatamente como seu script principal faz
db.upsert_data(table_name="fato_titulos", data=filme_cobaia, pk_column="show_id")

#Verifica se ele duplicou a linha ou se apenas atualizou
cursor.execute('SELECT COUNT(*) FROM "fato_titulos"')
total_depois = cursor.fetchone()[0]

cursor.execute(f'SELECT "release_year" FROM "fato_titulos" WHERE "show_id" = \'{filme_cobaia["show_id"]}\'')
ano_atualizado = cursor.fetchone()[0]

print("\n--- RESULTADO ---")
print(f"Total de linhas na Fato DEPOIS: {total_depois}")
if total_antes == total_depois:
    print("SUCESSO: O Upsert NÃO duplicou a linha!")
else:
    print("ERRO: O número de linhas aumentou. Ele duplicou o dado.")

print(f"Ano salvo no banco agora: {ano_atualizado}")
if ano_atualizado == 3000:
    print("SUCESSO: O Upsert ATUALIZOU o dado corretamente!")
else:
    print("ERRO: O dado antigo não foi alterado.")

db.close_connection()