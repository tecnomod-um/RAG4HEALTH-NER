import csv
import re

def extract_text_between_hpi_and_pmh(text):
    """Extrae el texto entre 'History of Present Illness:' y 'Past Medical History:'."""
    start_keyword = "History of Present Illness:"
    end_keyword = "Past Medical History:"
    
    # Usar expresiones regulares para capturar el texto, incluyendo saltos de línea
    start_match = re.search(re.escape(start_keyword), text, re.IGNORECASE)
    end_match = re.search(re.escape(end_keyword), text, re.IGNORECASE)
    
    if not start_match or not end_match or end_match.start() <= start_match.end():
        return []  # Si no se encuentran las palabras clave, retorna una lista vacía.
    
    # Extraer todo el texto entre las palabras clave
    relevant_text = text[start_match.end():end_match.start()].strip()
    
    # Eliminar retornos de carro y espacios múltiples, dejando un solo espacio entre las palabras
    relevant_text = re.sub(r'\s+', ' ', relevant_text)

    # Definir abreviaciones comunes y añadir "Pt.", "e.g.", "etc."
    abbreviations = ['Mr.', 'Mrs.', 'Dr.', 'Ms.', 'Prof.', 'Sr.', 'Sra.', 'St.', 'Jr.', 'Pt.', 'e.g.', 'etc.']
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

    return sentences

def process_csv(input_file, output_file):
    """Lee un archivo CSV, extrae frases entre 'History of Present Illness:' y 'Past Medical History:' y las guarda en un nuevo CSV."""
    with open(input_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        all_sentences = []

        for row in reader:
            text = row['text']
            sentences = extract_text_between_hpi_and_pmh(text)
            
            all_sentences.extend(sentences)

    # Escribir el resultado final en el archivo de salida
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['sentence'])
        writer.writerows([[sentence] for sentence in all_sentences])

# Uso del script
input_file = 'mimic-iv_notes_training_set.csv'  # Nombre del archivo CSV de entrada
output_file = 'mimic-iv-extract.csv'  # Nombre del archivo CSV de salida

process_csv(input_file, output_file)
