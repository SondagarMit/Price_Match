// Price Scraper Frontend JavaScript

// Auto-detect API base URL for both localhost and production
const getApiBaseUrl = () => {
    // If we're on the same origin, use relative URLs
    // Otherwise, use the current origin
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // For production, use the same origin
    // For localhost, also use the same origin (relative URLs work)
    return ''; // Empty string means relative URLs (same origin)
};

const API_BASE_URL = getApiBaseUrl();

const platformSelect = document.getElementById('platform');
const urlInput = document.getElementById('url');
const searchBtn = document.getElementById('searchBtn');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');
const resultsDiv = document.getElementById('results');

// Result elements
const productImage = document.getElementById('productImage');
const productTitle = document.getElementById('productTitle');
const productPrice = document.getElementById('productPrice');
const productRating = document.getElementById('productRating');
const productAvailability = document.getElementById('productAvailability');
const productDescription = document.getElementById('productDescription');
const productUrl = document.getElementById('productUrl');
const productDetailsTable = document.getElementById('productDetailsTable');
const productDetailsList = document.getElementById('productDetailsList');

// Hide error and results initially
function hideAll() {
    loadingDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
    resultsDiv.classList.add('hidden');
}

// Show error message
function showError(message) {
    hideAll();
    errorMessage.textContent = message;
    errorDiv.classList.remove('hidden');
}

// Show loading state
function showLoading() {
    hideAll();
    loadingDiv.classList.remove('hidden');
}

