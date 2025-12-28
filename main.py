import logging
import json
from pathlib import Path
from llm.client import call_gemini
from llm.prompt_builder import build_prompt
from llm.response_validator import validate_model_response
from file_io.file_reader import read_document_as_text
from file_io.document_detector import auto_detect_resume
from file_io.document_editor import duplicate_document, apply_replacements
from file_io.pdf_generator import generate_pdf

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
        
        # Detect resume file automatically
        data_dir = BASE_DIR / "data"
        logger.info(f"Auto-detecting resume file in {data_dir}...")
        resume_path = auto_detect_resume(data_dir)
        logger.info(f"Found resume file: {resume_path.name}")
        
        # Read job offer
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
        
        logger.info("Gemini found the following replacements:")
        print(json.dumps(validated_json, indent=2, ensure_ascii=False))
        
        # Duplicate document with new name
        logger.info(f"Duplicating resume file with company name: {company_name}...")
        duplicated_path = duplicate_document(resume_path, company_name)
        logger.info(f"Created duplicate: {duplicated_path.name}")
        
        # Apply replacements to the duplicated document
        logger.info("Applying replacements to document...")
        apply_replacements(duplicated_path, validated_json)
        logger.info("Replacements applied successfully")
        
        # Generate PDF
        logger.info("Generating PDF from edited document...")
        try:
            pdf_path = generate_pdf(duplicated_path)
            logger.info(f"PDF generated successfully: {pdf_path.name}")
        except RuntimeError as pdf_error:
            logger.warning(f"PDF generation failed: {pdf_error}")
            logger.info("Document editing completed, but PDF generation was skipped")
            pdf_path = None
        
        # Summary
        logger.info("=" * 60)
        logger.info("Process completed successfully!")
        logger.info(f"Edited document: {duplicated_path.name}")
        if pdf_path:
            logger.info(f"PDF file: {pdf_path.name}")
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
