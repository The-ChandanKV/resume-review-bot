from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import pdfplumber
from docx import Document
from io import BytesIO
import json

app = FastAPI(title="Resume Review Bot API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file: UploadFile) -> str:
    try:
        with pdfplumber.open(BytesIO(file.file.read())) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

def extract_text_from_docx(file: UploadFile) -> str:
    try:
        doc = Document(BytesIO(file.file.read()))
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing DOCX: {str(e)}")

def analyze_resume(text: str) -> Dict[str, Any]:
    # Mock AI analysis - in a real app, this would use an actual AI model
    word_count = len(text.split())
    return {
        "summary": "This is a mock analysis. In a real implementation, this would contain AI-generated feedback.",
        "metrics": {
            "word_count": word_count,
            "readability_score": min(100, max(10, word_count // 50))  # Mock score
        },
        "suggestions": [
            "Add more technical skills",
            "Include quantifiable achievements",
            "Consider adding a professional summary"
        ]
    }

@app.post("/upload_resume")
async def upload_resume(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    file_extension = file.filename.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        text = extract_text_from_pdf(file)
    elif file_extension in ['docx', 'doc']:
        text = extract_text_from_docx(file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF or DOCX file.")
    
    analysis = analyze_resume(text)
    return {"filename": file.filename, "text": text, "analysis": analysis}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
