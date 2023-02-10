from fastapi import FastAPI

from riot_oauth2 import Client

app = FastAPI(title="Riot OAuth2 Example")
from fastapi import HTTPException

client = Client(
    client_id='your client_id', client_secret='your client_secret', redirect_uri='http://localhost:8000/callback'
)


@app.get("/oauth")
async def login() -> str:
    url = client.get_oauth_url()
    return '<a href="' + url + '">Sign In</a>'


@app.get("/callback")
async def callback(code: str) -> str:
    try:
        token = await client.authorization(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    else:
        return '<pre>' + str(token) + '</pre>'
