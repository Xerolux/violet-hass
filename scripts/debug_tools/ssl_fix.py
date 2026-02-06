import logging
import ssl

_LOGGER = logging.getLogger(__name__)

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
