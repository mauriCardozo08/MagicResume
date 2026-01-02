import shutil
from pathlib import Path
from .document_editor import sanitize_filename

def prepare_company_directory(data_dir: Path, company_name: str) -> Path:
    sanitized_name = sanitize_filename(company_name)
    if not sanitized_name or sanitized_name == "unknown":
        sanitized_name = "customized"
        
    company_dir = data_dir / sanitized_name
    company_dir.mkdir(parents=True, exist_ok=True)
    
    return company_dir

def save_cover_letter(company_dir: Path, cover_letter_content: str) -> Path:
    file_path = company_dir / "cover_letter.txt"
    file_path.write_text(cover_letter_content, encoding="utf-8")
    return file_path

def copy_resume_to_company_dir(source_path: Path, company_dir: Path, company_name: str) -> Path:
    sanitized_company = sanitize_filename(company_name)
    if not sanitized_company or sanitized_company == "unknown":
        sanitized_company = "customized"
        
    stem = source_path.stem
    suffix = source_path.suffix
    new_name = f"{stem}_{sanitized_company}{suffix}"
    destination_path = company_dir / new_name
    
    shutil.copy2(source_path, destination_path)
    return destination_path
