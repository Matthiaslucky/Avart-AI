import os
from fastapi import UploadFile

class MediaProcessor:
    def __init__(self, upload_dir: str = "./uploads"):
        self.upload_dir = upload_dir
        # Ensure the uploads directory exists on disk
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> str:
        """
        Saves an uploaded video or image file asynchronously to the local storage directory.
        """
        file_path = os.path.join(self.upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        return file_path

    def analyze_media(self, file_path: str) -> dict:
        """
        Analyzes the uploaded asset to determine its media type and 
        prepares it for background extraction or feature detection tasks.
        """
        # Determine if the asset is a video based on common extensions
        is_video = file_path.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))
        media_type = "video" if is_video else "image"
        
        # Placeholder log/result for background/feature processing pipeline
        analysis_result = {
            "file_path": file_path,
            "type": media_type,
            "status": "ready_for_background_extraction"
        }
        
        print(f"Analyzed {media_type}: {file_path}")
        return analysis_result
