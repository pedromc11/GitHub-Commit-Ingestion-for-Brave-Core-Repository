import requests
import pymongo
import time
from pymongo import MongoClient

# Datos del usuario y claves

username = 'YOUR_GITHUB_USERNAME'
token = 'YOUR_GITHUB_TOKEN'
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'


# Ubicacion BBDD MongoDB
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'db_practicas3y4'
COLLECTION_COMMITS = 'prueba'
connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
collCommits = connection[DB_NAME][COLLECTION_COMMITS]

# Datos del proyecto
owner = 'brave'
repo = 'brave-core'
date = '2023-03-20T00:00:00Z'

# Cabeceras y datos de las peticiones
query = {'client_id': client_id, 'client_secret': client_secret}
auth_headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github+json'}
commits_per_page = 100

# Eliminar todos los documentos de la colección cada vez que se inicie
delete_result = collCommits.delete_many({})
print(f"Se han eliminado {delete_result.deleted_count} documentos.")

# Declaración de variables
current_page = 1 # Página de commits actual
remaining_commits = True # ¿Sigue habiendo commits?
insert_commit_count = 0 # Número de commits insertados

# Obtención del rate limit
def obtenerRateLimit():
    rateLimit_url = 'https://api.github.com/rate_limit'
    rateLimit_response = requests.get(rateLimit_url, headers=auth_headers, params=query)
    rateLimit_dict = rateLimit_response.json()
    
    #print(rateLimit_dict)
    print(f"Rate limit: {rateLimit_dict['resources']['core']['limit']}")
    print(f"Usado: {rateLimit_dict['resources']['core']['used']}")
    print(f"Tiempo de reset: {rateLimit_dict['resources']['core']['reset']}")
    
    return rateLimit_dict

def pedirCommits():
    # Definición de peticion
    commitsRequest_url = 'https://api.github.com/repos/{}/{}/commits?page={}&per_page={}&since={}'
    commitsRequest_url_params = commitsRequest_url.format(owner, repo, current_page, commits_per_page, date)

    # Petición de commits
    commitsRequest_response = requests.get(commitsRequest_url_params, headers=auth_headers, params=query)

    return commitsRequest_response

def pedirDatosCommit(sha_commit):
    # Petición de información del commit
    commitRequest_url = 'https://api.github.com/repos/{}/{}/commits/{}'
    commitRequest_url_params = commitRequest_url.format(owner, repo, sha_commit)
    commitRequest_response = requests.get(commitRequest_url_params, headers=auth_headers, params=query)
    
    return commitRequest_response

def esperarTiempoReset():
    ahora = int(time.time()) # Segundos transcurridos desde el 1 de enero de 1970 a las 00:00:00 UTC hasta la fecha y hora actual
    reset_seconds = int(rate_limit['resources']['core']['reset']) # Segundos transcurridos desde el 1 de enero de 1970 a las 00:00:00 UTC hasta la fecha y hora que se restauran las peticiones
    tiempo_reset = reset_seconds - ahora # Segundos restantes para restablecer peticiones
    tiempo_reset_minutos = tiempo_reset/60
    print(f"Minutos para reset: {int(tiempo_reset_minutos)} minutos aproximadamente")

    # Cuenta atrás hasta el restablecimiento de peticiones
    tiempo_reset += 10 # Margen adicional
    tiempo_reset_aux = tiempo_reset
    for i in range(tiempo_reset):
        time.sleep(1)
        tiempo_reset_aux -= 1
        print(f"Segundos restantes: {tiempo_reset_aux}")

def insertarInfoYEnMongo(commit, commit_response):
    commit['projectId'] = repo

    if commit_response.status_code == 200:
        commit_dict = commit_response.json()

        commit['stats'] = commit_dict['stats']
        commit['files'] = commit_dict['files']

        collCommits.insert_one(commit)

        global insert_commit_count
        insert_commit_count += 1

        print(f"Commit {insert_commit_count} insertado")
    else:
        print(f"Error al obtener el commit: {commit_response.status_code} - {commit_response.reason}")
        remaining_commits = False

# Obtener rate limit inicial
rate_limit = obtenerRateLimit()

# Mientras haya commits restantes por insertar
while remaining_commits:
    try:
        commits_response = pedirCommits()
        commits_response.raise_for_status()

        if commits_response.status_code == 200:
            print(f"Solicitud de la página {current_page} correcta")
            commits_dict = commits_response.json()
            page_commits = len(commits_dict)
            print(f"Página con {page_commits} commits")
            if page_commits != 0:
                for commit in commits_dict:
                    try:
                        # Petición de los datos del commit
                        commit_response = pedirDatosCommit(commit['sha'])
                        commit_response.raise_for_status()

                        # Inserción de datos adicionales e inserción del commit en MongoDB
                        insertarInfoYEnMongo(commit, commit_response)
                        
                    except requests.exceptions.HTTPError as error:
                        if error.response.status_code == 403 and "API rate limit exceeded" in error.response.text:
                            print("Se ha superado el límite de solicitudes.")

                            # Esperar hasta que se restablezcan las peticiones
                            esperarTiempoReset()

                            # Calcular nuevo rate limit
                            rate_limit = obtenerRateLimit()

                            # Volver a hacer la petición de los datos del commit
                            commit_response = pedirDatosCommit(commit['sha'])

                            # Inserción de datos adicionales e inserción del commit en MongoDB
                            insertarInfoYEnMongo(commit, commit_response)

                current_page += 1
                
            else:
                print("Nueva página en blanco. Todos los commits insertados.")
                remaining_commits = False
        else:
            print(f"Error al obtener la página {current_page}: {commits_response.status_code} - {commits_response.reason}")
            remaining_commits = False
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 403 and "API rate limit exceeded" in error.response.text:
            print("Se ha superado el límite de solicitudes.")
            esperarTiempoReset()

print(f"Nº de commits insertados: {insert_commit_count}")