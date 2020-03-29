from django.contrib import admin
from. models import Board, Topic, Post
from import_export.admin import ImportExportModelAdmin
# Register your models here.

#admin.site.register(Post)
#admin.site.register(Board)
#admin.site.register(Topic)
@admin.register(Post)
class ViewAdmin(ImportExportModelAdmin):
    pass

@admin.register(Board)
class ViewAdmin(ImportExportModelAdmin):
    pass

@admin.register(Topic)
class ViewAdmin(ImportExportModelAdmin):
    pass


