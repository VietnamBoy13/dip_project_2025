import os, subprocess
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .models import TestRun
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time

def home(request):
    if request.method == 'POST':
        name = request.POST.get('test_name', 'uploaded_test')
        code = request.POST.get('code_area')
        file = request.FILES.get('test_file')

        test_dir = 'uploaded_tests'
        os.makedirs(test_dir, exist_ok=True)
        filepath = os.path.join(test_dir, f"{name}.py")

        if file:
            fs = FileSystemStorage(location=test_dir)
            filename = fs.save(file.name, file)
            filepath = os.path.join(test_dir, filename)
        elif code:
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError as e:
                return HttpResponse(f"Ошибка в коде: {e}")

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("def test_user_code():\n")
                for line in code.splitlines():
                    f.write("    " + line + "\n")

        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{name}.log")
        report_dir = 'reports'
        os.makedirs(report_dir, exist_ok=True)
        report_file = os.path.join(report_dir, f"{name}.html")

        with open(log_file, 'w') as log:
            result = subprocess.run([
                'pytest', filepath, f'--html={report_file}', '--self-contained-html'
            ], stdout=log, stderr=log)

        status = "success" if result.returncode == 0 else "fail"
        TestRun.objects.create(name=name, status=status, log_path=log_file)

        return redirect('home')

    runs = TestRun.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'runs': runs})


def report_view(request, run_id):
    run = get_object_or_404(TestRun, id=run_id)
    # читаем лог
    try:
        with open(os.path.join(settings.BASE_DIR, run.log_path), encoding='utf-8') as f:
            log_content = f.read()
    except Exception:
        log_content = "Не удалось прочитать лог."

    return render(request, 'reports/report_template.html', {
        'run': run,
        'log_content': log_content
    })
def run_demo_test(request):
    # Настройки headless-браузера (без GUI)
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)  # Укажите путь, если нужно

    test_result = {
        'passed': False,
        'error': '',
        'log': ''
    }

    try:
        driver.get("https://tutorial.djangogirls.org/ru/")
        test_result['log'] += "Открыта главная страница.\n"

        # Ждём немного, чтобы страница прогрузилась
        time.sleep(2)

        # Находим кнопку по XPath
        button = driver.find_element("xpath", "/html/body/div/div[1]/nav/ul/li[11]")
        test_result['log'] += "Кнопка найдена.\n"

        button.click()
        test_result['log'] += "Клик по кнопке выполнен.\n"

        time.sleep(2)

        current_url = driver.current_url
        test_result['log'] += f"Текущий URL после клика: {current_url}\n"

        if current_url == "https://tutorial.djangogirls.org/ru/django_start_project/":
            test_result['passed'] = True
            test_result['log'] += "Тест пройден успешно.\n"
        else:
            test_result['error'] = f"Ожидался URL https://tutorial.djangogirls.org/ru/django_start_project/, но получен {current_url}"

    except NoSuchElementException:
        test_result['error'] = "Кнопка по заданному XPath не найдена."
    except Exception as e:
        test_result['error'] = str(e)
    finally:
        driver.quit()

    return render(request, "demo_test_result.html", {'result': test_result})