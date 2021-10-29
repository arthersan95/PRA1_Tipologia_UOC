import requests
from bs4 import BeautifulSoup
import pandas as pd
import regex as re


# Definimios una función que, dado el link a una web, verifique la existencia del
# fichero robots.txt
def robots_txt (link):
    robot = requests.get(link+"/robots.txt",data =None)
    return robot.text
    
# Comprobamos el fichero robots.txt de la web sobre la que realizaremos la PRA:
print(robots_txt("http://books.toscrape.com"))

# Obtenemos un 404 (Not Found). Esto puede ser debido a que esta web está específicamente diseñada
# para practicar con Web Scraping, por lo que el contenido de este fichero para esta web puede ser
# innecesario.


# Definimos el dataframe que iremos completando haciendo Web Scraping:

datos = pd.DataFrame(columns=['titulo','precio','cantidad_stock','categoria','rating'])

# Definimos una funcion que, dada una página de la web BooksToScrape, extraiga los datos
# necesarios para construir el dataset:

def get_data_page (page):
    data = pd.DataFrame(columns=['titulo','precio','cantidad_stock','categoria','rating'])
    url ='http://books.toscrape.com/catalogue/page-{}.html'
    url_final = url.format(page)
    res = requests.get(url_final).text
    soup = BeautifulSoup(res,'html.parser')
    for element in soup.findAll('article', class_ = 'product_pod'):
        # Para cada url de cada libro
        # Hacemos el request a la url
        url_libro = 'https://books.toscrape.com/catalogue/'+element.div.a.get('href')
        get_url_libro = requests.get(url_libro)
        soup = BeautifulSoup(get_url_libro.text, 'html.parser')
        # Obtenemos los campos que buscamos
        titulo = soup.find("div", class_ = re.compile("product_main")).h1.text
        precio = soup.find("p", class_ = "price_color").text[2:]
        cant_stock = re.sub("[^0-9]", "", soup.find("p", class_ = "instock availability").text)
        cat = re.sub("[^a-zA-Z\-]","", soup.find("a", href = re.compile("../category/books/")).get("href").split("/")[3])
        cat = re.sub("[\-]"," ", cat)
        rating = soup.find("p", class_ = re.compile("star-rating")).get("class")[1]
        if rating == 'One':
            rating = 1
        elif rating == 'Two':
            rating = 2
        elif rating == 'Three':
            rating = 3
        elif rating == 'Four':
            rating = 4
        elif rating == 'Five':
            rating = 5
        # Añadimos los datos al dataframe
        data = data.append({'titulo':titulo,'precio':precio, 'cantidad_stock':cant_stock, 'categoria':cat, 'rating':rating}, ignore_index=True)
    return data               

for page in range(1,51):
    datos = datos.append(get_data_page(page))

# Breve análisis de las variables del dataset obtenido:

#Comprobamos que no tenemos valores nulos ni vacíos:
        
(datos.isnull()).sum()
(datos.values=="").sum()

# Comprobamos el tipo de las variables:

datos.dtypes

# Pasamos las variables cuantitativas a numeric:

datos['precio'] = pd.to_numeric(datos['precio'])
datos['cantidad_stock'] = pd.to_numeric(datos['cantidad_stock'])
datos['rating'] = pd.to_numeric(datos['rating'])


# Resumen estadístico de los datos cuantitativos:

stats = datos[['precio', 'cantidad_stock', 'rating']].describe()

# Matriz de correlación:

corr_matrix = datos.corr()

# Como podemos comprobar, no tenemos ninguna correlación significativa con ninguna de las varialbes.
# Esto podría ser debido a tratrse de datos aleatorios.

# Generamos el fichero .csv

datos.to_csv('bookstoscrape.csv', sep =';', index=False)