"""Scraper package for e-commerce price comparison."""

from .base_scraper import BaseScraper
from .amazon_scraper import AmazonScraper
from .flipkart_scraper import FlipkartScraper
from .myntra_scraper import MyntraScraper
from .ajio_scraper import AjioScraper

__all__ = [
    'BaseScraper',
    'AmazonScraper',
    'FlipkartScraper',
    'MyntraScraper',
    'AjioScraper',
]

