"""Amazon India scraper implementation."""

from typing import Dict
import re
from .base_scraper import BaseScraper


class AmazonScraper(BaseScraper):
    """Scraper for Amazon India product pages."""
    
    def scrape(self, url: str) -> Dict:
        """
        Scrape product information from Amazon India.
        
        Args:
            url: Amazon product URL
            
        Returns:
            Dictionary with product information
        """
        soup = self.fetch_page(url)
        
        # Extract title
        title = None
        title_selectors = [
            '#productTitle',
            'h1.a-size-large.product-title-word-break',
            'span#productTitle',
        ]
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = self.clean_text(title_elem.get_text())
                break
        
        # Extract price
        price = None
        price_text = None
        price_selectors = [
            'span.a-price-whole',
            'span.a-price .a-offscreen',
            '#priceblock_dealprice',
            '#priceblock_saleprice',
            '#priceblock_ourprice',
            'span.a-color-price',
        ]
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text()
                price = self.extract_price(price_text)
                if price:
                    break
        
        # Extract rating
        rating = None
        rating_text = None
        rating_selectors = [
            'span.a-icon-alt',
            '#acrPopover',
            'span.a-icon.a-icon-star',
        ]
        for selector in rating_selectors:
            rating_elem = soup.select_one(selector)
            if rating_elem:
                rating_text = rating_elem.get_text() or rating_elem.get('aria-label', '')
                rating = self.extract_rating(rating_text)
                if rating:
                    break
        
        # Extract image
        image = None
        image_selectors = [
            '#landingImage',
            '#imgBlkFront',
            '#main-image',
            'img#productImage',
        ]
        for selector in image_selectors:
            img_elem = soup.select_one(selector)
            if img_elem:
                image = img_elem.get('src') or img_elem.get('data-src')
                if image:
                    break

        # If not found, try XPath (using lxml)
        if not image:
            try:
                from lxml import html
                import requests
                # Fetch page raw content
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                tree = html.fromstring(response.content)
                xpath = '/html/body/div[1]/div[1]/div/div[5]/div[3]/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[1]/span/span/div/img'
                img_node = tree.xpath(xpath)
                if img_node and hasattr(img_node[0], 'attrib'):
                    image = img_node[0].attrib.get('src', '')
            except Exception:
                image = ''
        
        # Extract availability
        availability = "In Stock"
        availability_selectors = [
            '#availability span',
            '#availability',
            '.a-color-success',
        ]
        for selector in availability_selectors:
            avail_elem = soup.select_one(selector)
            if avail_elem:
                availability = self.clean_text(avail_elem.get_text())
                if availability:
                    break
        
        # Extract description
        description = None
        description_selectors = [
            '#feature-bullets ul',
            '#productDescription',
            '.a-unordered-list.a-vertical.a-spacing-mini',
        ]
        for selector in description_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                # Get first few bullet points or paragraphs
                items = desc_elem.find_all(['li', 'p'], limit=3)
                if items:
                    description = ' | '.join([self.clean_text(item.get_text()) for item in items])
                    break
        
        return {
            'title': title or 'N/A',
            'price': price,
            'price_text': price_text or 'N/A',
            'rating': rating,
            'rating_text': rating_text or 'N/A',
            'image': image or '',
            'availability': availability or 'N/A',
            'description': description or 'N/A',
            # Use single extractor to avoid duplicate keys
            'details': self.extract_product_details(soup),
            'url': url,
        }

    def clean_detail_pair(self, raw_key: str, raw_val: str):
        """
        Normalize and clean a raw key/value pair scraped from Amazon detail sections.
        Returns (key, value) where empty strings may be returned if nothing usable.
        """
        def normalize(s: str) -> str:
            if not s:
                return ''
            # Remove common invisible unicode markers and normalize whitespace
            s = s.replace('\u200f', '').replace('\u200e', '').replace('\u202a', '').replace('\u202c', '')
            s = re.sub(r'\s+', ' ', s)
            return s.strip()

        k = normalize(raw_key)
        v = normalize(raw_val)

        # If key contains a colon with value, split it
        if (not v or v == '') and ':' in k:
            parts = [p.strip() for p in k.split(':', 1)]
            if len(parts) == 2:
                k, v = parts[0], parts[1]

        # Remove trailing colon from key
        if k.endswith(':'):
            k = k[:-1].strip()

        # Remove repeated key text from value (leading or trailing)
        try:
            if k:
                key_esc = re.escape(k)
                # trailing occurrences like ": Key" or ": Key :"
                v = re.sub(r':\s*' + key_esc + r'\s*:??$', '', v, flags=re.I).strip()
                # leading occurrences like "Key :" at start
                v = re.sub(r'^' + key_esc + r'\s*:??\s*', '', v, flags=re.I).strip()
        except Exception:
            pass

        # Final cleanup
        k = k.strip()
        v = v.strip()
        if v.lower() == k.lower():
            # value should not be identical to key
            v = ''

        return k, v

    def extract_product_details(self, soup):
        details = {}

        # 1. Product Information table (common)
        product_info = soup.select_one("#productDetails_techSpec_section_1")
        if product_info:
            rows = product_info.select("tr")
            for row in rows:
                key = row.select_one("th")
                val = row.select_one("td")
                if key and val:
                    raw_key = key.get_text(strip=True)
                    raw_val = val.get_text(strip=True)
                    k, v = self.clean_detail_pair(raw_key, raw_val)
                    if k and v:
                        details[k] = v

        # 2. Alternate product details table
        alt_info = soup.select_one("#productDetails_detailBullets_sections1")
        if alt_info:
            rows = alt_info.select("tr")
            for row in rows:
                key = row.select_one("th")
                val = row.select_one("td")
                if key and val:
                    raw_key = key.get_text(strip=True)
                    raw_val = val.get_text(strip=True)
                    k, v = self.clean_detail_pair(raw_key, raw_val)
                    if k and v:
                        details[k] = v


        # 3. Bullet points / detail-bullets section (handles detailBullets HTML format)
        # Try multiple selectors used by Amazon product pages
        # - #feature-bullets ul li span
        # - #detailBullets_feature_div ul.detail-bullet-list li
        bullet_points = []

        # feature-bullets (simple bullets)
        bullets = soup.select("#feature-bullets ul li span")
        for b in bullets:
            t = b.get_text(strip=True)
            if t:
                bullet_points.append(t)

        # detailBullets block (key/value list items)
        detail_block = soup.select_one("#detailBullets_feature_div") or soup.select_one("#detailBulletsWrapper_feature_div")
        if detail_block:
            lis = detail_block.select("ul.detail-bullet-list > li") or detail_block.select("ul li")
            for li in lis:
                # First try: spans inside the li (common pattern)
                spans = li.select('span')
                if spans and len(spans) >= 2:
                    raw_key = spans[0].get_text(separator=' ', strip=True)
                    raw_val = spans[1].get_text(separator=' ', strip=True)
                    # Normalize and clean pair
                    k, v = self.clean_detail_pair(raw_key, raw_val)
                    if k and v:
                        details[k] = v
                        continue

                # Second try: look for bold key element specifically
                key_elem = li.select_one("span.a-text-bold")
                if key_elem:
                    # value may be sibling span or rest of li text
                    val_elem = key_elem.find_next_sibling("span")
                    raw_key = key_elem.get_text(separator=' ', strip=True)
                    raw_val = val_elem.get_text(separator=' ', strip=True) if val_elem else ''
                    k, v = self.clean_detail_pair(raw_key, raw_val)
                    if k and v:
                        details[k] = v
                        continue

                # Fallback: try splitting the li text on ':' to produce key/value
                text = li.get_text(separator=' ', strip=True)
                if text and ':' in text:
                    parts = [p.strip() for p in text.split(':', 1)]
                    if len(parts) == 2 and parts[0]:
                        raw_key = parts[0].rstrip('\u200f\u200e').strip()
                        raw_val = parts[1]
                        k, v = self.clean_detail_pair(raw_key, raw_val)
                        if k and v:
                            details[k] = v
                            continue

                # Last resort: treat as a bullet point
                if text:
                    bullet_points.append(text)

        if bullet_points:
            details["Key Features"] = bullet_points

        return details

    def scrape_product_details(self, soup):
        details = {}

        table = soup.find("table", {"id": "productDetails_techSpec_section_1"})
        if not table:
            table = soup.find("table", {"id": "productDetails_detailBullets_sections1"})
        if not table:
            return details

        rows = table.find_all("tr")

        for row in rows:
            header = row.find("th")
            value = row.find("td")

            if not header or not value:
                continue

            key = header.get_text(separator=" ", strip=True)
            val = value.get_text(separator=" ", strip=True)

            # Clean weird unicode
            key = " ".join(key.split())
            val = " ".join(val.split())

            k, v = self.clean_detail_pair(key, val)
            if k and v:
                details[k] = v

        return details

