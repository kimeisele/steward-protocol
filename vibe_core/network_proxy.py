"""
KERNEL NETWORK PROXY - Controlled External Access
=================================================

Goal: Prevent agents from making arbitrary network requests.

Philosophy:
"The kernel is the gateway. All external communication flows through it."

Architecture:
- All HTTP requests go through kernel.request()
- Whitelist-based domain filtering
- Request logging for audit trail
- Rate limiting per agent (future)

Security Model:
- Default: DENY ALL
- Whitelist: Explicitly allowed domains
- Logging: All requests logged with agent_id, URL, timestamp
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from datetime import datetime

logger = logging.getLogger("NETWORK_PROXY")

class KernelNetworkProxy:
    """
    Kernel-controlled network gateway for agents.
    
    All agent network requests must go through this proxy.
    Non-whitelisted domains are blocked.
    """
    
    # Default whitelist of allowed domains
    DEFAULT_WHITELIST = [
        # AI APIs
        "api.openai.com",
        "api.anthropic.com",
        
        # Research & Search
        "api.tavily.com",
        "tavily.com",
        
        # Development
        "api.github.com",
        "github.com",
        "raw.githubusercontent.com",
        
        # General
        "wikipedia.org",
        "en.wikipedia.org",
    ]
    
    def __init__(self, kernel=None):
        """
        Initialize network proxy.
        
        Args:
            kernel: Reference to VibeKernel (optional)
        """
        self.kernel = kernel
        self.whitelist = set(self.DEFAULT_WHITELIST)
        self.request_log: List[Dict[str, Any]] = []
        
        logger.info(f"🌐 Network Proxy initialized with {len(self.whitelist)} whitelisted domains")
    
    def add_to_whitelist(self, domain: str) -> None:
        """
        Add domain to whitelist.
        
        Args:
            domain: Domain to whitelist (e.g., "example.com")
        """
        self.whitelist.add(domain)
        logger.info(f"✅ Whitelisted domain: {domain}")
    
    def remove_from_whitelist(self, domain: str) -> None:
        """
        Remove domain from whitelist.
        
        Args:
            domain: Domain to remove
        """
        self.whitelist.discard(domain)
        logger.info(f"❌ Removed from whitelist: {domain}")
    
    def _is_allowed(self, url: str) -> bool:
        """
        Check if URL is whitelisted.
        
        Args:
            url: Full URL to check
            
        Returns:
            True if allowed, False otherwise
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Check exact match
            if domain in self.whitelist:
                return True
            
            # Check if domain ends with any whitelisted domain
            # (allows subdomains, e.g., api.github.com matches github.com)
            for allowed in self.whitelist:
                if domain.endswith(f".{allowed}") or domain == allowed:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error parsing URL {url}: {e}")
            return False
    
    def request(
        self,
        agent_id: str,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request on behalf of agent.
        
        Args:
            agent_id: Requesting agent
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Target URL
            **kwargs: Additional arguments for requests.request()
            
        Returns:
            Response object
            
        Raises:
            PermissionError: If domain not whitelisted
        """
        # Check whitelist
        if not self._is_allowed(url):
            logger.warning(
                f"🚫 {agent_id} blocked from accessing {url} "
                f"(domain not whitelisted)"
            )
            raise PermissionError(
                f"Network access denied: {urlparse(url).netloc} not whitelisted. "
                f"Contact kernel administrator to whitelist this domain."
            )
        
        # Log request
        log_entry = {
            "agent_id": agent_id,
            "method": method,
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.request_log.append(log_entry)
        
        logger.info(f"🌐 {agent_id} → {method} {url}")
        
        # Make request
        try:
            response = requests.request(method, url, **kwargs)
            logger.debug(
                f"   ← {response.status_code} "
                f"({len(response.content)} bytes)"
            )
            return response
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            raise
    
    def get(self, agent_id: str, url: str, **kwargs) -> requests.Response:
        """Convenience method for GET requests"""
        return self.request(agent_id, "GET", url, **kwargs)
    
    def post(self, agent_id: str, url: str, **kwargs) -> requests.Response:
        """Convenience method for POST requests"""
        return self.request(agent_id, "POST", url, **kwargs)
    
    def put(self, agent_id: str, url: str, **kwargs) -> requests.Response:
        """Convenience method for PUT requests"""
        return self.request(agent_id, "PUT", url, **kwargs)
    
    def delete(self, agent_id: str, url: str, **kwargs) -> requests.Response:
        """Convenience method for DELETE requests"""
        return self.request(agent_id, "DELETE", url, **kwargs)
    
    def get_request_log(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get request log.
        
        Args:
            agent_id: Filter by agent (optional)
            
        Returns:
            List of request log entries
        """
        if agent_id:
            return [
                entry for entry in self.request_log
                if entry["agent_id"] == agent_id
            ]
        return self.request_log
    
    def clear_log(self) -> None:
        """Clear request log"""
        self.request_log.clear()
        logger.info("🗑️  Request log cleared")
