"""Module for generating PDF files from document formats."""
import subprocess
from pathlib import Path


def _check_libreoffice_available() -> bool:
    """Check if LibreOffice is available in the system."""
    try:
        result = subprocess.run(
            ["libreoffice", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _check_docx2pdf_available() -> bool:
    """Check if docx2pdf module is available."""
    try:
        import docx2pdf
        return True
    except ImportError:
        return False


def generate_pdf_from_docx(docx_path: Path) -> Path:
    """
    Generate a PDF file from a DOCX document.
    
    Args:
        docx_path: Path to the DOCX file
        
    Returns:
        Path to the generated PDF file
        
    Raises:
        FileNotFoundError: If DOCX file doesn't exist
        RuntimeError: If PDF generation fails or no conversion tool is available
    """
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")
    
    pdf_path = docx_path.with_suffix(".pdf")
    
    # Try docx2pdf first (works on Windows with Word or LibreOffice)
    if _check_docx2pdf_available():
        try:
            from docx2pdf import convert
            convert(str(docx_path), str(pdf_path))
            if pdf_path.exists():
                return pdf_path
            else:
                # Conversion didn't create file, likely Word not installed
                raise RuntimeError("docx2pdf conversion completed but PDF file was not created. Microsoft Word may not be installed.")
        except Exception as e:
            # Check if error is related to Word not being installed
            error_str = str(e).lower()
            if "invalid class string" in error_str or "word.application" in error_str or "com_error" in error_str:
                # Word is not installed, try LibreOffice instead
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"docx2pdf requires Microsoft Word which is not installed: {e}, trying LibreOffice...")
            else:
                # Other error, log and try LibreOffice
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"docx2pdf conversion failed: {e}, trying LibreOffice...")
    
    # Try LibreOffice as fallback
    if _check_libreoffice_available():
        try:
            # Use LibreOffice headless mode to convert
            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", str(docx_path.parent),
                    str(docx_path)
                ],
                capture_output=True,
                check=True,
                timeout=30
            )
            if pdf_path.exists():
                return pdf_path
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise RuntimeError(
                f"Failed to convert DOCX to PDF using LibreOffice: {e}. "
                "Please ensure LibreOffice is installed and available in PATH."
            ) from e
    
    # If we get here, no conversion method worked
    raise RuntimeError(
        "No PDF conversion tool available. "
        "Please install either 'docx2pdf' (pip install docx2pdf) or LibreOffice."
    )


def generate_pdf_from_odt(odt_path: Path) -> Path:
    """
    Generate a PDF file from an ODT document.
    
    Args:
        odt_path: Path to the ODT file
        
    Returns:
        Path to the generated PDF file
        
    Raises:
        FileNotFoundError: If ODT file doesn't exist
        RuntimeError: If PDF generation fails or LibreOffice is not available
    """
    if not odt_path.exists():
        raise FileNotFoundError(f"ODT file not found: {odt_path}")
    
    pdf_path = odt_path.with_suffix(".pdf")
    
    # ODT conversion requires LibreOffice
    if not _check_libreoffice_available():
        raise RuntimeError(
            "LibreOffice is required to convert ODT to PDF. "
            "Please install LibreOffice and ensure it's available in PATH."
        )
    
    try:
        # Use LibreOffice headless mode to convert
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(odt_path.parent),
                str(odt_path)
            ],
            capture_output=True,
            check=True,
            timeout=30
        )
        
        if pdf_path.exists():
            return pdf_path
        else:
            raise RuntimeError(f"PDF file was not created: {pdf_path}")
            
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to convert ODT to PDF using LibreOffice: {e}. "
            "Please ensure LibreOffice is installed and available in PATH."
        ) from e
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "PDF conversion timed out. The document may be too large or LibreOffice may be unresponsive."
        )


def generate_pdf(file_path: Path) -> Path:
    """
    Generate a PDF file from a document based on its file extension.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Path to the generated PDF file
        
    Raises:
        ValueError: If file format is not supported for PDF generation
    """
    suffix = file_path.suffix.lower()
    
    if suffix == ".docx":
        return generate_pdf_from_docx(file_path)
    elif suffix == ".odt":
        return generate_pdf_from_odt(file_path)
    else:
        raise ValueError(f"Unsupported file format for PDF generation: {suffix}. Use .docx or .odt")

