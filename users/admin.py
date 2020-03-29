from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from import_export.admin import ImportExportModelAdmin


class CustomUserAdmin(UserAdmin):
   add_form = CustomUserCreationForm
   form = CustomUserChangeForm
   model = CustomUser
   list_display = ['email', 'username', 'cell_phone' ,'is_staff', ]


#admin.site.register(CustomUser, CustomUserAdmin)
@admin.register(CustomUser)
class ViewAdmin(ImportExportModelAdmin):
   pass

