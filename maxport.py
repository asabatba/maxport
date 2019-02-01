import time
# import requests
# import csv
import os
import datetime
# from random import uniform
# from sys import argv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
# from joblib import Parallel, delayed
# import concurrent.futures
import json


def secondsBetween(t_start, t_final):
    seconds = t_final.tm_sec - t_start.tm_sec
    minutes = t_final.tm_min - t_start.tm_min
    hours = t_final.tm_hour - t_start.tm_hour
    return seconds + minutes*60 + hours*3600


class element_has_css_class(object):
    """An expectation for checking that an element has a particular css class.

    locator - used to find the element
    returns the WebElement once it has the particular css class
    """

    def __init__(self, locator, css_class):
        self.locator = locator
        self.css_class = css_class

    def __call__(self, driver):
        # Finding the referenced element
        element = driver.find_element(*self.locator)
        if self.css_class in element.get_attribute("class"):
            return element
        else:
            return False


# funcion que permite seleccionar por ID, con una espera adicional por si el elemnto aun no se ha cargado
def selGetById(browser, id):
    
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, id)))

    try:
        id_ele = browser.find_element_by_id(id)
    except Exception as err:
        # print()
        raise LookupError("Error: No se ha podido encontrar el elemento con id={}\n{}".format(id,err))
        

    return id_ele


def chromeTest():

    # time.sleep(uniform(0, 2))

    with open('user.json', 'r') as f:
        creds = json.load(f)

    filtro_estado = "=ASSESS"

    tiempo_espera = 0.5

    filtrar_hasta = ( datetime.datetime.today()+datetime.timedelta(days=12, hours=6) ).strftime("<%d/%m/%Y %H:%M:%S")


    options = Options()
    # options.headless = True # si se comenta esta linea, Chrome es visible durante la ejecucion
    options.add_experimental_option("prefs", {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        # "safebrowsing.enabled": True
    })

    browser = webdriver.Chrome(options=options)
    # browser.implicitly_wait(5)

    try:
        browser.get("https://maximo.lacaixa.es/")
    except Exception as err:
        print('Problema de conexión con la url\n{}'.format(err))
        browser.close()
        return 0
        # return None, None, None
    # browser.close()
    # return 1

    # try:
    #     WebDriverWait(browser, 10).until(
    #         EC.presence_of_element_located((By.ID, "j_username")))
    #     # assert "Welcome to People Contract Map" in browser.page_source
    # except:
    #     print("Error: La página de login no es la esperada o no se ha podido cargar.")
    #     browser.close()
    #     # return t_start, 'E'
    #     # return None, None, None



    input_user = selGetById(browser, "j_username")
    input_user.send_keys(creds['usuario'])
    time.sleep(tiempo_espera)

    input_pass = selGetById(browser, "j_password")
    input_pass.send_keys(creds['password'])
    time.sleep(tiempo_espera)

    input_user.submit()
    time.sleep(tiempo_espera*3)

    welcome_msg = selGetById(browser, "txtappname")

    print("Mensaje de bienvenida: {}".format(welcome_msg.text))


    listado_cambios = selGetById(browser, "mx228")

    listado_cambios.click()
    time.sleep(tiempo_espera*3)

    input_estado = selGetById(browser, "mx781")
    time.sleep(tiempo_espera*3)
    input_estado.send_keys(filtro_estado)

    input_inicio_programado = selGetById(browser, "mx721")
    time.sleep(tiempo_espera*3)
    input_inicio_programado.send_keys(filtrar_hasta)

    time.sleep(tiempo_espera)

    input_estado.send_keys(Keys.ENTER)
    time.sleep(tiempo_espera*10)


    num_resultados = selGetById(browser, "mx257").text.split(" ")[-1]

    print("Núm de resultados después de filtrar: {}".format(num_resultados))

    boton_descarga = selGetById(browser, "mx260")
    boton_descarga.click()
    time.sleep(tiempo_espera*4)

    browser.close()

    return 1



if __name__ == '__main__':

    chromeTest()


