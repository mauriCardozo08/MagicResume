import os
from typing import Union

def read_docx(file_path: str) -> str:
    from docx import Document

    document = Document(file_path)
    paragraphs = [p.text for p in document.paragraphs]
    return "\n".join(paragraphs)


def read_odt(file_path: str) -> str:
    from odf.opendocument import load
    from odf.text import P

    doc = load(file_path)
    paragraphs = []

    for element in doc.getElementsByType(P):
        text_parts = []
        for node in element.childNodes:
            if node.nodeType == node.TEXT_NODE:
                text_parts.append(node.data)
        paragraphs.append("".join(text_parts))

    return "\n".join(paragraphs)


def read_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def read_document_as_text(file_path: str) -> str:
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".docx":
        return read_docx(file_path)
    elif extension == ".odt":
        return read_odt(file_path)
    elif extension == ".txt":
        return read_txt(file_path)
    else:
        raise ValueError("Unsupported file format. Use .docx, .odt, or .txt")
