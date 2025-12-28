"""Module for duplicating and editing document files with text replacements."""
import re
import shutil
from pathlib import Path
from typing import Dict, List


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be used as a filename.
    Removes or replaces invalid characters.
    
    Args:
        name: String to sanitize
        
    Returns:
        Sanitized string safe for use in filenames
    """
    # Replace invalid characters with underscore
    # Invalid chars: < > : " / \ | ? *
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized


def duplicate_document(source_path: Path, company_name: str) -> Path:
    """
    Duplicate a document file with a new name based on company name.
    
    Args:
        source_path: Path to the source document
        company_name: Company name to append to filename
        
    Returns:
        Path to the duplicated document
        
    Raises:
        FileNotFoundError: If source file doesn't exist
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    # Sanitize company name for filename
    sanitized_company = sanitize_filename(company_name)
    if not sanitized_company or sanitized_company == "unknown":
        sanitized_company = "customized"
    
    # Generate new filename: {stem}_{company_name}{suffix}
    stem = source_path.stem
    suffix = source_path.suffix
    new_name = f"{stem}_{sanitized_company}{suffix}"
    new_path = source_path.parent / new_name
    
    # If file already exists, append a number
    counter = 1
    original_new_path = new_path
    while new_path.exists():
        new_name = f"{stem}_{sanitized_company}_{counter}{suffix}"
        new_path = source_path.parent / new_name
        counter += 1
        if counter > 1000:  # Safety limit
            raise RuntimeError(f"Could not generate unique filename for {original_new_path}")
    
    # Copy the file
    shutil.copy2(source_path, new_path)
    return new_path


def apply_replacements_to_docx(file_path: Path, replacements: Dict[str, List[Dict[str, str]]]) -> None:
    """
    Apply text replacements to a DOCX document.
    
    Args:
        file_path: Path to the DOCX file to edit
        replacements: Dictionary with 'role_replacements' and 'skill_replacements' lists
        
    Raises:
        FileNotFoundError: If file doesn't exist
        RuntimeError: If editing fails
    """
    from docx import Document
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        doc = Document(str(file_path))
        
        # Combine all replacements
        all_replacements = []
        all_replacements.extend(replacements.get("role_replacements", []))
        all_replacements.extend(replacements.get("skill_replacements", []))
        
        if not all_replacements:
            return  # No replacements to apply
        
        # Function to replace text in a paragraph
        def replace_in_paragraph(paragraph, old_text: str, new_text: str) -> bool:
            """Replace text in a paragraph, preserving formatting."""
            if old_text not in paragraph.text:
                return False
            
            # Split paragraph into runs to preserve formatting
            # We need to find and replace while maintaining run formatting
            full_text = paragraph.text
            if old_text in full_text:
                # Clear the paragraph
                paragraph.clear()
                # Split by the old text
                parts = full_text.split(old_text, 1)
                if len(parts) == 2:
                    # Add first part
                    if parts[0]:
                        paragraph.add_run(parts[0])
                    # Add new text
                    paragraph.add_run(new_text)
                    # Add remaining part
                    if parts[1]:
                        paragraph.add_run(parts[1])
                    return True
            return False
        
        # Apply replacements to paragraphs
        for replacement in all_replacements:
            old_text = replacement.get("from", "")
            new_text = replacement.get("to", "")
            
            if not old_text or old_text == new_text:
                continue
            
            # Replace in main paragraphs
            for paragraph in doc.paragraphs:
                replace_in_paragraph(paragraph, old_text, new_text)
            
            # Replace in tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            replace_in_paragraph(paragraph, old_text, new_text)
            
            # Replace in headers and footers
            for section in doc.sections:
                # Header
                if section.header:
                    for paragraph in section.header.paragraphs:
                        replace_in_paragraph(paragraph, old_text, new_text)
                    for table in section.header.tables:
                        for row in table.rows:
                            for cell in row.cells:
                                for paragraph in cell.paragraphs:
                                    replace_in_paragraph(paragraph, old_text, new_text)
                
                # Footer
                if section.footer:
                    for paragraph in section.footer.paragraphs:
                        replace_in_paragraph(paragraph, old_text, new_text)
                    for table in section.footer.tables:
                        for row in table.rows:
                            for cell in row.cells:
                                for paragraph in cell.paragraphs:
                                    replace_in_paragraph(paragraph, old_text, new_text)
        
        # Save the document
        doc.save(str(file_path))
        
    except Exception as e:
        raise RuntimeError(f"Failed to edit DOCX file {file_path}: {e}") from e


def apply_replacements_to_odt(file_path: Path, replacements: Dict[str, List[Dict[str, str]]]) -> None:
    """
    Apply text replacements to an ODT document.
    
    Args:
        file_path: Path to the ODT file to edit
        replacements: Dictionary with 'role_replacements' and 'skill_replacements' lists
        
    Raises:
        FileNotFoundError: If file doesn't exist
        RuntimeError: If editing fails
    """
    from odf.opendocument import load
    from odf.text import P, Span
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        doc = load(str(file_path))
        
        # Combine all replacements
        all_replacements = []
        all_replacements.extend(replacements.get("role_replacements", []))
        all_replacements.extend(replacements.get("skill_replacements", []))
        
        if not all_replacements:
            return  # No replacements to apply
        
        # Function to replace text in a text element
        def replace_in_text_element(element, old_text: str, new_text: str) -> bool:
            """Replace text in an ODF text element."""
            # Get all text nodes
            text_nodes = []
            for node in element.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    text_nodes.append(node)
            
            # Combine text from all nodes
            full_text = "".join([node.data for node in text_nodes])
            
            if old_text in full_text:
                # Clear existing text nodes
                for node in text_nodes:
                    element.removeChild(node)
                
                # Split and recreate with replacement
                parts = full_text.split(old_text, 1)
                if len(parts) == 2:
                    # Add first part as text node
                    if parts[0]:
                        text_node = doc.createTextNode(parts[0])
                        element.appendChild(text_node)
                    # Add new text
                    new_text_node = doc.createTextNode(new_text)
                    element.appendChild(new_text_node)
                    # Add remaining part
                    if parts[1]:
                        remaining_node = doc.createTextNode(parts[1])
                        element.appendChild(remaining_node)
                    return True
            return False
        
        # Apply replacements to all paragraphs
        for replacement in all_replacements:
            old_text = replacement.get("from", "")
            new_text = replacement.get("to", "")
            
            if not old_text or old_text == new_text:
                continue
            
            # Replace in paragraphs
            for paragraph in doc.getElementsByType(P):
                replace_in_text_element(paragraph, old_text, new_text)
        
        # Save the document
        doc.save(str(file_path))
        
    except Exception as e:
        raise RuntimeError(f"Failed to edit ODT file {file_path}: {e}") from e


def apply_replacements(file_path: Path, replacements: Dict[str, List[Dict[str, str]]]) -> None:
    """
    Apply replacements to a document based on its file extension.
    
    Args:
        file_path: Path to the document file
        replacements: Dictionary with 'role_replacements' and 'skill_replacements' lists
        
    Raises:
        ValueError: If file format is not supported
    """
    suffix = file_path.suffix.lower()
    
    if suffix == ".docx":
        apply_replacements_to_docx(file_path, replacements)
    elif suffix == ".odt":
        apply_replacements_to_odt(file_path, replacements)
    else:
        raise ValueError(f"Unsupported file format for editing: {suffix}. Use .docx or .odt")

