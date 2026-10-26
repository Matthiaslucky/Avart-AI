from celery import Celery
from model_engine import ModelEngine

celery_app = Celery(
    "avart_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Initialize model engine instance for the worker
engine = ModelEngine()

@celery_app.task(name="tasks.generate_media_task")
def generate_media_task(job_id: str, media_type: str, prompt: str):
    print(f"Starting background job {job_id} for {media_type} with prompt: '{prompt}'")
    
    try:
        if media_type in ["basic_image", "pro_image"]:
            output_path = engine.generate_image(prompt, job_id)
        else:
            # Placeholder or video generation handler
            output_path = f"./outputs/{job_id}.mp4"
            
        return {
            "job_id": job_id, 
            "status": "completed", 
            "result_path": output_path
        }
    except Exception as e:
        return {
            "job_id": job_id,
            "status": "failed",
            "error": str(e)
        }
if __name__ == "__main__":
    import time
    print("Avart AI worker active and listening...")
    while True:
        # worker polling loop
        time.sleep(1)
        
