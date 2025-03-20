from django.contrib import admin
from .models import User, Slambooks, Url_slambook, Questions

admin.site.register(Slambooks)
admin.site.register(User)
admin.site.register(Url_slambook)
admin.site.register(Questions)