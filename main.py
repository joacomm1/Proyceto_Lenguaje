from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import csv

# Leer nombres de productos desde el archivo
with open('productos_nombre.txt', 'r') as file:
    productos = file.read().splitlines()

# Configurar el servicio de ChromeDriver
service = Service(executable_path="chromedriver.exe")

# Matriz para almacenar los resultados
resultados = []

def extract_product_info(html, tienda):
    soup = BeautifulSoup(html, 'lxml')

    # Extraer nombre del producto
    if(tienda == "Ripley"):
        nombre_producto = soup.find_all('div', class_='catalog-product-details__name')
        nombre_producto = nombre_producto[0].text
    if(tienda == "Falabella"):
        nombre_producto = soup.find_all('b', class_='jsx-2481219049 copy2 primary jsx-3451706699 normal line-clamp line-clamp-3 pod-subTitle subTitle-rebrand')
        nombre_producto = nombre_producto[0].text
    # Extraer precios
    precio_normal = soup.find('li', class_='catalog-prices__list-price') or \
                    next((li.get('data-normal-price') for li in soup.find_all('li', class_='jsx-2112733514') if li.get('data-normal-price')), 'No disponible')
    precio_normal = precio_normal.text.strip() if hasattr(precio_normal, 'text') else precio_normal

    precio_internet = soup.find('li', class_='catalog-prices__offer-price') or \
                      next((li.get('data-internet-price') for li in soup.find_all('li', class_='jsx-2112733514') if li.get('data-internet-price')), 'No disponible')
    precio_internet = precio_internet.text.strip() if hasattr(precio_internet, 'text') else precio_internet

    precio_tarjeta = soup.find('li', class_='catalog-prices__card-price') or \
                     next((li.get('data-cmr-price') for li in soup.find_all('li', class_='jsx-2112733514') if li.get('data-cmr-price')), 'No disponible')
    precio_tarjeta = precio_tarjeta.text.strip().split()[0] if hasattr(precio_tarjeta, 'text') else precio_tarjeta

    return [nombre_producto, precio_tarjeta, precio_internet, precio_normal, tienda]

def precios_productos_FALABELLA(productos, resultados):
    # Configurar el servicio de ChromeDriver
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    
    # Navegar a la página de Falabella
    driver.get("https://falabella.com")
    time.sleep(2)

    for producto in productos:
        input_element = driver.find_element(By.ID, "testId-SearchBar-Input")
        input_element.send_keys(Keys.CONTROL + "a")  # Seleccionar todo el texto existente
        input_element.send_keys(Keys.DELETE)  # Borrar el texto seleccionado
        input_element.send_keys(f"{producto}" + Keys.ENTER)
        time.sleep(3)

        for i in range(1, 10):
            try:
                # Crear el XPATH dinámicamente para cada iteración
                sXpath = f'//*[@id="testId-searchResults-products"]/div[{i}]'
                contentData = driver.find_element(By.XPATH, sXpath)
                htmlData = contentData.get_attribute('innerHTML')
                product_info = extract_product_info(htmlData, "Falabella")
                resultados.append(product_info)
            except Exception as e:
                print(f"Error al procesar el elemento {i}: {e}")
    
    # Cerrar el navegador
    driver.quit()
    
    return resultados

def precios_productos_RIPLEY(productos, resultados):
    # Configurar el servicio de ChromeDriver
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    
    # Navegar a la página de Ripley
    driver.get("https://simple.ripley.cl/")
    time.sleep(2)

    for producto in productos:
        input_element = driver.find_element(By.XPATH, '//*[@id="ripley-sticky-header"]/section/nav/div/ul/li/div[1]/div[1]/input')
        input_element.send_keys(Keys.CONTROL + "a")  # Seleccionar todo el texto existente
        input_element.send_keys(Keys.DELETE)  # Borrar el texto seleccionado
        input_element.send_keys(f"{producto}" + Keys.ENTER)
        time.sleep(3)

        # Encontrar todos los elementos con la clase `catalog-product-details`
        content_data_elements = driver.find_elements(By.CLASS_NAME, 'catalog-product-details')
        
        # Limitar el procesamiento a los primeros 10 elementos
        for index, contentData in enumerate(content_data_elements[:10]):
            try:
                htmlData = contentData.get_attribute('innerHTML')
                product_info = extract_product_info(htmlData, "Ripley")
                resultados.append(product_info)
            except Exception as e:
                print(f"Error al procesar el elemento {index+1}: {e}")
    
    # Cerrar el navegador
    driver.quit()
    
    return resultados

# Obtener resultados de Falabella y Ripley
resultados = precios_productos_FALABELLA(productos, resultados)
resultados = precios_productos_RIPLEY(productos, resultados)

# Imprimir los resultados combinados
for resultado in resultados:
    print(resultado)
# Nombre del archivo CSV
archivo_csv = 'resultados_productos.csv'

# Escribir los resultados en el archivo CSV
with open(archivo_csv, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Escribir encabezados
    writer.writerow(['Nombre', 'Precio Tarjeta', 'Precio Internet', 'Precio Normal', 'Tienda'])
    
    # Escribir resultados
    for resultado in resultados:
        writer.writerow(resultado)