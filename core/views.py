
import os
import subprocess

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect

from .models import TestRun


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
            with open(filepath, 'w') as f:
                f.write(code)

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
