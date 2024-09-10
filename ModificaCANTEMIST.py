import csv
import re

def split_sentences_to_csv(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        all_sentences = []

        for row in reader:
            content = row[0]  # Toma el contenido de la primera columna
            
            # Eliminar retornos de carro y espacios múltiples, dejando un solo espacio entre las palabras
            relevant_text = re.sub(r'\s+', ' ', content)

            # Definir abreviaciones comunes y añadir "Pt.", "e.g.", "etc."
            abbreviations = ['Mr.', 'Mrs.', 'Dr.', 'Ms.', 'Prof.', 'Sr.', 'Sra.', 'St.', 'Jr.', 'Pt.', 'e.g.', 'etc.', 'ml.', '...', 'GMBH.', 'dynes.sec.c', 'Fig.']
            abbreviation_pattern = re.compile(r'\b\w\.')

            # Reemplazar temporalmente las abreviaciones y cualquier carácter seguido de un punto
            for abbr in abbreviations:
                relevant_text = relevant_text.replace(abbr, abbr.replace('.', '<DOT>'))
            
            relevant_text = abbreviation_pattern.sub(lambda x: x.group().replace('.', '<DOT>'), relevant_text)
            
            # Reemplazar también puntos en números
            relevant_text = re.sub(r'(\d+)\.', r'\1<DOT>', relevant_text)

            # Separar el texto en frases utilizando el punto como delimitador
            sentences = [sentence.strip() for sentence in relevant_text.split('.') if sentence]

            # Restaurar los puntos en las abreviaciones, caracteres individuales y números
            sentences = [sentence.replace('<DOT>', '.') for sentence in sentences]
            
            # Filtrar frases que comiencen con ":"
            sentences = [sentence for sentence in sentences if not sentence.startswith(":")]

            # Eliminar filas vacías y asegurar comillas correctas
            sentences = [f'"{sentence}"' for sentence in sentences if sentence]

            all_sentences.extend(sentences)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        for sentence in all_sentences:
            writer.writerow([sentence])

if __name__ == "__main__":
    input_file = 'clinicalDataModified.csv'  # Reemplaza con el nombre de tu archivo de entrada
    output_file = 'CANTEMIST.csv'  # Nombre del archivo de salida
    split_sentences_to_csv(input_file, output_file)
