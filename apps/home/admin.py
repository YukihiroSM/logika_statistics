# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Location, Group, Payment, Report, Issue
from django.contrib import admin


class LocationAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        field = 'territorial_manager'
        super().save_model(request, obj, form, change)
        if change and field in form.changed_data and form.cleaned_data.get(field):
            reports_to_change = Report.objects.filter(
                    location_name=form.cleaned_data.get(
                        "lms_location_name"
                        )
                    ).all()
            for report in reports_to_change:
                report.territorial_manager = form.cleaned_data.get('territorial_manager')
                report.save()


admin.site.register(Location, LocationAdmin)
admin.site.register(Group)
admin.site.register(Payment)
admin.site.register(Report)
admin.site.register(Issue)
