from fastapi import FastAPI
from route import test, llm, upload, session
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.include_router(test.router)
app.include_router(llm.router)
app.include_router(upload.router)
app.include_router(session.router)

@app.get("/")
async def root():
    return {"message": "SalesCoach API is running"}