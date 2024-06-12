import streamlit as st
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Configurar las credenciales de Google Sheets
def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Especifica la ruta completa al archivo 'credentials.json'
    creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client

# Inicializar configuración
CLIENT_ID = '117378'
CLIENT_SECRET = '91eeae97f0721dbe32a37d93100948af876b10ec'
REDIRECT_URI = 'http://localhost:8501'

# URL de autorización
AUTHORIZATION_URL = (
    f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}"
    f"&response_type=code&redirect_uri={REDIRECT_URI}"
    f"&approval_prompt=force&scope=profile:read_all,activity:read_all"
)

# Crear la aplicación en Streamlit
st.title("Strava API App")
st.write("Please authorize the app by clicking the button below!")

# Paso 1: Autorización del usuario
if st.button('Conectar con Strava'):
    auth_url = AUTHORIZATION_URL
    st.markdown(f'[Conectar con Strava]({auth_url})', unsafe_allow_html=True)
    st.write('Conectando con Strava...')

# Paso 2: Manejar redirección y obtener código de autorización
query_params = st.experimental_get_query_params()
code_input = query_params.get('code', [None])[0]

if code_input:
    # Paso 3: Intercambiar el código de autorización por un token de acceso
    TOKEN_URL = 'https://www.strava.com/api/v3/oauth/token'
    TOKEN_DATA = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code_input,
        'grant_type': 'authorization_code'
    }
    TOKEN_HEADERS = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        token_response = requests.post(TOKEN_URL, data=TOKEN_DATA, headers=TOKEN_HEADERS)
        token_response.raise_for_status()
        strava_token = token_response.json()

        # Obtener el token de acceso
        ACCESS_TOKEN = strava_token.get('access_token')

        if ACCESS_TOKEN:
            # Paso 4: Obtener los datos del perfil del usuario
            ATHLETE_URL = "https://www.strava.com/api/v3/athlete"
            headers = {
                'Authorization': f"Bearer {ACCESS_TOKEN}"
            }
            athlete_response = requests.get(ATHLETE_URL, headers=headers)
            athlete_response.raise_for_status()
            athlete = athlete_response.json()

            # Mostrar la información del perfil del usuario
            st.write('===== USER PROFILE =====')
            st.json(athlete)

            # Paso 5: Guardar los datos en Google Sheets
            client = get_gsheet_client()
            sheet = client.open("StravaUserData").sheet1  # Abrir la hoja de cálculo
            # Añadir una nueva fila con los datos del usuario y el token
            sheet.append_row([
                athlete.get('id'),
                athlete.get('username'),
                athlete.get('firstname'),
                athlete.get('lastname'),
                athlete.get('city'),
                athlete.get('state'),
                athlete.get('country'),
                athlete.get('sex'),
                athlete.get('profile'),
                ACCESS_TOKEN  # Guardar el token de acceso
            ])
            st.write('Datos del usuario y token guardados en Google Sheets.')

            # Obtener la actividad más reciente del usuario
            ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
            activities_response = requests.get(ACTIVITIES_URL, headers=headers)
            activities_response.raise_for_status()
            activities = activities_response.json()

            if activities:
                # Obtener el id de la primera actividad
                ACTIVITY_ID = activities[0]['id']

                # Paso 6: Obtener el flujo de actividad
                STREAM_URL = (
                    f"https://www.strava.com/api/v3/activities/{ACTIVITY_ID}/streams"
                    f"?types=altitude,time,latlng"
                )
                stream_response = requests.get(STREAM_URL, headers=headers)
                stream_response.raise_for_status()
                stream = stream_response.json()

                # Mostrar los datos del flujo de actividad
                st.write('===== ACTIVITY STREAM =====')
                if stream:
                    for data_stream in stream:
                        st.write(f"Type: {data_stream['type']}")
                        st.write(f"Data: {data_stream['data']}")
                        st.write(f"Series type: {data_stream['series_type']}")
                        st.write(f"Original size: {data_stream['original_size']}")
                        st.write(f"Resolution: {data_stream['resolution']}")
                else:
                    st.write('No stream data found for this activity.')
            else:
                st.write('No activities found.')

        else:
            st.write('Failed to retrieve access token. Please check your credentials and authorization code.')
            st.json(strava_token)  # Mostrar la respuesta para depuración
    except requests.exceptions.RequestException as e:
        st.write(f"An error occurred: {e}")
else:
    st.write("Please authorize the app and then input the code from the URL after redirecting.")
