from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import undetected_chromedriver as uc

from database import MongoConnector
from product import Product
from fastapi import FastAPI
from api.v1 import api_endpoints

# from fastapi.middleware.wsgi import WSGIMiddleware
# from dash_pages import app_dash


# Added options to run code in headless mode. For this to run, added version_main when instantiating driver
options = uc.ChromeOptions()
options.add_argument('--headless')

chrome_path = 'C:/Users/George/Desktop/chromedrive/chromedriver.exe'
s = Service(chrome_path)
driver = uc.Chrome(service=s, version_main=112, options=options)

now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
connector = MongoConnector()
urls_data = connector.list('urls')
# you can also add a list of urls to insert in mongo db
urls = []
if not urls:
    urls = [url["link"] for url in urls_data]


app = FastAPI()
app.include_router(api_endpoints)
# app.mount("/dash", WSGIMiddleware(app_dash))


if __name__ == '__main__':
    # print(urls)
    for url in urls:
        # uncomment if you want to insert the links in the db automatically
        # link_dict = {'link': url}
        # connector.insert_one('urls', link_dict)
        driver.get(url)
        product = {}

        # Get product name
        product_name = driver.find_element(By.CLASS_NAME, 'page-title')
        # adding strip( to get rid of the new lines in print)
        product_text = product_name.get_attribute('textContent').strip()
        product.update({"product_name": product_text})
        # print({"product name": product_text})

        # Get price history and associate it with dates
        price_element = driver.find_element(By.CLASS_NAME, 'product-new-price')
        price_text = price_element.get_attribute('textContent').split(" ")
        price = float(price_text[0].strip().replace(',', '.'))
        product.update({"price_history": [{"date": now, "price": price}]})

        # print({"price": price_text[0], "currency": price_text[-1]})

        # Get image
        # image = driver.find_element(By.CSS_SELECTOR, 'img')
        # image_src = image.get_attribute('src')
        image = driver.find_element(By.CLASS_NAME, 'product-gallery-image')
        image_src = image.get_attribute('href')

        product.update({"image": image_src})

        # print({"image": image_src})
        # time.sleep(3)

        # Get sku
        # the text is fetched as str:"Cod produs: 8006540067550"
        sku = driver.find_element(By.XPATH, "//span[@class='product-code-display hidden-xs']").text.split(":")[-1].strip()
        # sku_text = sku.get_attribute('textContent')
        product.update({"sku": sku})

        # scraping recommendation section
        recommended_carousel = driver.find_element(By.CSS_SELECTOR, 'section.page-section-slot-1')
        data_carousel = recommended_carousel.find_elements(By.CLASS_NAME, 'rec-card-item')
        # getting data per article. The page is dynamic so recommendations change
        recommendation_list = []
        for recommendation in data_carousel:
            art = recommendation.get_attribute('data-name')
            # print(type(art))
            recommendation_list.append(art)
        # added the below line because the code crashed after the section was modified on the website
        # and had items of <class 'NoneType'> causing Pydantic validation errors
        recommendation_list = [item for item in recommendation_list if item is not None]
        product.update({'recommendations': recommendation_list})


        # Create a Product object with the data from the dictionary scraped
        my_product = Product(**product)

        result_product = connector.read_sku('products', my_product.sku)

        if result_product:
            db_product = Product(**result_product)
            last_price = db_product.price_history[-1]['price']
            print(f'Last price from the database is {last_price}')
            if my_product.price_history[0]['price'] != last_price:
                # Update the price_history with the new date and price
                connector.update_history('products', my_product.sku, my_product.price_history[0])
                print(f"Price history updated for SKU: {my_product.sku}")
            else:
                print(f"Price remains the same for SKU: {my_product.sku}")
            if my_product.image != result_product['image']:
                connector.update_one('products', {'image': result_product['image']}, {'image': my_product.image})
                print('Images updated in the database.')
            else:
                print(f"Image remains the same for SKU: {my_product.sku}")
        else:
            # Insert the whole product with the initial price_history
            connector.insert_one('products', my_product.dict())
            print(f"Product inserted with SKU: {my_product.sku}")

    # Launch the application
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")


