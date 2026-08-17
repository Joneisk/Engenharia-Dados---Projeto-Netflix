import os
import pandas as pd

class CreateGoldLayer:
    def __init__(self, input_dir='silver', output_dir='gold'):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True) # Cria a pasta gold se não existir

    def _create_dimension(self, df, column_name, dim_name, id_col_name):
        """
        Método auxiliar para criar uma tabela dimensão a partir de uma coluna da fato.
        """
        # Pega os valores únicos e remove nulos
        dim_df = df[[column_name]].drop_duplicates().dropna().reset_index(drop=True)
        
        # Cria uma chave substituta (Surrogate Key) auto-incremental
        dim_df[id_col_name] = dim_df.index + 1
        
        # Reordena as colunas para o ID ficar na frente
        dim_df = dim_df[[id_col_name, column_name]]
        
        # Salva a dimensão em Parquet
        output_path = os.path.join(self.output_dir, f'{dim_name}.parquet')
        dim_df.to_parquet(output_path, index=False)
        print(f"Dimensão '{dim_name}' criada com {len(dim_df)} registros.")
        
        return dim_df

    def build_star_schema(self, filename):
        """
        Lê o arquivo da Silver, cria as dimensões e gera a tabela Fato.
        """
        input_path = os.path.join(self.input_dir, filename)
        
        print(f"Lendo dados da Silver: {input_path}...")
        df_silver = pd.read_parquet(input_path)
        
        
        #CRIANDO AS DIM
        
        dim_diretor = self._create_dimension(df_silver, 'director', 'dim_diretor', 'id_diretor')
        dim_pais = self._create_dimension(df_silver, 'country', 'dim_pais', 'id_pais')
        dim_classificacao = self._create_dimension(df_silver, 'rating', 'dim_classificacao', 'id_classificacao')
        dim_tipo = self._create_dimension(df_silver, 'type', 'dim_tipo', 'id_tipo')

        #Criando a Fato
       
        fato = df_silver.copy()
        
        # Fazendo o JOIN para trazer os IDs numéricos para a tabela Fato
        fato = fato.merge(dim_diretor, on='director', how='left')
        fato = fato.merge(dim_pais, on='country', how='left')
        fato = fato.merge(dim_classificacao, on='rating', how='left')
        fato = fato.merge(dim_tipo, on='type', how='left')
        
        # Removendo as colunas de texto originais 
        colunas_para_remover = ['director', 'country', 'rating', 'type']
        fato = fato.drop(columns=colunas_para_remover)
        
        # Reorganizando a Fato para os IDs ficarem no começo
        colunas_fato = ['show_id', 'id_tipo', 'id_diretor', 'id_pais', 'id_classificacao', 
                        'title', 'cast', 'date_added', 'release_year', 'duration', 
                        'listed_in', 'description']
        fato = fato[colunas_fato]
        
        # Salva a tabela Fato
        fato_path = os.path.join(self.output_dir, 'fato_titulos.parquet')
        fato.to_parquet(fato_path, index=False)
        print(f"Tabela Fato 'fato_titulos' criada com {len(fato)} registros.")


if __name__ == "__main__":
    gold_layer = CreateGoldLayer(input_dir='silver', output_dir='gold')
    gold_layer.build_star_schema('netflix_titles.parquet')