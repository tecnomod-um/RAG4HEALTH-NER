import pandas as pd
import os

def merge_csv_files(output_file):
    # Lista para almacenar los DataFrames de cada archivo CSV
    all_dataframes = []
    
    # Iterar sobre los archivos que siguen el patrón clinical_data_rada_X.csv
    for i in range(10):
        filename = f'clinical_data_rada_p7_{i}.csv'
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            all_dataframes.append(df)
        else:
            print(f"File {filename} does not exist and will be skipped.")
    
    # Concatenar todos los DataFrames en uno solo
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Guardar el DataFrame combinado en un nuevo archivo CSV
    combined_df.to_csv(output_file, index=False)
    print(f"All files have been merged into {output_file}")

if __name__ == "__main__":
    output_file = 'Pattern7NER.csv'  # Nombre del archivo de salida
    merge_csv_files(output_file)
