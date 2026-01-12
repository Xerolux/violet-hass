def _validate_credentials_strength(username: str, password: str) -> None:
    """Validate credential strength requirements."""
    if not username or len(username) < 3:
        raise ValueError("Username must be at least 3 characters long")
    
    if not password:
        raise ValueError("Password is required")
    
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    # Password complexity requirements
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain uppercase letters")
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain lowercase letters")
    if not re.search(r'\d', password):
        raise ValueError("Password must contain numbers")
    
    # Check for common weak passwords
    weak_passwords = ['password', '123456', 'admin', 'violet', 'pool', 'qwerty']
    if password.lower() in weak_passwords:
        raise ValueError("Password is too common")


def _secure_auth_error_message() -> str:
    """Return generic error message to prevent username enumeration."""
    return "Invalid credentials or connection failed"


def _create_ssl_context(use_ssl: bool, verify_cert: bool = True) -> bool | ssl.SSLContext:
    """Create secure SSL context with proper certificate validation."""
    if not use_ssl:
        # Only allow SSL to be disabled in development environments
        _LOGGER.warning("SSL disabled - connection will not be encrypted")
        return False
    
    # Create strict SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    
    if not verify_cert:
        # Only for development - certificate verification disabled
        _LOGGER.warning("Certificate verification disabled - development only")
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    
    return ssl_context