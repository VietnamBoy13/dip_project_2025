import os
import subprocess
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .models import Test, TestCase, TestResult, User
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from .forms import CustomLoginForm, CustomUserCreationForm

def index(request):
    return render(request, 'index.html')

@login_required
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

        # Попробуем найти Test с таким именем или создадим (если нужно)
        test_obj, created = Test.objects.get_or_create(name=name, defaults={'created_by': request.user})

        # Создаём запись результата теста
        TestResult.objects.create(
            test=test_obj,
            user=request.user,
            status=status,
            report_path=report_file,
        )

        return redirect('home')

    # Показываем все результаты запусков, последние сверху
    runs = TestResult.objects.all().order_by('-run_at')
    return render(request, 'home.html', {'runs': runs})


@login_required
def report_view(request, run_id):
    run = get_object_or_404(TestResult, id=run_id)
    try:
        with open(os.path.join(settings.BASE_DIR, run.report_path), encoding='utf-8') as f:
            report_content = f.read()
    except Exception:
        report_content = "Не удалось прочитать отчет."

    try:
        with open(os.path.join(settings.BASE_DIR, run.report_path.replace('.html', '.log')), encoding='utf-8') as f:
            log_content = f.read()
    except Exception:
        log_content = "Не удалось прочитать лог."

    return render(request, 'reports/report_template.html', {
        'run': run,
        'report_content': report_content,
        'log_content': log_content,
    })


def run_demo_test(request):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    test_result = {
        'passed': False,
        'error': '',
        'log': ''
    }

    try:
        driver.get("https://tutorial.djangogirls.org/ru/")
        test_result['log'] += "Открыта главная страница.\n"

        time.sleep(2)

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

def auth_view(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            login_form = CustomLoginForm(request, data=request.POST)
            register_form = CustomUserCreationForm()
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('index')
        elif 'register' in request.POST:
            register_form = CustomUserCreationForm(request.POST)
            login_form = CustomLoginForm()
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect('home')
    else:
        login_form = CustomLoginForm()
        register_form = CustomUserCreationForm()

    return render(request, 'auth.html', {
        'login_form': login_form,
        'register_form': register_form
    })