from django.contrib import admin
from .models import Paribhasha, ParibhashaLine



class ParibhashaLineInline(admin.TabularInline):  # This creates a related form
    model = ParibhashaLine
    extra = 1  # Show one blank line by default
    min_num = 1  # Minimum 1 line required
    max_num = 10  # Maximum 50 lines per Paribhasha
    fields = ['name']  # Only show the name field


class ParibhashaAdmin(admin.ModelAdmin):
    list_display = ('hindi', 'hinglish', 'pageno')
    search_fields = ('hindi', 'hinglish')
    list_filter = ('pageno',)
    inlines = [ParibhashaLineInline]  # Attach the inline form here


# Register the models
admin.site.register(Paribhasha, ParibhashaAdmin)


# ✅ Change the admin panel title and header
admin.site.site_header = "Paribhasha Administrator"
admin.site.site_title = "Paribhasha Admin Panel"
admin.site.index_title = "Welcome to Paribhasha Administrator"
