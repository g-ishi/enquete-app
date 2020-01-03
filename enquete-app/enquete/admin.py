from django.contrib import admin

from . import models

admin.site.register(models.Enquete)
admin.site.register(models.Question)
admin.site.register(models.Choice)
admin.site.register(models.Member)
admin.site.register(models.EQ)
admin.site.register(models.QC)
admin.site.register(models.QM)
