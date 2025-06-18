from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Пользователь
class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username

# 2. Тест
class Test(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')

    def __str__(self):
        return self.name

# 3. Тест-кейс
class TestCase(models.Model):
    code_snippet = models.TextField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='cases')

    def __str__(self):
        return f"Кейс для {self.test.name}"

# 4. Результат теста
class TestResult(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('fail', 'Провалено'),
    ]

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    run_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    report_path = models.TextField()

    def __str__(self):
        return f"Результат {self.test.name} от {self.user.username}"
