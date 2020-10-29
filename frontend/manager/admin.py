from django.contrib import admin
from .models import Account,Token
# Register your models here.
admin.site.register(Account)
admin.site.register(Token)