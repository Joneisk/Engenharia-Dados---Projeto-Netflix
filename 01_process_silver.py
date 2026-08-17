import os
import pandas as pd

class convertColumnsToString:
    def __init__(self, df):
        self.df = df

    def convert(self):
        for col in self.df.columns:
            if self.df[col].apply(lambda x: isinstance(x, list)).any():
                self.df[col] = self.df[col].apply(lambda x: str(x) if isinstance(x, list) else x)
        return self.df

class NormalizeData:
    def __init__(self, input_dir='bronze', output_dir='silver'):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)  #cria a pasta de saída se não existir

    def normalize(self):
        list_files = os.listdir(self.input_dir)

        for file in list_files:  # lendo todos os excel ou json
            input_path = os.path.join(self.input_dir, file)
            name, ext = os.path.splitext(file)

            output_path = os.path.join(self.output_dir, f'{name}.parquet')

            if ext.lower() == '.csv':
                df = pd.read_csv(input_path)
            elif ext.lower() == '.json':
                try:
                    df = pd.read_json(input_path)
                except ValueError:
                    df = pd.read_json(input_path, lines=True)
            else:
                print(f"Unsupported file type: {ext}")
                continue

            df = convertColumnsToString(df).convert()
            df = df.drop_duplicates().reset_index(drop=True)  # Remove duplicates

            df.to_parquet(output_path, index=False)

if __name__ == "__main__":
    normalizer = NormalizeData(input_dir='bronze', output_dir='silver')
    normalizer.normalize()