from django.contrib import admin
from .models import Booking, Event, Facility, EventGallery
from django.utils.html import format_html
# Register your models here.
admin.site.register(Booking)
admin.site.register(Event)
admin.site.register(EventGallery)

# For Approach 1: Facility Model
@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['name']
    list_editable = ['is_active']

# class EventGalleryInline(admin.TabularInline):
#     model = EventGallery
#     extra = 1
#     fields = ['image', 'title', 'description', 'is_featured', 'order', 'image_preview']
#     readonly_fields = ['image_preview']
    
#     def image_preview(self, obj):
#         if obj.image:
#             try:
#                 image_url = obj.image.url
#                 return format_html(
#                     '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 4px;" />',
#                     image_url
#                 )
#             except Exception as e:
#                 # Log the error for debugging
#                 print(f"Error getting image URL in admin preview: {e}")
#                 return format_html(
#                     '<div style="width: 100px; height: 100px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-size: 12px; text-align: center;">Image Error</div>'
#                 )
#         return format_html(
#             '<div style="width: 100px; height: 100px; background: #f8f8f8; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-size: 12px; text-align: center;">No Image</div>'
#         )
#     image_preview.short_description = "Preview"

# class EventGalleryAdmin(admin.ModelAdmin):
    # list_display = ['event', 'title', 'is_featured', 'order', 'uploaded_at', 'image_preview']
    # list_filter = ['is_featured', 'uploaded_at', 'event__category']
    # search_fields = ['event__name', 'title', 'description']
    # list_editable = ['is_featured', 'order']
    
    # def image_preview(self, obj):
    #     """Safe image preview for list view"""
    #     if obj and obj.image:
    #         try:
    #             image_url = obj.image.url
    #             return format_html(
    #                 '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 3px;" />',
    #                 image_url
    #             )
    #         except Exception as e:
    #             print(f"Error getting image URL in admin list: {e}")
    #             return format_html(
    #                 '<div style="width: 50px; height: 50px; background: #e0e0e0; display: flex; align-items: center; justify-content: center; border-radius: 3px; font-size: 10px;">Error</div>'
    #             )
    #     return format_html(
    #         '<div style="width: 50px; height: 50px; background: #f5f5f5; display: flex; align-items: center; justify-content: center; border-radius: 3px; font-size: 10px;">None</div>'
    #     )
    # image_preview.short_description = "Preview"

    # def get_queryset(self, request):
    #     """Optimize queryset to avoid N+1 queries"""
        # return super().get_queryset(request).select_related('event')