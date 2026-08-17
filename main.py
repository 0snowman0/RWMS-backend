from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "RWMS API is running"}