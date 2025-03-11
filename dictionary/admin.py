from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from .models import Word, Paribhasha

class CustomParibhashaInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        # Store the current request on the formset for later use.
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def add_fields(self, form, index):
        """
        Called for each form; disable the 'description' field if the parent Word is reviewed
        and the current user is not a superuser.
        """
        super().add_fields(form, index)
        if self.instance and self.instance.reviewed and self.request and not self.request.user.is_superuser:
            form.fields['description'].disabled = True

class ParibhashaInline(admin.TabularInline):
    model = Paribhasha
    extra = 1
    min_num = 1
    max_num = 10
    fields = ['description']

    def get_formset(self, request, obj=None, **kwargs):
        # Get the base formset class from the superclass.
        Formset = super().get_formset(request, obj, **kwargs)
        # Return a subclass that uses our custom formset,
        # passing in the request so that we can use it in add_fields().
        class CustomFormset(Formset, CustomParibhashaInlineFormSet):
            def __init__(self, *args, **kwargs):
                # Inject the request into the formset.
                kwargs['request'] = request
                super().__init__(*args, **kwargs)
        return CustomFormset

    def has_delete_permission(self, request, obj=None):
        """
        Prevent non-superusers from deleting inline descriptions when the parent Word is reviewed.
        """
        # If obj is not a Paribhasha instance, defer to the default behavior.
        if not isinstance(obj, Paribhasha):
            return super().has_delete_permission(request, obj)
        if obj.word and obj.word.reviewed and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

class WordAdmin(admin.ModelAdmin):
    list_display = ('hindi', 'hinglish', 'pageno', 'reviewed', 'review_by')
    search_fields = ('hindi', 'hinglish')
    list_filter = ('pageno', 'reviewed')
    inlines = [ParibhashaInline]
    readonly_fields = ('review_by',)
    ordering = ('hindi',)

    def get_readonly_fields(self, request, obj=None):
        """
        If the Word is reviewed and the user is not a superuser, make all fields read-only.
        """
        if obj and obj.reviewed and not request.user.is_superuser:
            return [field.name for field in self.model._meta.fields]
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.reviewed and obj.review_by is None:
            obj.review_by = request.user
        obj.save()

admin.site.register(Word, WordAdmin)

admin.site.site_header = "Paribhasha Administrator"
admin.site.site_title = "Paribhasha Admin Panel"
admin.site.index_title = "Welcome to Paribhasha Administrator"
