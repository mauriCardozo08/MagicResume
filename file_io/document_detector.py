from pathlib import Path


def auto_detect_resume(data_dir: Path) -> Path:
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")
    
    if not data_dir.is_dir():
        raise ValueError(f"Path is not a directory: {data_dir}")
    
    docx_files = list(data_dir.glob("*.docx"))
    odt_files = list(data_dir.glob("*.odt"))
    
    all_resumes = docx_files + odt_files
    
    if len(all_resumes) == 0:
        raise FileNotFoundError(
            f"No resume file found in {data_dir}. "
            "Please ensure there is a .docx or .odt file in the data directory."
        )
    
    if len(all_resumes) > 1:
        file_list = ", ".join([f.name for f in all_resumes])
        raise ValueError(
            f"Multiple resume files found in {data_dir}: {file_list}. "
            "Please ensure there is only one resume file in the data directory."
        )
    
    return all_resumes[0]

