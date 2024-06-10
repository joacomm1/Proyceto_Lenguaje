from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup

# Leer nombres de productos desde el archivo
with open('productos_nombre.txt', 'r') as file:
    productos = file.read().splitlines()

print(productos)

# Configurar el servicio de ChromeDriver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Navegar a la página de Falabella
driver.get("https://falabella.com")
time.sleep(2)

# Encontrar la barra de búsqueda y buscar "iphone 15"
input_element = driver.find_element(By.ID, "testId-SearchBar-Input")
input_element.send_keys("iphone 15" + Keys.ENTER)

# Esperar a que se carguen los resultados
time.sleep(2)

# Extraer el contenido de la sección de resultados de búsqueda
for i in range(1, 7):
    try:
        # Crear el XPATH dinámicamente para cada iteración
        sXpath = f'//*[@id="testId-searchResults-products"]/div[{i}]'
        contentData = driver.find_element(By.XPATH, sXpath)
        htmlData = contentData.get_attribute('innerHTML')
        lxmlData = BeautifulSoup(htmlData, 'lxml')

        # Buscar los elementos específicos del nombre del producto
        nombre_producto = lxmlData.find_all('b', class_='jsx-2481219049 copy2 primary jsx-3451706699 normal line-clamp line-clamp-3 pod-subTitle subTitle-rebrand')

        # Buscar los precios con distintos medios de pago
        precios = lxmlData.find_all('li', class_='jsx-2112733514')

        # Extraer precios de cada medio de pago
        precio_cmr = next((li.get('data-cmr-price') for li in precios if li.get('data-cmr-price')), None)
        precio_internet = next((li.get('data-internet-price') for li in precios if li.get('data-internet-price')), None)
        precio_normal = next((li.get('data-normal-price') for li in precios if li.get('data-normal-price')), None)

        # Imprimir solo el contenido de texto del primer elemento encontrado, si existe
        if nombre_producto:
            nombre = nombre_producto[0].text
            print(f"Producto: {nombre}")
            if precio_cmr:
                print(f"Precio CMR: ${precio_cmr}")
            if precio_internet:
                print(f"Precio Internet: ${precio_internet}")
            if precio_normal:
                print(f"Precio Normal: ${precio_normal}")
    except Exception as e:
        print(f"Error al procesar el elemento {i}: {e}")
# Cerrar el navegador
driver.quit()
