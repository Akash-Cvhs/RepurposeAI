"""
HTTP Client for external API calls with error handling and logging
"""

import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def request_json(
    service: str,
    method: str,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Make HTTP request and return JSON response
    
    Args:
        service: Service name for logging (e.g., "clinicaltrials", "serpapi")
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        params: Query parameters
        json_data: JSON body for POST requests
        headers: HTTP headers
        timeout: Request timeout in seconds
    
    Returns:
        JSON response as dictionary
    
    Raises:
        RuntimeError: If request fails
    """
    try:
        logger.info(f"[{service}] {method} {url}")
        
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=headers,
            timeout=timeout
        )
        
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"[{service}] Request successful")
        
        return result
        
    except requests.exceptions.Timeout:
        error_msg = f"Request to {service} timed out after {timeout}s"
        logger.error(f"[{service}] {error_msg}")
        raise RuntimeError(error_msg)
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error from {service}: {e.response.status_code} - {e.response.text}"
        logger.error(f"[{service}] {error_msg}")
        raise RuntimeError(error_msg)
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Request to {service} failed: {str(e)}"
        logger.error(f"[{service}] {error_msg}")
        raise RuntimeError(error_msg)
        
    except ValueError as e:
        error_msg = f"Invalid JSON response from {service}: {str(e)}"
        logger.error(f"[{service}] {error_msg}")
        raise RuntimeError(error_msg)
