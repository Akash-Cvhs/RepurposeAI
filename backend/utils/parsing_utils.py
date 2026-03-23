import PyPDF2
from pathlib import Path
from typing import Optional

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """Extract text content from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
    
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def parse_structured_data(text: str, data_type: str) -> dict:
    """Parse structured data from text based on type"""
    
    if data_type == "clinical_trial":
        return parse_clinical_trial_data(text)
    elif data_type == "patent":
        return parse_patent_data(text)
    else:
        return {"raw_text": text}

def parse_clinical_trial_data(text: str) -> dict:
    """Parse clinical trial information from text"""
    # Simple parsing logic - can be enhanced with NLP
    data = {
        "title": "",
        "phase": "",
        "status": "",
        "condition": "",
        "intervention": "",
        "sponsor": ""
    }
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip().lower()
        if 'title:' in line:
            data["title"] = line.split('title:')[1].strip()
        elif 'phase' in line:
            data["phase"] = line
        elif 'status:' in line:
            data["status"] = line.split('status:')[1].strip()
    
    return data

def parse_patent_data(text: str) -> dict:
    """Parse patent information from text"""
    data = {
        "title": "",
        "patent_number": "",
        "filing_date": "",
        "expiration_date": "",
        "assignee": "",
        "abstract": ""
    }
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip().lower()
        if 'patent number:' in line:
            data["patent_number"] = line.split('patent number:')[1].strip()
        elif 'title:' in line:
            data["title"] = line.split('title:')[1].strip()
        elif 'assignee:' in line:
            data["assignee"] = line.split('assignee:')[1].strip()
    
    return data