"""
Password Leak Detection Tool
Based on HaveIBeenPwned API and local breach databases
"""
import asyncio
import hashlib
import aiohttp
from typing import Dict, List, Optional
from loguru import logger

from app.core.config import settings


class PasswordLeakChecker:
    """Password leak detection service"""
    
    def __init__(self):
        self.api_url = settings.pwned_passwords_api_url
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _hash_password(self, password: str) -> str:
        """Generate SHA-1 hash of password"""
        return hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    
    async def check_password_leak(self, password: str) -> Dict[str, any]:
        """
        Check if password has been leaked using HaveIBeenPwned API
        
        Args:
            password: Password to check
            
        Returns:
            Dict containing leak status and details
        """
        try:
            # Generate SHA-1 hash
            sha1_hash = self._hash_password(password)
            prefix = sha1_hash[:5]
            suffix = sha1_hash[5:]
            
            # Query HaveIBeenPwned API
            url = f"{self.api_url}{prefix}"
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    response_text = await response.text()
                    
                    # Parse response to find our hash suffix
                    for line in response_text.splitlines():
                        if ':' in line:
                            line_suffix, count = line.split(':', 1)
                            if line_suffix == suffix:
                                return {
                                    "is_leaked": True,
                                    "leak_count": int(count),
                                    "breach_sources": ["HaveIBeenPwned"],
                                    "risk_level": self._calculate_risk_level(int(count)),
                                    "hash_prefix": prefix
                                }
                    
                    # Not found in leaks
                    return {
                        "is_leaked": False,
                        "leak_count": 0,
                        "breach_sources": [],
                        "risk_level": "low",
                        "hash_prefix": prefix
                    }
                
                elif response.status == 429:
                    # Rate limited
                    logger.warning("Rate limited by HaveIBeenPwned API")
                    return {
                        "is_leaked": None,
                        "leak_count": 0,
                        "breach_sources": [],
                        "risk_level": "unknown",
                        "error": "Rate limited",
                        "hash_prefix": prefix
                    }
                
                else:
                    logger.error(f"HaveIBeenPwned API returned status {response.status}")
                    return {
                        "is_leaked": None,
                        "leak_count": 0,
                        "breach_sources": [],
                        "risk_level": "unknown",
                        "error": f"API error: {response.status}",
                        "hash_prefix": prefix
                    }
        
        except Exception as e:
            logger.error(f"Error checking password leak: {str(e)}")
            return {
                "is_leaked": None,
                "leak_count": 0,
                "breach_sources": [],
                "risk_level": "unknown",
                "error": str(e),
                "hash_prefix": prefix if 'prefix' in locals() else None
            }
    
    def _calculate_risk_level(self, leak_count: int) -> str:
        """Calculate risk level based on leak count"""
        if leak_count == 0:
            return "low"
        elif leak_count < 10:
            return "medium"
        elif leak_count < 100:
            return "high"
        else:
            return "critical"
    
    async def batch_check_passwords(self, passwords: List[str]) -> Dict[str, Dict[str, any]]:
        """
        Check multiple passwords for leaks
        
        Args:
            passwords: List of passwords to check
            
        Returns:
            Dict mapping password hashes to leak information
        """
        results = {}
        
        # Group passwords by SHA-1 prefix to minimize API calls
        prefix_groups = {}
        password_map = {}
        
        for password in passwords:
            sha1_hash = self._hash_password(password)
            prefix = sha1_hash[:5]
            suffix = sha1_hash[5:]
            
            if prefix not in prefix_groups:
                prefix_groups[prefix] = []
            
            prefix_groups[prefix].append(suffix)
            password_map[suffix] = password
        
        # Check each prefix group
        for prefix, suffixes in prefix_groups.items():
            try:
                url = f"{self.api_url}{prefix}"
                
                if not self.session:
                    self.session = aiohttp.ClientSession()
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        
                        # Parse leaked hashes for this prefix
                        leaked_hashes = {}
                        for line in response_text.splitlines():
                            if ':' in line:
                                line_suffix, count = line.split(':', 1)
                                leaked_hashes[line_suffix] = int(count)
                        
                        # Check each password in this group
                        for suffix in suffixes:
                            password = password_map[suffix]
                            leak_count = leaked_hashes.get(suffix, 0)
                            
                            results[password] = {
                                "is_leaked": leak_count > 0,
                                "leak_count": leak_count,
                                "breach_sources": ["HaveIBeenPwned"] if leak_count > 0 else [],
                                "risk_level": self._calculate_risk_level(leak_count),
                                "hash_prefix": prefix
                            }
                    
                    else:
                        # Handle API errors for this prefix group
                        for suffix in suffixes:
                            password = password_map[suffix]
                            results[password] = {
                                "is_leaked": None,
                                "leak_count": 0,
                                "breach_sources": [],
                                "risk_level": "unknown",
                                "error": f"API error: {response.status}",
                                "hash_prefix": prefix
                            }
                
                # Add delay to respect rate limits
                await asyncio.sleep(0.1)
            
            except Exception as e:
                logger.error(f"Error checking prefix {prefix}: {str(e)}")
                for suffix in suffixes:
                    password = password_map[suffix]
                    results[password] = {
                        "is_leaked": None,
                        "leak_count": 0,
                        "breach_sources": [],
                        "risk_level": "unknown",
                        "error": str(e),
                        "hash_prefix": prefix
                    }
        
        return results


# Standalone function for simple usage (compatible with original script)
async def check_password(password: str) -> bool:
    """
    Simple function to check if password is leaked
    Compatible with the original 泄露检查.py script
    
    Args:
        password: Password to check
        
    Returns:
        True if password is leaked, False otherwise
    """
    async with PasswordLeakChecker() as checker:
        result = await checker.check_password_leak(password)
        return result.get("is_leaked", False)


# For backward compatibility with the original script
def check_password_sync(password: str) -> bool:
    """Synchronous wrapper for backward compatibility"""
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(check_password(password))


if __name__ == "__main__":
    # Test the leak checker (compatible with original script)
    import asyncio
    
    async def main():
        test_password = "asidnfasioff"
        
        async with PasswordLeakChecker() as checker:
            result = await checker.check_password_leak(test_password)
            
            if result["is_leaked"]:
                print(f"密码已泄露！泄露次数: {result['leak_count']}")
            elif result["is_leaked"] is False:
                print("密码未在泄露数据库中。")
            else:
                print(f"无法检查密码状态: {result.get('error', 'Unknown error')}")
    
    asyncio.run(main())
