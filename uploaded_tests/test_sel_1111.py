from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time

def test_navigation():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)  # укажите путь к chromedriver, если нужно

    try:
        driver.get("https://tutorial.djangogirls.org/ru/")
        time.sleep(2)  # ждем загрузку страницы

        button = driver.find_element("xpath", "/html/body/div/div[1]/nav/ul/li[11]")
        button.click()
        time.sleep(2)  # ждем перехода

        current_url = driver.current_url
        assert current_url == "https://tutorial.djangogirls.org/ru/django_start_project/", \
            f"Ожидался URL https://tutorial.djangogirls.org/ru/django_start_project/, но получен {current_url}"

    except NoSuchElementException:
        assert False, "Кнопка по XPath не найдена"

    finally:
        driver.quit()