// Display results
function displayResults(data) {
    hideAll();
    
    // Set product image
    if (data.image) {
        productImage.src = data.image;
        productImage.alt = data.title || 'Product Image';
    } else {
        productImage.src = 'https://via.placeholder.com/400x400?text=No+Image';
    }
    
    // Set product title
    productTitle.textContent = data.title || 'N/A';
    
    // Set price
    if (data.price) {
        productPrice.textContent = `₹${data.price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    } else if (data.price_text) {
        productPrice.textContent = data.price_text;
    } else {
        productPrice.textContent = 'N/A';
    }
    
    // Set rating
    if (data.rating) {
        productRating.textContent = data.rating.toFixed(1);
        // Update star display (simple version - could be enhanced)
        const stars = productRating.parentElement.querySelectorAll('.fa-star');
        const fullStars = Math.floor(data.rating);
        const hasHalfStar = data.rating % 1 >= 0.5;
        
        stars.forEach((star, index) => {
            if (index < fullStars) {
                star.classList.add('text-yellow-400');
                star.classList.remove('text-gray-300');
            } else if (index === fullStars && hasHalfStar) {
                star.classList.add('fa-star-half-alt');
                star.classList.remove('fa-star');
                star.classList.add('text-yellow-400');
                star.classList.remove('text-gray-300');
            } else {
                star.classList.add('text-gray-300');
                star.classList.remove('text-yellow-400');
            }
        });
    } else {
        productRating.textContent = 'N/A';
    }
    
    // Set availability
    // Availability styling helper: colored badge with subtle background
    function styleAvailability(status) {
        if (!status) return `<span style="color: #6b7280; font-weight:600;">N/A</span>`;

        let lower = status.toLowerCase();

        // Green badge for available / in stock
        if (lower.includes("in stock") || lower.includes("available")) {
            return `<span style="background: rgba(22,198,12,0.12); color: #16c60c; padding: 6px 10px; border-radius: 8px; font-weight:600; display:inline-block;">${status}</span>`;
        }

        // Red badge for out of stock / unavailable
        return `<span style="background: rgba(232,27,35,0.10); color: #e81123; padding: 6px 10px; border-radius: 8px; font-weight:600; display:inline-block;">${status}</span>`;
    }

    productAvailability.innerHTML = styleAvailability(data.availability);
    
    // Set description
    productDescription.textContent = data.description || 'No description available';
    
    // Render product details (key/value pairs and Key Features list)
    try {
        const details = (data && data.details) ? data.details : {};
        const features = details['Key Features'];

        // Helper to escape user-supplied keys for RegExp
        const escapeRegExp = (str) => String(str).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

        // Debug: log raw details object for troubleshooting
        try {
            console.debug && console.debug('Product details (raw):', details);
            // Also log using console.log so it's visible even when debug is filtered
            try { console.log('Product details (log):', details); } catch (e) {}
        } catch (e) {
            // ignore console errors in older browsers
        }

        if (!productDetailsTable || !productDetailsList) {
            // Elements not present in DOM; skip rendering but log for debugging
            console.warn('Product details containers not found in DOM');
        } else {
            // Clear previous contents
            productDetailsTable.innerHTML = '';
            productDetailsList.innerHTML = '';

            // Build simple key: value lines (one per entry) — cleaner layout for Product Details
            const entries = Object.entries(details).filter(([k]) => k !== 'Key Features');
            if (entries.length > 0) {
                // helper to normalize whitespace and remove invisible unicode markers
                const normalize = (s) => ('' + (s || '')).replace(/\u200f|\u200e|\u202a|\u202c/g, '').replace(/\s+/g, ' ').trim();

                // Build a map to deduplicate keys while preserving insertion order
                const seen = new Map();

                entries.forEach(([rawK, rawV]) => {
                    let k = normalize(rawK);
                    let v = normalize(rawV);

                    // If the raw key itself contains a colon and appears to include both key and value,
                    // and the raw value is just the repeated key (or empty), split the raw key into key/value.
                    if (k.includes(':')) {
                        const parts = k.split(':');
                        const left = parts.shift().trim();
                        const right = parts.join(':').trim();

                        const vStripped = (v || '').replace(/:$/, '').trim();

                        // Conditions where splitting makes sense:
                        // - value is empty or equals the left (possibly with trailing colon)
                        // - value starts/contains only the left
                        if (right && (!v || v === '' || vStripped.toLowerCase() === left.toLowerCase() || vStripped.toLowerCase().startsWith(left.toLowerCase()))) {
                            k = left;
                            v = right;
                        } else if (!right && (!v || v === '')) {
                            // If no right part and value empty, keep left as key and leave value empty
                            k = left;
                        }
                    }

                    // If value empty but key contains a colon with value, split it (fallback)
                    if ((!v || v === '') && /:/.test(k)) {
                        const parts = k.split(':');
                        k = parts.shift().trim();
                        v = parts.join(':').trim();
                    }

                    // If value still appears to contain only the key (e.g., "Batteries :"), strip that
                    try {
                        const keyEsc = escapeRegExp(k);
                        const trailingPattern = new RegExp(':\\s*' + keyEsc + '\\s*:?$', 'i');
                        if (trailingPattern.test(v)) {
                            v = v.replace(trailingPattern, '').trim();
                        }
                        const leadingPattern = new RegExp('^' + keyEsc + '\\s*:?\\s*', 'i');
                        if (leadingPattern.test(v) && v.toLowerCase() !== k.toLowerCase()) {
                            v = v.replace(leadingPattern, '').trim();
                        }
                    } catch (err) {
                        // ignore regex issues for very long keys
                    }

                    // If key already seen, prefer the non-empty value
                    if (seen.has(k)) {
                        const existing = seen.get(k);
                        if ((!existing || existing === '') && v) {
                            seen.set(k, v);
                        }
                    } else {
                        seen.set(k, v);
                    }
                });

                // Render lines from the map: left = key:, right = value
                for (const [k, v] of seen.entries()) {
                    // Skip empty keys
                    if (!k) continue;

                    const row = document.createElement('div');
                    row.className = 'py-1';

                    const keyEl = document.createElement('span');
                    keyEl.className = 'font-semibold text-gray-800 mr-1';

                    const valEl = document.createElement('span');
                    valEl.className = 'text-gray-700';

                    // Normalize for rendering (remove invisible unicode and extra spaces)
                    const renderKey = ('' + (k || '')).replace(/\u200f|\u200e|\u202a|\u202c/g, '').replace(/\s+/g, ' ').trim();
                    let renderVal = ('' + (v || '')).replace(/\u200f|\u200e|\u202a|\u202c/g, '').replace(/\s+/g, ' ').trim();

                    // Remove any repeated key text from the value (leading/trailing)
                    try {
                        const keyEsc = escapeRegExp(renderKey);
                        renderVal = renderVal.replace(new RegExp('^' + keyEsc + '\\s*:?\\s*', 'i'), '').replace(new RegExp(':?\\s*' + keyEsc + '\\s*:?$', 'i'), '').trim();
                    } catch (err) {
                        // ignore regex errors for pathological keys
                    }

                    // Final key should not include a trailing colon
                    const finalKey = renderKey.replace(/:$/, '').trim();

                    // Set text: key with single trailing colon, value only
                    keyEl.textContent = finalKey ? finalKey + ':' : '';
                    valEl.textContent = renderVal || '';

                    row.appendChild(keyEl);
                    row.appendChild(valEl);
                    productDetailsTable.appendChild(row);
                }

                // Debug: rendered HTML
                try { console.debug && console.debug('Product details (rendered lines):', productDetailsTable.innerHTML); } catch (e) {}
                // Also log rendered HTML to console.log for visibility
                try { console.log('Product details (rendered HTML):', productDetailsTable.innerHTML); } catch (e) {}
            }

            // (Key Features rendering removed per user request)

            // If no details found, show a placeholder message
            if (entries.length === 0 && (!features || features.length === 0)) {
                productDetailsTable.textContent = 'No product details available.';
                try { console.debug && console.debug('Product details: none available'); } catch (e) {}
            }
        }
    } catch (e) {
        console.error('Failed to render product details:', e);
    }

    // Set product URL
    if (data.url) {
        productUrl.href = data.url;
    }
    
    // Show results
    resultsDiv.classList.remove('hidden');
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Handle search button click
searchBtn.addEventListener('click', async () => {
    const platform = platformSelect.value;
    const url = urlInput.value.trim();
    
    // Validate inputs
    if (!url) {
        showError('Please enter a product URL');
        return;
    }
    
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        showError('Please enter a valid URL (must start with http:// or https://)');
        return;
    }
    
    // Show loading
    showLoading();
    
    try {
        // Make API request
        const apiUrl = `${API_BASE_URL}/api/scrape?platform=${encodeURIComponent(platform)}&url=${encodeURIComponent(url)}`;
        const response = await fetch(apiUrl);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Failed to scrape product');
        }
        
        if (result.success && result.data) {
            displayResults(result.data);
        } else {
            showError('No data received from server');
        }
    } catch (error) {
        showError(error.message || 'An error occurred while scraping the product');
    }
});

// Allow Enter key to trigger search
urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchBtn.click();
    }
});

// Check platform status on load
async function checkPlatforms() {
    try {
        const apiUrl = `${API_BASE_URL}/api/platforms`;
        const response = await fetch(apiUrl);
        const data = await response.json();
        
        // Update platform select options based on availability
        if (data.platforms) {
            data.platforms.forEach(platform => {
                const option = platformSelect.querySelector(`option[value="${platform.name}"]`);
                if (option) {
                    if (!platform.available) {
                        option.disabled = true;
                        option.textContent = `${platform.name.charAt(0).toUpperCase() + platform.name.slice(1)} (Coming Soon)`;
                    }
                }
            });
        }
    } catch (error) {
        console.error('Failed to fetch platform status:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkPlatforms();
    hideAll();
});

