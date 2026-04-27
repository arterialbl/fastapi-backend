from fastapi import FastAPI
from routers import users, auth

app = FastAPI()


@app.get("/")
def root():
    return {"message": "FastAPI + PostgreSQL works"}


app.include_router(auth.router)
app.include_router(users.router)