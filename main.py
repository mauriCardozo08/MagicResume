import logging
import json
from pathlib import Path
from llm.client import call_gemini
from llm.prompt_builder import build_prompt
from llm.response_validator import validate_model_response
from file_io.file_reader import read_document_as_text
from file_io.document_detector import auto_detect_resume
from file_io.document_editor import apply_replacements


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

def main():
    try:
        logger.info("Starting program...")
        
        data_dir = BASE_DIR / "data"
        logger.info(f"Auto-detecting resume file in {data_dir}...")
        resume_path = auto_detect_resume(data_dir)
        logger.info(f"Found resume file: {resume_path.name}")
        
        job_offer_path = BASE_DIR / "data" / "job.txt"
        if not job_offer_path.exists():
            raise FileNotFoundError(f"Job offer file not found: {job_offer_path}")
        
        logger.info("Reading resume and job offer documents...")
        resume_content = read_document_as_text(str(resume_path))
        job_offer_content = read_document_as_text(str(job_offer_path))
        
        logger.info("Building initial prompt...")
        prompt = build_prompt(resume_content, job_offer_content)
        
        logger.info("Calling Gemini API...")
        response = call_gemini(prompt)
        
        logger.info("Validating and parsing response...")
        validated_json = validate_model_response(response.text)
        
        company_name = validated_json.get("company_name", "unknown")
        logger.info(f"Company name extracted: {company_name}")
        
        logger.info(f"Preparing directory for company: {company_name}...")
        from file_io.file_manager import prepare_company_directory, save_cover_letter, copy_resume_to_company_dir
        
        output_dir = BASE_DIR / "outputs"
        company_dir = prepare_company_directory(output_dir, company_name)
        logger.info(f"Company directory ready: {company_dir}")

        logger.info("Saving cover letter...")
        cover_letter_text = validated_json.get("cover_letter", "")
        cover_letter_path = save_cover_letter(company_dir, cover_letter_text)
        logger.info(f"Cover letter saved to: {cover_letter_path}")
        
        logger.info("Gemini found the following replacements:")
        print(json.dumps(validated_json, indent=2, ensure_ascii=False))
        
        logger.info(f"Copying resume to company directory...")
        duplicated_path = copy_resume_to_company_dir(resume_path, company_dir, company_name)
        logger.info(f"Created working copy: {duplicated_path.name}")
        
        logger.info("Applying replacements to document...")
        apply_replacements(duplicated_path, validated_json)
        logger.info("Replacements applied successfully")
        

        
        logger.info("=" * 60)
        logger.info("Process completed successfully!")
        logger.info(f"Output Directory: {company_dir}")
        logger.info(f"Cover Letter: {cover_letter_path.name}")
        logger.info(f"Edited CV: {duplicated_path.name}")

        logger.info("=" * 60)
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
