from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def resolve_affiliate_url(affiliate_url):
    try:
        response = requests.get(affiliate_url, allow_redirects=True)
        return response.url  # This is the final URL after all redirects
    except Exception as e:
        print(f"Error resolving affiliate URL: {e}")
        return None

def get_product_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')

        # Example for Shopee
        if 'shopee' in url:
            title_element = soup.find('div', {'class': '_3e_UQT'})  # Update class name
            price_element = soup.find('div', {'class': '_3n5NQx'})  # Update class name
            image_element = soup.find('img', {'class': '_3yZnxJ'})  # Update class name
        # Example for Lazada
        elif 'lazada' in url:
            title_element = soup.find('h1', {'class': 'pdp-mod-product-title'})
            price_element = soup.find('span', {'class': 'pdp-price_type_normal'})
            image_element = soup.find('img', {'class': 'pdp-mod-common-image'})
        # Example for Amazon
        elif 'amazon' in url:
            title_element = soup.find('span', {'id': 'productTitle'})
            price_element = soup.find('span', {'class': 'a-price-whole'})
            image_element = soup.find('img', {'id': 'landingImage'})
        else:
            return None

        # Check if elements were found
        if not all([title_element, price_element, image_element]):
            print("Failed to find one or more elements on the page.")
            return None

        title = title_element.text.strip()
        price = price_element.text.strip()
        image = image_element['src']

        return {
            'title': title,
            'price': price,
            'image': image,
            'url': url
        }
    except Exception as e:
        print(f"Error scraping product details: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        affiliate_url = request.form['url']
        final_url = resolve_affiliate_url(affiliate_url)
        if not final_url:
            return render_template('index.html', error="Failed to resolve affiliate URL.")

        product_details = get_product_details(final_url)
        if product_details:
            return render_template('index.html', product=product_details)
        else:
            return render_template('index.html', error="Invalid URL or unsupported website.")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)