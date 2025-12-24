"""Validation utilities"""
import re
from email_validator import validate_email as validate_email_lib, EmailNotValidError


def validate_email(email):
    """Validate email address format
    
    Args:
        email (str): Email address to validate
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        # Validate and normalize
        valid = validate_email_lib(email, check_deliverability=False)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)


def validate_phone(phone):
    """Validate phone number format
    
    Args:
        phone (str): Phone number to validate
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not phone:
        return True, ""  # Phone is optional
    
    # Remove spaces and dashes
    phone = phone.replace(" ", "").replace("-", "")
    
    # Check if it contains only digits and optional + at start
    if not re.match(r'^\+?\d{10,15}$', phone):
        return False, "Phone number must be 10-15 digits"
    
    return True, phone


def validate_password(password):
    """Validate password strength
    
    Args:
        password (str): Password to validate
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, ""


def allowed_file(filename, allowed_extensions=None):
    """Check if file has allowed extension
    
    Args:
        filename (str): Name of the file
        allowed_extensions (set): Set of allowed extensions
    
    Returns:
        bool: True if file extension is allowed
    """
    if allowed_extensions is None:
        allowed_extensions = {'xlsx', 'xls', 'csv'}
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
