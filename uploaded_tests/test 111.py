def test_user_code():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import NoSuchElementException
    import time
    
    def test_navigation():
        chrome_options = Options()
        # НЕ использовать headless!
        # chrome_options.add_argument("--headless")
    
        driver = webdriver.Chrome(options=chrome_options)  # путь можно указать, если не работает
    
        try:
            driver.get("https://tutorial.djangogirls.org/ru/")
            time.sleep(2)
    
            button = driver.find_element("link text", "Начало работы с Django")
            button.click()
            time.sleep(2)
    
            current_url = driver.current_url
            assert current_url == "https://tutorial.djangogirls.org/ru/django_start_project/", \
                f"Ожидался URL https://tutorial.djangogirls.org/ru/django_start_project/, но получен {current_url}"
    
        except NoSuchElementException:
            assert False, "Кнопка не найдена"
    
        finally:
            input("Нажми Enter, чтобы закрыть браузер...")
            driver.quit()
