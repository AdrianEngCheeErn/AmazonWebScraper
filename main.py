import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd


#Used to go through amazon's bot detector
custom_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'da, en-gb, en',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}

visited_urls = set()

def get_product_info(url):
    response = requests.get(url, headers=custom_headers)
    if response.status_code != 200:
        print(f"Error in getting webpage: {url}")
        return None

    soup = BeautifulSoup(response.text, "lxml")

    title_element = soup.select_one("#productTitle")
    title = title_element.text.strip() if title_element else None

    price_element = soup.select_one('span.a-offscreen')
    price = price_element.text if price_element else None

    rating_element = soup.select_one("#acrPopover")
    print(rating_element)
    rating_text = rating_element.attrs.get("title") if rating_element else None
    print(rating_text)
    rating = rating_text.replace("out of 5 stars", "") if rating_text else None

    image_element = soup.select_one("#landingImage")
    image = image_element.attrs.get("src") if image_element else None

    description_element = soup.select_one("#productDescription")
    description = description_element.text.strip() if description_element else None

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "image": image,
        "description": description,
        "url": url
    }   


def parse_listing(listing_url):
    response = requests.get(listing_url, headers=custom_headers)
    print(response.status_code)
    soup_search = BeautifulSoup(response.text, "lxml")
    
    #Select all the links to each product 
    link_elements = soup_search.select("[data-asin] h2 a")
    page_data = []

    for link in link_elements:
        full_url = urljoin(listing_url, link.attrs.get("href"))
        if full_url not in visited_urls:
            visited_urls.add(full_url)
            product_info = get_product_info(full_url)
            if product_info:
                page_data.append(product_info)

    #get link to next amazon page
    next_page_el = soup_search.select_one('a.s-pagination-next')
    print(next_page_el)
    if next_page_el:
        next_page_url = next_page_el.attrs.get('href')
        next_page_url = urljoin(listing_url, next_page_url)
        print(f'Scraping next page: {next_page_url}', flush=True)
        page_data += parse_listing(next_page_url)

    return page_data


get_product_info('https://www.amazon.com/Bose-QuietComfort-Cancelling-Headphones-Bluetooth/dp/B0CCZ26B5V/ref=sr_1_3?dib=eyJ2IjoiMSJ9.pCIyXyl6jitR9GPiizoNP72thzeyC_Ne2vKN8vfn0EoFJesKPAi-o6MZSRMsZbMWnFj6BqMN6kRLefJ-pcWkVSpc2L9K9GZUdRHe6JXaNy9yWgFMoHzElIiDtrAimhGvjDQtn9Y1qVx4-nbim1pz5xrQTWdMGr9HVwAgBiepQA1aSbTyzauhwjrCkInddad2OjlSNISRf00Cv7vfMWklVDrDRUOHZNf6xEa1RBH-5g-9xDgFJh3D4SgC7FpK-JpUX4rERxInyWTO7p_mDl-bc1szCOsEgY-5WHnMM08YjnM.e4p6pmXYaT974h-kPBhCBIOAwCvGO_Sb2uMDoVBPlXY&dib_tag=se&keywords=bose&qid=1710049796&s=aht&sr=1-3&th=1')


search_url = "https://www.amazon.com/s?k=bose&rh=n%3A12097479011&ref=nb_sb_noss"
data = parse_listing(search_url)
print(data)