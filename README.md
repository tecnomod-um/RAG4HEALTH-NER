# RAG4HEALTH-NER
The objective is to generate an annotated corpus of data for being used to train a NER model based on predefined textual medical patterns and Retrieval Augmented Generation (RAG).

We have focused on annotating the following entities:
- Procedure
- Finding
- BodyStructure
- Qualifier (Severity, Temporal, Contextual)
- Person
- ObservableEntity
- NumericValue


For that we have used RAG (Retrieval Augmented Generation) with a LLM. The following steps have been carried out:
- For increasing the variety of the generated texts we have used CANTEMIST and texts from Physical examitation and History of present illness sections of MIMIC IV (sentence level)
- For generating the texts, we have used seven typical clinical text patterns as seeds, and 10 seeds for each pattern
- For each seed, together with the context from the external processed corpus from CANTEMIST and MIMIC IV, we have prompt GPT-4 10 times

We have made a responsible use of MIMIC data by using Azure OpenAI service.

Example of one of the patterns seeds, annotated with the entities:

_The uncle mentioned that his nephew had been under observation for 4 days due to a suspected allergy when he was nine years old where "uncle" and "nephew" are (Person); "under observation" is a (Procedure); "suspected allergy" is a (Finding) and  "suspected" is a (Contextual Qualifier); "for 4 days" and "nine years old" are (Temporal Qualifier)_


You will not find the corpus with CANTEMIST and MIMIC IV in this repository due to data privacy. However, you can access the code to preprocess them (ModificaCANTEMIST, ExtractFromMIMIC), as well as the code to run in Azure GPT-4 (PruebaAzure). Finally you can access to the seeds from each of the seven patterns, as well as the annotated corpora generated.

The evaluation results are being processed and will be published as a scientific publication.

# Acknowledgemnts
- This reposity contains work done during the research stay of Catalina Martínez Costa at Stefan Schulz's group at the department of Medical informatics, statistics and documentation (Medical University of Graz).

- Este trabajo es resultado de la estancia 22206/EE/23 financiada por la Fundación Séneca-Agencia de Ciencia y Tecnología de la Región de Murcia (https://www.fseneca.es/) con cargo al Programa Regional de Movilidad, Colaboración e Intercambio de Conocimiento “Jiménez de la Espada”.
![Fundación Séneca](https://www.fseneca.es/web/sites/all/themes/fuse17/img/fseneca-color.svg)
![Región de Murcia](https://www.carm.es/web/imagen?ALIAS=IMGR4&IDIMAGEN=9074)
