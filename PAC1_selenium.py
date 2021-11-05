from selenium import webdriver
import sys
import os
import pandas as pd
from selenium.webdriver.common.by import By
import regex as re
from time import sleep
from random import randint

# URL de la que obtenemos la información
URL = "https://books.toscrape.com"

# Configuramos el webdriver
option = webdriver.ChromeOptions()
# Obtenemos el path de la carpeta actual
My_path = os.path.dirname(os.path.abspath("__file__"))

# Abrimos el navegador utilizando el archivo chromedriver (descargado de http://chromedriver.chromium.org/downloads)
browser = webdriver.Chrome(executable_path=My_path + '/chromedriver', options=option)

# Creamos el dataframe
datos = pd.DataFrame(columns=['titulo','precio','cantidad_stock','categoria','rating'])

current_page = 1
max_pages = 99
done = False

while (current_page <= max_pages) and (not done):
    # Seleccionamos un wait time entre 1 y 3 segundos para esperar entre peticiones a la página web
    waitTime = randint(1,3)
    print("Waiting", waitTime, "seconds to retrieve the items on page", URL)
    sleep(waitTime)
    try:
        browser.get(URL)
        print('Successfully accessed the web page:', URL)
    except:
        print('The server could not serve up the web page!')
        sys.exit('Script processing cannot continue!!!')
      
    book_section = browser.find_element(By.TAG_NAME, "ol")
    book_listing = book_section.find_elements(By.TAG_NAME, "li")
    book_page_browser = webdriver.Chrome(executable_path=My_path + '/chromedriver', options=option)

    for book_item in book_listing:
    	# Obtenemos la url de cada libro
        thumnail_container = book_item.find_element(By.CLASS_NAME, "image_container")
        detail_url = thumnail_container.find_element(By.TAG_NAME, "a").get_attribute("href")
        # Obtenemos el título del libro
        titulo = book_item.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a").get_attribute("title")
        # Obtenemos el precio del libro
        book_price_text = book_item.find_element(By.CLASS_NAME, "price_color").text
        try:
            precio = re.search(r"[0-9\.]+", book_price_text)[0]
        except AttributeError:
            precio = 0.00
        
        # De nuevo esperamos para hacer la petición al sitio web
        waitTime = randint(1,3)
        sleep(waitTime)
        book_page_browser = webdriver.Chrome(executable_path=My_path + '/chromedriver', options=option)
        try:
            book_page_browser.get(detail_url)
            print('Successfully accessed the web page:', detail_url)
        except:
            print('The server could not serve up the web page!')
            sys.exit('Script processing cannot continue!!!')

        product_container = book_page_browser.find_element(By.CLASS_NAME, "product_page")
        cat =  book_page_browser.find_element_by_xpath("//*[@id='default']/div/div/ul/li[3]/a").text
        rating = book_page_browser.find_element_by_xpath("//*[@id='content_inner']/article/div[1]/div[2]/p[3]").get_attribute("class")
        if rating == 'star-rating One':
            rating = 1
        elif rating == 'star-rating Two':
            rating = 2
        elif rating == 'star-rating Three':
            rating = 3
        elif rating == 'star-rating Four':
            rating = 4
        elif rating == 'star-rating Five':
            rating = 5
        product_description = product_container.find_elements(By.TAG_NAME, "p")[3].text
        table_rows = product_container.find_elements(By.TAG_NAME, "tr")
        item_quantity_text = table_rows[5].find_element(By.TAG_NAME, "td").text
        try:
            cant_stock = re.search(r"\d+", item_quantity_text)[0]
        except AttributeError:
            cant_stock = 0
        # Añadimos los datos al dataframe
        datos = datos.append({'titulo':titulo,'precio':precio, 'cantidad_stock':cant_stock, 'categoria':cat, 'rating':rating}, ignore_index=True)    
    
    book_page_browser.quit()

    try:
    	# Obtenemos la siguiente página
        next_button_element = browser.find_element(By.CLASS_NAME, "next")
        current_page = current_page + 1
        URL = next_button_element.find_element(By.TAG_NAME, "a").get_attribute("href")
    except:
        done = True
browser.quit()

# Guardamos los datos en un csv
datos.to_csv('bookstoscrape_selenium.csv', sep =';', index=False)