from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
from processor import MediaProcessor
from celery.result import AsyncResult
from worker import celery_app
from worker import generate_media_task
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class GenerationRequest(BaseModel):
    user_id: str
    prompt: str
    media_type: str

app = FastAPI(title="Avart AI Global Backend")

# Add CORS Middleware right below app initialization
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from payment import router as payment_router 
app.include_router(payment_router)

# Initialize the Media Processor for handling user uploads
processor = MediaProcessor(upload_dir="./uploads")
@app.get("/")
async def serve_index():
    return FileResponse("index.html")

# User wallet stored in USD for worldwide accessibility
users_db = {"123": {"email": "creator@avart.ai", "balance_usd": 100.0}}

@app.post("/api/generate")
async def request_generation(req: GenerationRequest):
    # Bypass user lookup for testing
    user = {"email": "creator@avart.ai", "balance_usd": 100.0}

    # Sustainable global pricing in USD
    pricing_usd = {
        "basic_image": 0.05,
        "pro_image": 0.10,
        "ai_video": 0.75
    }
    
    cost = pricing_usd.get(req.media_type)
    if not cost:
        raise HTTPException(status_code=400, detail="Invalid media type selected.")
    
    if user["balance_usd"] < cost:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient wallet balance. This generation costs ${cost}. Please fund your account."
        )
    
    # Deduct USD cost
    user["balance_usd"] = round(user["balance_usd"] - cost, 4)
    job_id = str(uuid.uuid4())
    
    # Dispatch to background celery worker
    generate_media_task.delay(job_id, req.media_type, req.prompt)
    
    return {
        "status": "success",
        "message": f"Processing your {req.media_type} on Avart AI...",
        "job_id": job_id,
        "charged_usd": cost,
        "remaining_balance_usd": user["balance_usd"]
    }

@app.post("/api/v1/media/upload")
async def upload_and_process_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    # Validate accepted formats for background extraction/feature analysis
    allowed_extensions = (".mp4", ".mov", ".avi", ".mkv", ".jpg", ".jpeg", ".png")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="Unsupported file format.")
    
    # Save the file securely via the processor class
    file_path = await processor.save_upload(file)
    
    # Queue background analysis for feature and background extraction
    background_tasks.add_task(processor.analyze_media, file_path)
    
    return {
        "status": "success",
        "message": "Media uploaded and queued for background feature analysis.",
        "filename": file.filename,
        "path": file_path
    }
@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    # Retrieve task state using Celery's result backend
    task_result = AsyncResult(job_id, app=celery_app)
    
    if task_result.state == 'PENDING':
        response = {
            "job_id": job_id,
            "status": "processing",
            "message": "Job is currently in the queue or rendering."
        }
    elif task_result.state == 'SUCCESS':
        response = {
            "job_id": job_id,
            "status": "completed",
            "result": task_result.result
        }
    else:
        response = {
            "job_id": job_id,
            "status": str(task_result.state),
            "error": str(task_result.info)
        }
    return response



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
