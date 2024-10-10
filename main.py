import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Define a Pydantic model for input validation
class QueryInput(BaseModel):
    question: str = None
    model: str = None
    db_type: str = None
    database: str = None
    user: str = None
    host: str = None
    password: str = None
    api_key: str = None
    port: str = None

# Initialize FastAPI app
app = FastAPI()

# Load the initial config data
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

# Update the config file
def update_config(model: str, 
                  db_type: str, 
                  database: str,
                  user: str,
                  password: str,
                  host: str,
                  port: str,
                  api_key: str):

    with open('config.json', 'r+') as f:
        data = json.load(f)
        data['model'] = model
        data['db_type'] = db_type
        data['database'] = database
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


@app.post("/query")
async def query(input: QueryInput):
    # Extract model, db_type, and database from user input
    model = input.model
    db_type = input.db_type
    database = input.database
    user = input.user
    password = input.password
    host = input.host
    port = input.port
    api_key = input.api_key

    # Update the config with user-provided values
    update_config(model, db_type, database, user, password, host, port, api_key)

    # Load the app from your existing graph module
    from src.graph import get_app
    app_instance = get_app()

    # Invoke the app with the user's question
    messages = app_instance.invoke({"messages": [("user", input.question)]})

    # Extract the final answer
    try:
        json_str = messages["messages"][-1].tool_calls[0]["args"]["final_answer"]
        return {"response": json_str}
    except (IndexError, KeyError):
        raise HTTPException(status_code=500, detail="Failed to retrieve answer.")


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


# import json

# model = "gpt-3.5-turbo"
# db_type = "sqlite"
# database = "./Chinook.db"

# with open('config.json', 'r+') as f:
#         data = json.load(f)

#         data['model'] = model
#         data['db_type'] = db_type
#         data['database'] = database

#         f.seek(0)  
#         json.dump(data, f)
#         f.truncate()

# from graph import get_app

# app = get_app()

# messages = app.invoke(
#     {"messages": [("user", "Who composed the track 'Go Down'?")]}
#     # {"messages": [("user", "Give me the details about composer with most tracks composed")]}
# )

# json_str = messages["messages"][-1].tool_calls[0]["args"]["final_answer"]
# print(json_str)