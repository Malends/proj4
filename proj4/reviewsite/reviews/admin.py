from django.contrib import admin
from .models import Doctor, Speciality, Review, Forbidden, Excepted


class ReviewForm(admin.ModelAdmin):
    search_fields = ['doctor', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'raw_review']
    list_display = ('doctor', 'created_at', 'raw_review', 'edited_review', 'ip_address', 'user')
    autocomplete_fields = ['doctor']


class DoctorForm(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'second_name', 'speciality__name']


class SpecialityForm(admin.ModelAdmin):
    search_fields = ['name']


class ForbiddenForm(admin.ModelAdmin):
    search_fields = ['word']


class ExceptedForm(admin.ModelAdmin):
    search_fields = ['word']


admin.site.register(Doctor, DoctorForm)
admin.site.register(Speciality, SpecialityForm)
admin.site.register(Review, ReviewForm)
admin.site.register(Forbidden, ForbiddenForm)
admin.site.register(Excepted, ExceptedForm)
