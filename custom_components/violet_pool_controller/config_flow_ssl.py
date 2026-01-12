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


async def fetch_api_data_with_ssl(
    session: aiohttp.ClientSession,
    api_url: str,
    auth: Optional[aiohttp.BasicAuth],
    use_ssl: bool,
    timeout: int,
    retries: int = 3,
) -> dict[str, Any]:
    """Fetch API data with proper SSL certificate validation.
    
    Args:
        session: The aiohttp session to use.
        api_url: The API URL to query.
        auth: Authentication credentials.
        use_ssl: Whether to use SSL.
        timeout: Request timeout in seconds.
        retries: Number of retry attempts.
        
    Returns:
        Dictionary with API response data.
        
    Raises:
        ValueError: If API request fails or authentication issues.
    """
    BASE_RETRY_DELAY = 1
    _LOGGER = logging.getLogger(__name__)
    
    for attempt in range(retries):
        try:
            # Create secure SSL context
            ssl_context = _create_ssl_context(use_ssl, verify_cert=True)
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            
            async with session.get(
                api_url, auth=auth, ssl=ssl_context, timeout=timeout_obj
            ) as response:
                # Handle authentication failures specifically
                if response.status == 401:
                    raise ValueError("Authentication failed - invalid credentials")
                elif response.status == 403:
                    raise ValueError("Access forbidden - insufficient permissions")
                elif response.status >= 400:
                    response_text = await response.text()
                    raise ValueError(f"HTTP {response.status}: {response_text.strip()[:200]}")
                    
                response.raise_for_status()
                data = await response.json()
                
                if not data:
                    raise ValueError("No data received from controller")
                    
                return data
                
        except aiohttp.ClientResponseError as err:
            if err.status == 401:
                raise ValueError("Authentication failed - invalid credentials") from err
            elif err.status == 403:
                raise ValueError("Access forbidden - insufficient permissions") from err
            elif attempt + 1 == retries:
                _LOGGER.error("HTTP error after %d attempts: %s", retries, err)
                raise ValueError(f"HTTP request failed: {err}") from err
                
        except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as err:
            if attempt + 1 == retries:
                _LOGGER.error("Connection failed after %d attempts: %s", retries, err)
                raise ValueError(f"Connection failed: {err}") from err
                
        except ValueError as err:
            # Re-raise validation errors immediately
            raise
                
        except Exception as err:
            if attempt + 1 == retries:
                _LOGGER.error("Unexpected error after %d attempts: %s", retries, err)
                raise ValueError(f"API request failed: {err}") from err
            
            retry_delay = BASE_RETRY_DELAY**attempt
            _LOGGER.warning(
                "API attempt %d/%d failed, retrying in %ds",
                attempt + 1,
                retries,
                retry_delay,
            )
            await asyncio.sleep(retry_delay)