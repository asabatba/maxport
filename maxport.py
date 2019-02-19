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

# funcion que espera a que se cargue la pagina (desaparezca el indicador de espera)


def esperar_carga(browser):
    time.sleep(0.5)
    WebDriverWait(browser, 20).until(
        EC.invisibility_of_element_located((By.ID, 'wait')))


# funcion que permite seleccionar por ID, con una espera adicional por si el elemnto aun no se ha cargado
def selGetById(browser, id):

    tiempo_corto = 0.2

    # se espera a que desaparezca el elemento DOM "wait"
    esperar_carga(browser)
    time.sleep(tiempo_corto)

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, id)))

    try:
        id_ele = browser.find_element_by_id(id)
    except Exception as err:
        # print()
        raise LookupError(
            "Error: No se ha podido encontrar el elemento con id={}\n{}".format(id, err))

    return id_ele


def isUsernameValid(username):
    if (username[:3] != 'U01' and username[:3] != 'u01'):
        print('El nombre de usuario es incorrecto (no empieza por U01)')
        return 0

    if (len(username) != 8):
        print('El numero de caracteres del usuario no es el adecuado (deberian ser 8)')
        return 0

    return 1


def isPasswordValid(password):
    if (len(password) != 8):
        print('La longitud del password no es la adecuada (deberia ser 8)')
        return 0

    return 1


def createUserJson():

    while True:
        user = input('Introduce el nombre del usuario (U01): ')
        if isUsernameValid(user):
            break

    while True:
        password = input('Introduce la contraseña para el usuario indicado: ')
        if isPasswordValid(password):
            break

    creds = {'usuario': user, 'password': password}

    with open('user.json', 'w') as f:
        json.dump(creds, f)
    print('Se ha generado el archivo user.json con los datos de inicio de sesión.')

    return creds


def chromeTest():

    # CONFIG #
    filtro_estado = "=ASSESS"
    tiempo_espera = 0.6
    
    dias_adelante = 12
    num_reintentos = 3
    # /CONFIG #

    try:
        with open('user.json', 'r') as f:
            creds = json.load(f)
            print('Se ha cargado el usuario {}.'.format(creds['usuario']))
            len(creds['password'])
    except FileNotFoundError:
        print('No se ha encontrado el fichero de configuración user.json, se procede a generar uno nuevo.')
        creds = createUserJson()

    except Exception:
        print('Ha habido un problema decodificando el fichero user.json, se procede a generar uno nuevo.')
        creds = createUserJson()

    filtrar_hasta = (datetime.datetime.today(
    )+datetime.timedelta(days=dias_adelante, hours=6)).strftime("<%d/%m/%Y %H:%M:%S")

    # filtro para cambios que sean actuales
    filtrar_desde = (datetime.datetime.today() -
                     datetime.timedelta(hours=12)).strftime(">%d/%m/%Y %H:%M:%S")

    # filtro_tiempo = ">{} AND <{}".format(filtrar_desde, filtrar_hasta)

    options = Options()
    # options.headless = True # si se comenta esta linea, Chrome es visible durante la ejecucion
    options.add_experimental_option("prefs", {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        # "safebrowsing.enabled": True
    })

    print('Se abre una versión controlada de Chrome.')
    browser = webdriver.Chrome(options=options)
    # browser.implicitly_wait(5)

    try:
        browser.get("https://maximo.lacaixa.es/")
    except Exception as err:
        # print()
        browser.close()
        raise ConnectionError(
            'Ha habido un problema abriendo el navegador en la url de Maximo\n\n{}'.format(err))
        # return 0
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
    # time.sleep(tiempo_espera)
    esperar_carga(browser)

    input_pass = selGetById(browser, "j_password")
    input_pass.send_keys(creds['password'])
    # time.sleep(tiempo_espera)
    esperar_carga(browser)

    input_user.submit()
    # time.sleep(tiempo_espera*3)

    try:
        welcome_msg = selGetById(browser, "txtappname")
    except Exception as err:
        browser.close()
        raise ConnectionRefusedError(
            'No se ha podido realizar login en Maximo. Es posible que los datos del usuario del fichero user.json sean incorrectos.\n{}'.format(err))

    print("Mensaje de bienvenida: {}".format(welcome_msg.text))

    listado_cambios = selGetById(browser, "mx228")

    listado_cambios.click()
    # time.sleep(tiempo_espera*2)
    esperar_carga(browser)

    input_estado = selGetById(browser, "mx781")
    time.sleep(tiempo_espera*3)
    esperar_carga(browser)
    input_estado.send_keys(filtro_estado)

    # filtro para inicio programado
    input_inicio_programado = selGetById(browser, "mx721")
    time.sleep(tiempo_espera*3)
    esperar_carga(browser)
    input_inicio_programado.send_keys(filtrar_hasta)

    time.sleep(tiempo_espera)

    # filtro para finalizacion programada
    input_inicio_programado = selGetById(browser, "mx733")
    time.sleep(tiempo_espera*3)
    esperar_carga(browser)
    input_inicio_programado.send_keys(filtrar_desde)

    # time.sleep(tiempo_espera)

    # darle al enter

    input_estado.send_keys(Keys.ENTER)
    # time.sleep(tiempo_espera*10)
    esperar_carga(browser)

    num_resultados = selGetById(browser, "mx257").text.split(" ")[-1]

    print("Núm de resultados después de filtrar: {}".format(num_resultados))

    for i in range(num_reintentos):
        try:
            boton_descarga = selGetById(browser, "mx260")
            boton_descarga.click()

        except Exception:
            print("Fallo {}, reintentando...".format(i+1))
            time.sleep(tiempo_espera*4)

        else:
            break

    time.sleep(tiempo_espera*10)

    browser.close()

    return 1


if __name__ == '__main__':

    chromeTest()
