from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import test, llm, upload, session
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(test.router)
app.include_router(llm.router)
app.include_router(upload.router)
app.include_router(session.router)

@app.get("/")
async def root():
    return {"message": "SalesCoach API is running"}