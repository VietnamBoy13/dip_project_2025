from django.contrib import admin
from .models import User, Test, TestCase, TestResult
from django.contrib.auth.admin import UserAdmin

admin.site.register(User, UserAdmin)
admin.site.register(Test)
admin.site.register(TestCase)
admin.site.register(TestResult)
