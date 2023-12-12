import json
import os
import openai
from PyPDF2 import PdfFileReader, PdfMerger

def create_assistant(client):
  assistant_file_path = 'assistant.json'

  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    file = client.files.create(file=open("1 Caso La Valluna.pdf", "rb"),
                               purpose='assistants')

    assistant = client.beta.assistants.create(name="MBA Copilot",
                                              instructions="""
          MBA Copilot está especializado en casos de estudio de MBA. Utiliza ejemplos de la base de datos para enriquecer sus respuestas. Cuando se enfrenta a preguntas no relacionadas con MBA o gestión de empresas, responde con "No relacionado con Master of Business Administration". Mantiene un tono profesional y accesible, centrandose en temas de MBA y discutiendo sectores empresariales relacionados. Diseñado para un público universitario en Bolivia, se mantiene dentro de su especialización, evitando temas ajenos a los estudios de MBA y permitiendo algunas conversaciones casuales relacionadas. Presenta un estilo amigable y profesional. La herramienta de 'dalle' no se utiliza para crear imágenes que no estén relacionadas con casos de MBA. Al abordar los casos de estudio de MBA, presentará siempre la información en una tabla de dos columnas, donde la columna "Elemento" contendrá los campos "antecedentes", "Diagnostico", "Problema Central", "Actores y Objetivos", "Alternativas", "pros", "contras", y "plan de acción", y la columna "Contenido" incluirá las respuestas asociadas a cada campo.
          """,
                                              model="gpt-4-1106-preview",
                                              tools=[{
                                                  "type": "retrieval"
                                              }],
                                              file_ids=[file.id])

    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id


#Funcion que crea una lista de listas de nombres, cada lista de nombres contiene el grupo de archivos que se uniran mas tarde en 1 solo
def gruposDeArchivos500MBs(carpeta):
    MAX_SIZE_MB = 500 * 1024 * 1024  # 500 MB en bytes
    archivos = os.listdir(carpeta)
    grupos = []
    grupo_actual = []
    tamaño_actual = 0

    for archivo in archivos:
        ruta_completa = os.path.join(carpeta, archivo)
        tamaño_archivo = os.path.getsize(ruta_completa)
        if tamaño_actual + tamaño_archivo > MAX_SIZE_MB: #Cuando el grupo superaria los 500 MBs con el archivo, entonces el grupo se añade a grupos y se crea un nuevo grupo
            grupos.append(grupo_actual)
            grupo_actual = [archivo]
            tamaño_actual = tamaño_archivo
        else:
            grupo_actual.append(archivo) #Solo agrega el archivo al grupo
            tamaño_actual += tamaño_archivo # Y modifica el tamaño actual

    if grupo_actual: # Verifica si tiene elementos, si es asi entonces se lo agrega a grupos
        grupos.append(grupo_actual)

    return grupos

# Uso de la función
grupos_casos_de_estudio = gruposDeArchivos500MBs("casos de estudio")
grupos_matrices_casos_de_estudio = gruposDeArchivos500MBs("matrices")

def unirArchivos(listaDeArchivos, nombreCarpeta):
    # Crear el directorio 'knowledge' si no existe
    os.makedirs('knowledge', exist_ok=True)

    # Encontrar el siguiente nombre de archivo disponible
    contador = 1
    while os.path.exists(f'knowledge/{contador}_{nombreCarpeta}.pdf'):
        contador += 1
    nuevo_nombre = f'{contador} {nombreCarpeta}.pdf'

    # Crear un nuevo PDF combinando los archivos de la lista
    merger = PdfMerger()
    for archivo in listaDeArchivos:
        ruta_completa = os.path.join(nombreCarpeta, archivo)
        merger.append(ruta_completa)

    # Guardar el nuevo archivo PDF en la carpeta 'knowledge'
    with open(f'knowledge/{nuevo_nombre}', 'wb') as archivo_salida:
        merger.write(archivo_salida)

    print(f"Archivo {nuevo_nombre} creado en la carpeta 'knowledge'.")

def unirGrupoDeArchivos(listaDeListas, nombreCarpeta):
    for lista in listaDeListas:
        unirArchivos(lista, nombreCarpeta)

#unirGrupoDeArchivos(grupos_casos_de_estudio, "casos de estudio")
# unirGrupoDeArchivos(grupos_matrices_casos_de_estudio, "matrices")

print (grupos_casos_de_estudio)


# Dame una lista de todas las matrices que se hicieron el año 2022
# Dame una lista de casos de estudio que se subieron el año 2022