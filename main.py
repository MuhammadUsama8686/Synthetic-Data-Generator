# main.py
from fastapi import FastAPI, Request, HTTPException  # Add HTTPException import
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from typing import List
import asyncio
from models import DatasetRequest, DatasetResponse
from generator import generate_dataset

app = FastAPI(title="SynthGenAI Dataset Generator")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-dataset/", response_model=DatasetResponse)
async def generate_dataset_endpoint(request: DatasetRequest):
    try:
        dataset = await generate_dataset(
            dataset_type=request.dataset_type,
            topic=request.topic,
            language=request.language,
            num_samples=request.num_samples,
            additional_description=request.additional_description,
            domains=request.domains
        )
        return DatasetResponse(data=dataset)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dataset: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)