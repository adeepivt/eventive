from django.contrib import admin
from .models import Booking, Event, Facility, EventGallery
from django.utils.html import format_html
# Register your models here.
admin.site.register(Booking)
admin.site.register(Event)

# For Approach 1: Facility Model
@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['name']
    list_editable = ['is_active']

class EventGalleryInline(admin.TabularInline):
    model = EventGallery
    extra = 1
    fields = ['image', 'title', 'description', 'is_featured', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"

@admin.register(EventGallery)
class EventGalleryAdmin(admin.ModelAdmin):
    list_display = ['event', 'title', 'is_featured', 'order', 'uploaded_at', 'image_preview']
    list_filter = ['is_featured', 'uploaded_at', 'event__category']
    search_fields = ['event__name', 'title', 'description']
    list_editable = ['is_featured', 'order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"