import streamlit as st
from streamlit_chat import message
import requests

FASTAPI_URL = "http://127.0.0.1:8000/query"

st.set_page_config(page_title="SeaQuiller", page_icon=":bird:")
st.markdown("<h1 style='text-align: center;'>SeaQuiller 🐦</h1>", unsafe_allow_html=True)


if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
if 'db_type' not in st.session_state:
    st.session_state['db_type'] = []
if 'database' not in st.session_state:
    st.session_state['database'] = []
if 'user' not in st.session_state:
    st.session_state['user'] = []
if 'password' not in st.session_state:
    st.session_state['password'] = []
if 'host' not in st.session_state:
    st.session_state['host'] = []
if 'port' not in st.session_state:
    st.session_state['port'] = []


st.sidebar.title("Options")
expander = st.sidebar.expander("Choose Model Params", icon="🤖")
model_name = expander.selectbox("Choose a model:", ("GPT-3.5", "GPT-4"))
api_key = expander.text_input("Enter API Key:", type="password")

db_expander = st.sidebar.expander("Choose Database Params", icon="🗒️")
db_type = db_expander.selectbox("Select DB Type: ", options=['mysql', 'postgresql', 'sqlite', 'mssql', 'oracle'])

if db_type == "sqlite":
    database = db_expander.text_input("Choose a database path: ")
else:
    database = db_expander.text_input("Choose a database path: ")
    user = db_expander.text_input("Enter username: ")
    password = db_expander.text_input("Enter password: ", type="password")
    host = db_expander.text_input("Enter host: ")
    port = db_expander.text_input("Enter port: ")


clear_button = st.sidebar.button("Clear Conversation", key="clear")

# Map model names to OpenAI model IDs
if model_name == "GPT-3.5":
    model = "gpt-3.5-turbo"
else:
    model = "gpt-4"

# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a SQL expert with a strong attention to detail"}
    ]
    st.session_state['db_type'] = []
    st.session_state["database"] = []
    st.session_state['user'] = []
    st.session_state['password'] = []
    st.session_state['host'] = []
    st.session_state['port'] = []


def generate_response(prompt):
    if prompt and db_type:
        # Prepare the JSON payload
        payload = {
            "question": prompt,
            "model": model,
            "db_type": db_type,
            "database": database,
            "api_key": api_key
        }

        # Send POST request to FastAPI
        try:
            response = requests.post(FASTAPI_URL, json=payload)

            if response.status_code == 200:
                data = response.json()
                return data['response']
                # st.success(data['response'])
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please fill in all fields.")


response_container = st.container()
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['db_type'].append(db_type)
        st.session_state["database"].append(database)


if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
