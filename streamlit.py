import streamlit as st
import json
import requests
from urllib.parse import urlencode, urlparse, parse_qs

# Initial Settings
CLIENT_ID = '117378'
CLIENT_SECRET = '91eeae97f0721dbe32a37d93100948af876b10ec'
REDIRECT_URI = 'http://localhost:8501'

# Authorization URL
AUTHORIZATION_URL = (
    f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}"
    f"&response_type=code&redirect_uri={REDIRECT_URI}"
    f"&approval_prompt=force&scope=profile:read_all,activity:read_all"
)

# Create a Streamlit app
st.title("Strava API App")
st.write("Please authorize the app by clicking the button below!")

# Step 1: User Authorization
if st.button('Conectar con Strava'):
    auth_url = AUTHORIZATION_URL
    st.markdown(f'[Conectar con Strava]({auth_url})', unsafe_allow_html=True)
    st.write('Conectando con Strava...')

# Step 2: Handle redirect and get authorization code
query_params = st.experimental_get_query_params()
code_input = query_params.get('code', [None])[0]

if code_input:
    # Step 3: Exchange the authorization code for an access token
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

        # Get the access token
        ACCESS_TOKEN = strava_token.get('access_token')

        if ACCESS_TOKEN:
            # Step 4: Get Activities
            ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
            headers = {
                'Authorization': f"Bearer {ACCESS_TOKEN}"
            }
            activities_response = requests.get(ACTIVITIES_URL, headers=headers)
            activities_response.raise_for_status()
            activities = activities_response.json()

            if activities:
                # Get the id of the first activity
                ACTIVITY_ID = activities[0]['id']

                # Step 5: Get Activity Stream Data
                STREAM_URL = (
                    f"https://www.strava.com/api/v3/activities/{ACTIVITY_ID}/streams"
                    f"?types=altitude,time,latlng"
                )
                stream_response = requests.get(STREAM_URL, headers=headers)
                stream_response.raise_for_status()
                stream = stream_response.json()

                # Print out the retrieved information
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
            st.json(strava_token)  # Display the response for debugging
    except requests.exceptions.RequestException as e:
        st.write(f"An error occurred: {e}")
else:
    st.write("Please authorize the app and then input the code from the URL after redirecting.")
