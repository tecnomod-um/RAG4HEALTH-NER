import os
import requests
import json
import torch
import pandas as pd

from sentence_transformers import SentenceTransformer, util

def retrieve_similar_instances(seed_text, external_texts, top_n=3):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    #model = SentenceTransformer('all-mpnet-base-v2')
    #model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')
    seed_embedding = model.encode(seed_text, convert_to_tensor=True)
    external_embeddings = model.encode(external_texts, convert_to_tensor=True)

    cos_scores = util.pytorch_cos_sim(seed_embedding, external_embeddings)[0]
    print("Cosine scores:")
    print(cos_scores)
    top_results = torch.topk(cos_scores, k=top_n)
    print("Top results:")
    print(top_results)
    similar_texts = [external_texts[idx] for idx in top_results[1]]
    
    return similar_texts


def generate_context(query, external_texts):
    # Retrieve similar instances
    similar_texts = retrieve_similar_instances(query, external_texts)
    print("Retrieved similar texts:")
    print(similar_texts)
    print("---------------------")
    retrieved_context = " ".join(similar_texts)
    return retrieved_context

def generate_response(query, retrieved_context):
    GPT4V_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    print("API KEY ", GPT4V_KEY)
    headers = {
        "Content-Type": "application/json",
        "api-key": GPT4V_KEY,
    }
    


    payload = {
        "messages": [
            {'role': 'system', 'content': "You are a data augmentation tool that helps users to generate similar texts based on structure"},
            {'role': 'system', 'content': "The output format you should follow is the following: Text: <text> Entities: <entities>, where <entities> consists of a list of <entity> : (entity_type), separated by ;"},
            {'role': 'user', 'content': f"Seed Data: {query}\nRetrieved Context: {retrieved_context}\nTask: Generate similar medical texts with the same kind of entities and retrieve only the text in which the entities appear"}
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }
    GPT4V_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    try:
        response = requests.post(GPT4V_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")
    response_json = json.loads(response.content)
    answer = response_json['choices'][0]['message']['content']
    return answer

def process_response(response,data):

    # Dividir la respuesta en bloques de texto
    texts = response.split("Text:")
    texts = [text.strip() for text in texts if text.strip()]

    for text in texts:
        text_parts = text.split("Entities:")
        if len(text_parts) == 2:
            text_content = text_parts[0].strip()
            entities_content = text_parts[1].strip()
            entities_lines = entities_content.split("\n")
            entities = ", ".join([line.strip() for line in entities_lines if line.strip()])
            # Añadir un nuevo diccionario a la lista de datos
            data.append({"Text": text_content, "Entities": entities})

    return data

def merge_csv_files(pattern_num, output_file):
    # Lista para almacenar los DataFrames de cada archivo CSV
    all_dataframes = []
    
    # Iterar sobre los archivos que siguen el patrón clinical_data_rada_pX_{i}.csv
    for i in range(10):
        filename = f'Pattern_{pattern_num}/clinical_data_rada_p{pattern_num}_{i}.csv'
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            all_dataframes.append(df)
        else:
            print(f"File {filename} does not exist and will be skipped.")
    
    # Concatenar todos los DataFrames en uno solo
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Guardar el DataFrame combinado en un nuevo archivo CSV
    combined_df.to_csv(f'Pattern_{pattern_num}/{output_file}', index=False)
    print(f"All files have been merged into Pattern_{pattern_num}/{output_file}")

# Sample external texts for retrieval
external_texts = pd.read_csv("AllclinicalData.csv")["Clinical notes"].tolist()

def process_files_for_pattern(pattern_num):
    # Leer los archivos Pattern#XSeeds.csv y Pattern#XSeedsWithEntities.csv desde la carpeta Pattern_X
    seeds_df = pd.read_csv(f'Pattern_{pattern_num}/Pattern#{pattern_num}Seeds.csv', header=None)
    entities_df = pd.read_csv(f'Pattern_{pattern_num}/Pattern#{pattern_num}SeedsWithEntities.csv', header=None)

    # Asegurarse de que ambos DataFrames tienen al menos 10 filas
    if len(seeds_df) < 10 or len(entities_df) < 10:
        raise ValueError(f"Los archivos en Pattern_{pattern_num} deben contener al menos 10 filas.")

    # Iterar sobre las primeras 10 filas
    for i in range(10):
        seed_query = seeds_df.iloc[i, 0].strip()  # Suponiendo que el texto está en la primera columna
        context = generate_context(seed_query, external_texts)
        
        entity_query = entities_df.iloc[i, 0].strip()  # Suponiendo que el texto está en la primera columna
        response_list = []

        for _ in range(10):  # Llamar a generate_response 10 veces con el mismo contexto
            response = generate_response(entity_query, context)
            print(response)
            clinicaldata = process_response(response, response_list)

        # Convertir la lista de respuestas en un DataFrame y guardarla en un archivo CSV
        df = pd.DataFrame(clinicaldata)
        df.to_csv(f'Pattern_{pattern_num}/clinical_data_rada_p{pattern_num}_{i}.csv', index=False)

# Iterar sobre el rango de patrones del 1 al 7
for pattern_num in range(1, 7):
    # Procesar archivos para cada patrón dado
    process_files_for_pattern(pattern_num)

    # Nombre del archivo de salida para cada patrón
    output_file = f'Pattern{pattern_num}NER.csv'
    merge_csv_files(pattern_num, output_file)
