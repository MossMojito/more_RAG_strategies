import re

def clean_text(text):
    """
    Remove dirty characters from text.
    """
    if not text:
        return ""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = text.replace('\r\n', '\n').replace('\t', ' ')
    return text.strip()

def extract_structure_metadata(chunk):
    """
    Extract headers and bold text from a text chunk.
    """
    metadata = {}
    
    # Extract headers
    headers_h2 = re.findall(r'^##\s+(.+)$', chunk, re.MULTILINE)
    headers_h3 = re.findall(r'^###\s+(.+)$', chunk, re.MULTILINE)
    
    if headers_h2:
        metadata["headers_h2"] = headers_h2
    if headers_h3:
        metadata["headers_h3"] = headers_h3
    
    # Extract bold text (first 10)
    bold_text = re.findall(r'\*\*([^*]+)\*\*', chunk)
    if bold_text:
        metadata["bold_text"] = bold_text[:10]
    
    metadata["char_count"] = len(chunk)
    metadata["word_count"] = len(chunk.split())
    
    return metadata

def flatten_metadata(metadata):
    """
    Convert lists in metadata to comma-separated strings for ChromaDB.
    """
    flat = {}
    for key, value in metadata.items():
        if isinstance(value, list):
            flat[key] = ", ".join(str(v) for v in value)
        else:
            flat[key] = str(value).lower() if isinstance(value, bool) else value
    return flat
