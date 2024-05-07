import streamlit as st
import json
import requests
import webbrowser

# Initial Settings
CLIENT_ID = '117378'
CLIENT_SECRET = '91eeae97f0721dbe32a37d93100948af876b10ec'
REDIRECT_URI = 'http://localhost/'

# Authorization URL
AUTHORIZATION_URL = f'https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}' \
                   f'&response_type=code&redirect_uri={REDIRECT_URI}' \
                   f'&approval_prompt=force' \
                   f'&scope=profile:read_all,activity:read_all'

# Create a Streamlit app
st.title("Strava API App")
st.write("Please authorize the app and copy the generated code!")

if st.button('Conectar con Strava'):
    # Redirigir a la página de autorización de Strava
    webbrowser.open(AUTHORIZATION_URL)
    st.write('Conectando con Strava...')

# Create a button to submit the code
if st.button("Submit"):
    # Get the access token
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
    token_response = requests.post(TOKEN_URL, data=TOKEN_DATA, headers=TOKEN_HEADERS)

    # Save json response as a variable
    strava_token = token_response.json()

    with open('strava_token.json', 'w') as outfile:
        json.dump(strava_token, outfile)

    # Read the token from the saved file
    with open('strava_token.json', 'r') as token:
        data = json.load(token)

    # Get the access token
    ACCESS_TOKEN = data['access_token']

    # Build the API url to get activities data
    ACTIVITIES_URL = f"https://www.strava.com/api/v3/athlete/activities?" \
              f"access_token={ACCESS_TOKEN}"
    st.write('RESTful API:', ACTIVITIES_URL)

    # Get the response in json format
    activities_response = requests.get(ACTIVITIES_URL)
    activities = activities_response.json()

    # Get the id of the activity
    ACTIVITY_ID = activities[0]['id']

    # Build the API url to get activity stream data
    STREAM_URL = f"https://www.strava.com/api/v3/activities/{ACTIVITY_ID}/streams?" \
              f"types=altitude,time,latlng" \
              f"&access_token={ACCESS_TOKEN}"
    st.write('RESTful API:', STREAM_URL)

    # Get the response in json format
    stream_response = requests.get(STREAM_URL)
    stream = stream_response.json()

    # Print out the retrieved information
    st.write('='*5, 'ACTIVITY STREAM', '='*5)
    st.write('Type:', stream[0]['type'])
    st.write('Data:', stream[0]['data'])
    st.write('Series type:', stream[0]['series_type'])
    st.write('Original size:', stream[0]['original_size'])
    st.write('Resolution:', stream[0]['resolution'])
