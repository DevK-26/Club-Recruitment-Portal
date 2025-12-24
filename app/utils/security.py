"""Security utilities for password management and authentication"""
import bcrypt
import secrets
import string


def generate_random_password(length=12):
    """Generate a secure random password with mixed characters
    
    Args:
        length (int): Length of the password (default: 12)
    
    Returns:
        str: Random password with uppercase, lowercase, digits, and special characters
    """
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*"
    
    # Ensure at least one character from each set
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]
    
    # Fill the rest randomly
    all_chars = lowercase + uppercase + digits + special
    password.extend(secrets.choice(all_chars) for _ in range(length - 4))
    
    # Shuffle to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def hash_password(password):
    """Hash a password using bcrypt
    
    Args:
        password (str): Plain text password
    
    Returns:
        str: Hashed password
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')


def check_password(password_hash, password):
    """Verify a password against its hash
    
    Args:
        password_hash (str): Stored password hash
        password (str): Plain text password to verify
    
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    except Exception:
        return False


def generate_token(length=32):
    """Generate a secure random token
    
    Args:
        length (int): Length of the token in bytes
    
    Returns:
        str: URL-safe random token
    """
    return secrets.token_urlsafe(length)
