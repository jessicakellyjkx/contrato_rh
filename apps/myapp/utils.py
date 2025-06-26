"""
Utility functions for the RH Contract application
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, Optional


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    return filename


def format_currency(value: float) -> str:
    """
    Format currency value to Brazilian Real format
    
    Args:
        value: Numeric value
        
    Returns:
        Formatted currency string
    """
    if value is None:
        return ''
    return f"R$ {value:.2f}"


def format_date(date_obj, format_str: str = '%d/%m/%Y') -> str:
    """
    Format date object to string
    
    Args:
        date_obj: Date object
        format_str: Format string
        
    Returns:
        Formatted date string
    """
    if date_obj is None:
        return ''
    return date_obj.strftime(format_str)


def build_address(rua: str, bairro: str, cidade: str, estado: str, cep: str) -> str:
    """
    Build complete address string
    
    Args:
        rua: Street name
        bairro: Neighborhood
        cidade: City
        estado: State
        cep: ZIP code
        
    Returns:
        Complete address string
    """
    if not rua:
        return ''
    
    parts = [rua, bairro, f"{cidade} - {estado}", f"CEP: {cep}"]
    return ", ".join(filter(None, parts))


def get_contract_type_from_filename(filename: str) -> str:
    """
    Extract contract type from filename
    
    Args:
        filename: Contract filename
        
    Returns:
        Contract type
    """
    if filename.startswith("contrato_entrada_"):
        return "contrato_entrada"
    elif filename.startswith("termo_uso_"):
        return "termo_uso"
    elif filename.startswith("sindicato_"):
        return "sindicato"
    else:
        return "contrato_entrada"  # default


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Validate file extension
    
    Args:
        filename: File name
        allowed_extensions: List of allowed extensions
        
    Returns:
        True if valid, False otherwise
    """
    if not filename:
        return False
    
    file_ext = os.path.splitext(filename)[1].lower()
    return file_ext in allowed_extensions


def validate_file_size(file_size: int, max_size: int) -> bool:
    """
    Validate file size
    
    Args:
        file_size: File size in bytes
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if valid, False otherwise
    """
    return file_size <= max_size


def create_unique_filename(base_name: str, extension: str) -> str:
    """
    Create unique filename with timestamp
    
    Args:
        base_name: Base name for the file
        extension: File extension
        
    Returns:
        Unique filename
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    sanitized_name = sanitize_filename(base_name)
    return f"{sanitized_name}_{timestamp}{extension}"


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory_path: Path to directory
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get file information
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
    """
    if not os.path.exists(file_path):
        return {}
    
    stat = os.stat(file_path)
    return {
        'size': stat.st_size,
        'created': datetime.fromtimestamp(stat.st_ctime),
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'exists': True
    }


def safe_file_operation(operation_func, *args, **kwargs) -> Optional[Any]:
    """
    Safely execute file operation with error handling
    
    Args:
        operation_func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Result of operation or None if failed
    """
    try:
        return operation_func(*args, **kwargs)
    except (OSError, IOError) as e:
        # Log error here if logger is available
        print(f"File operation error: {e}")
        return None
    except Exception as e:
        # Log error here if logger is available
        print(f"Unexpected error in file operation: {e}")
        return None 