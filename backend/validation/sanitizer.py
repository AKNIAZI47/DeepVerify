"""
HTML sanitization module.

This module provides HTML sanitization to prevent XSS attacks
while allowing safe HTML formatting where needed.
"""

import bleach
from typing import List, Dict, Optional
import re


class HTMLSanitizer:
    """HTML sanitization using bleach library."""
    
    # Default allowed tags for rich text
    DEFAULT_ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'code', 'pre', 'ul', 'ol', 'li', 'a', 'span', 'div',
    ]
    
    # Default allowed attributes
    DEFAULT_ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'rel'],
        'span': ['class'],
        'div': ['class'],
    }
    
    # Default allowed protocols for links
    DEFAULT_ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']
    
    @staticmethod
    def sanitize_html(
        html: str,
        allowed_tags: Optional[List[str]] = None,
        allowed_attributes: Optional[Dict[str, List[str]]] = None,
        allowed_protocols: Optional[List[str]] = None,
        strip: bool = False,
    ) -> str:
        """
        Sanitize HTML content to prevent XSS attacks.
        
        Args:
            html: HTML content to sanitize
            allowed_tags: List of allowed HTML tags (None = use defaults)
            allowed_attributes: Dict of allowed attributes per tag (None = use defaults)
            allowed_protocols: List of allowed URL protocols (None = use defaults)
            strip: If True, strip disallowed tags instead of escaping
            
        Returns:
            Sanitized HTML string
        """
        if not html:
            return ""
        
        if allowed_tags is None:
            allowed_tags = HTMLSanitizer.DEFAULT_ALLOWED_TAGS
        
        if allowed_attributes is None:
            allowed_attributes = HTMLSanitizer.DEFAULT_ALLOWED_ATTRIBUTES
        
        if allowed_protocols is None:
            allowed_protocols = HTMLSanitizer.DEFAULT_ALLOWED_PROTOCOLS
        
        return bleach.clean(
            html,
            tags=allowed_tags,
            attributes=allowed_attributes,
            protocols=allowed_protocols,
            strip=strip,
        )
    
    @staticmethod
    def sanitize_text_only(html: str) -> str:
        """
        Strip all HTML tags and return plain text.
        
        Args:
            html: HTML content
            
        Returns:
            Plain text with all HTML removed
        """
        return bleach.clean(html, tags=[], strip=True)
    
    @staticmethod
    def sanitize_for_display(html: str) -> str:
        """
        Sanitize HTML for safe display (allows basic formatting).
        
        Args:
            html: HTML content
            
        Returns:
            Sanitized HTML safe for display
        """
        # More restrictive tag list for user-generated content
        safe_tags = ['p', 'br', 'strong', 'em', 'u', 'code', 'pre', 'blockquote']
        
        return bleach.clean(
            html,
            tags=safe_tags,
            attributes={},  # No attributes allowed
            strip=True,
        )
    
    @staticmethod
    def sanitize_url(url: str) -> str:
        """
        Sanitize URL to prevent javascript: and data: URIs.
        
        Args:
            url: URL to sanitize
            
        Returns:
            Sanitized URL or empty string if dangerous
        """
        if not url:
            return ""
        
        url = url.strip()
        
        # Check for dangerous protocols
        dangerous_protocols = [
            'javascript:',
            'data:',
            'vbscript:',
            'file:',
        ]
        
        url_lower = url.lower()
        for protocol in dangerous_protocols:
            if url_lower.startswith(protocol):
                return ""
        
        # Only allow http, https, and mailto
        if not url_lower.startswith(('http://', 'https://', 'mailto:', '/')):
            return ""
        
        return url
    
    @staticmethod
    def linkify_text(text: str, skip_tags: Optional[List[str]] = None) -> str:
        """
        Convert URLs in text to clickable links.
        
        Args:
            text: Plain text with URLs
            skip_tags: List of tags to skip when linkifying
            
        Returns:
            HTML with URLs converted to links
        """
        if skip_tags is None:
            skip_tags = ['pre', 'code']
        
        return bleach.linkify(
            text,
            skip_tags=skip_tags,
            parse_email=True,
        )
    
    @staticmethod
    def remove_scripts(html: str) -> str:
        """
        Remove all script tags and event handlers from HTML.
        
        Args:
            html: HTML content
            
        Returns:
            HTML with scripts removed
        """
        # Remove script tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove event handlers (onclick, onload, etc.)
        html = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
        html = re.sub(r'\s*on\w+\s*=\s*[^\s>]*', '', html, flags=re.IGNORECASE)
        
        return html
    
    @staticmethod
    def sanitize_css(css: str) -> str:
        """
        Sanitize CSS to prevent CSS injection attacks.
        
        Args:
            css: CSS content
            
        Returns:
            Sanitized CSS
        """
        if not css:
            return ""
        
        # Remove dangerous CSS properties
        dangerous_patterns = [
            r'expression\s*\(',
            r'javascript:',
            r'@import',
            r'behavior:',
            r'-moz-binding:',
        ]
        
        for pattern in dangerous_patterns:
            css = re.sub(pattern, '', css, flags=re.IGNORECASE)
        
        return css


class Sanitizer:
    """Main sanitizer class providing convenience methods."""
    
    @staticmethod
    def sanitize(content: str, content_type: str = "html") -> str:
        """
        Sanitize content based on type.
        
        Args:
            content: Content to sanitize
            content_type: Type of content ("html", "text", "url", "css")
            
        Returns:
            Sanitized content
        """
        if content_type == "html":
            return HTMLSanitizer.sanitize_html(content)
        elif content_type == "text":
            return HTMLSanitizer.sanitize_text_only(content)
        elif content_type == "url":
            return HTMLSanitizer.sanitize_url(content)
        elif content_type == "css":
            return HTMLSanitizer.sanitize_css(content)
        else:
            # Default to text-only sanitization
            return HTMLSanitizer.sanitize_text_only(content)
    
    @staticmethod
    def sanitize_dict(data: dict, fields: Optional[List[str]] = None) -> dict:
        """
        Sanitize specific fields in a dictionary.
        
        Args:
            data: Dictionary with data to sanitize
            fields: List of field names to sanitize (None = all string fields)
            
        Returns:
            Dictionary with sanitized values
        """
        sanitized = data.copy()
        
        for key, value in sanitized.items():
            if fields is None or key in fields:
                if isinstance(value, str):
                    sanitized[key] = HTMLSanitizer.sanitize_text_only(value)
        
        return sanitized


# Convenience functions
def sanitize_html(html: str) -> str:
    """Sanitize HTML content."""
    return HTMLSanitizer.sanitize_html(html)


def sanitize_text(text: str) -> str:
    """Strip all HTML and return plain text."""
    return HTMLSanitizer.sanitize_text_only(text)


def sanitize_url(url: str) -> str:
    """Sanitize URL."""
    return HTMLSanitizer.sanitize_url(url)
