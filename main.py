from fastapi import FastAPI
from routes import test , llm
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.include_router(test.router)
app.include_router(llm.router)
@app.get("/")
async def root():
    return {"message": "Hello World"}