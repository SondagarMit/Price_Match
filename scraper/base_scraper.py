"""Base scraper class with common utilities."""

from abc import ABC, abstractmethod
import re
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""
    
    # Common user agents to avoid blocking
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.USER_AGENTS[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    @abstractmethod
    def scrape(self, url: str) -> Dict:
        """
        Scrape product information from the given URL.
        
        Args:
            url: Product URL to scrape
            
        Returns:
            Dictionary with product information (title, price, rating, image, availability, description)
            
        Raises:
            Exception: If scraping fails
        """
        pass
    
    def fetch_page(self, url: str) -> BeautifulSoup:
        """
        Fetch and parse a web page.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object of the parsed HTML
            
        Raises:
            requests.RequestException: If the request fails
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch page: {str(e)}")
    
    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def extract_price(price_text: Optional[str]) -> Optional[float]:
        """
        Extract numeric price from text.
        
        Args:
            price_text: Price string (e.g., "₹1,299.00" or "$29.99")
            
        Returns:
            Float price value or None if not found
        """
        if not price_text:
            return None
        
        # Remove currency symbols and commas
        price_clean = re.sub(r'[^\d.]', '', price_text)
        try:
            return float(price_clean)
        except ValueError:
            return None
    
    @staticmethod
    def extract_rating(rating_text: Optional[str]) -> Optional[float]:
        """
        Extract numeric rating from text.
        
        Args:
            rating_text: Rating string (e.g., "4.5 out of 5" or "4.5")
            
        Returns:
            Float rating value or None if not found
        """
        if not rating_text:
            return None
        
        # Extract first decimal number
        match = re.search(r'(\d+\.?\d*)', rating_text)
        if match:
            try:
                rating = float(match.group(1))
                # Normalize to 0-5 scale if needed
                if rating > 5:
                    rating = rating / 10
                return rating
            except ValueError:
                return None
        return None

