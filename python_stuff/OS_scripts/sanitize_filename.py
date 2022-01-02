import re
from pathvalidate import sanitize_filepath

def sanitize_filename(filename):
    """
    Sanitize filename to a command-line-friendly format

    Args:
        filename (Pathlike): A string like path

    Returns:
        str: Path string to sanitized filename
    """
    filename = re.sub(r"[^A-Za-z\d\-\_\s\,\.\[\]]", r"_", str(filename))
    filename = sanitize_filepath(filename, platform="auto").replace(" ", "_")
    return filename
