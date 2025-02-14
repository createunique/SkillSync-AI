"""
Module: utils
Purpose: Provides functions to extract text from files (PDF, DOCX, TXT) and to retrieve candidate contact details.

"""

import pdfplumber
import docx
import re

def get_pdf_content(pdf_path):
    """
    Extracts and concatenates text from all pages of a PDF file.

    Args:
        pdf_path (str): Path or file-like object for the PDF.

    Returns:
        str: Combined text extracted from each page.
    """
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages).strip()

def get_docx_content(docx_path):
    """
    Retrieves text from a DOCX file by reading its paragraphs.

    Args:
        docx_path (str): Path or file-like object for the DOCX file.

    Returns:
        str: Text content joined by newlines.
    """
    document = docx.Document(docx_path)
    paras = [p.text for p in document.paragraphs]
    return "\n".join(paras).strip()

def get_txt_content(txt_file):
    """
    Reads text from a plain text file-like object.

    Args:
        txt_file (file-like): The text file opened in binary mode.

    Returns:
        str: Decoded and stripped text.
    """
    return txt_file.read().decode("utf-8").strip()

def fetch_text_content(file_obj):
    """
    Determines the file type and extracts text accordingly.

    Args:
        file_obj: Uploaded file object with attribute 'type'.

    Returns:
        str: Extracted text content.

    Raises:
        ValueError: If the file format is not supported.
    """
    if file_obj.type == "application/pdf":
        return get_pdf_content(file_obj)
    elif file_obj.type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
         ]:
        return get_docx_content(file_obj)
    elif file_obj.type == "text/plain":
        return get_txt_content(file_obj)
    else:
        raise ValueError("Unsupported file type. Provide PDF, DOCX, or TXT only.")

def retrieve_contact_details(text):
    """
    Scans given text to extract the candidate's first line (assumed name) and email address.

    Args:
        text (str): The complete text from which to extract details.

    Returns:
        tuple: (Name extracted from first line, email address if found or None)
    """
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    first_line = text.split("\n")[0]
    return first_line.strip(), (email_match.group(0) if email_match else None)
