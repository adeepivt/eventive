from django.contrib import admin
from .models import Profile
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib import messages
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'get_username', # Custom method to display username for sorting/linking
        'user_type',
        'approval_status',
        'is_user_active', # Custom method to show User's active status
    )
    list_filter = (
        'user_type',
        'approval_status',
    )
    search_fields = (
        'user__username', # Search by username of the related User
        'mobile',
    )
    ordering = ('-user__date_joined',) # Show newest registrations first, for example

    # Define custom actions for approving and rejecting
    actions = ['approve_selected_profiles', 'reject_selected_profiles']

    # Custom methods for list_display
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username' # Column header in admin
    get_username.admin_order_field = 'user__username' # Allows sorting by username

    def is_user_active(self, obj):
        return obj.user.is_active
    is_user_active.short_description = 'User Active?' # Column header
    is_user_active.boolean = True # Displays as a True/False icon
    is_user_active.admin_order_field = 'user__is_active'


    def approve_selected_profiles(self, request, queryset):
        updated_count = 0
        for profile in queryset:
            # Ensure we are only approving pending vendors
            if profile.user_type == 'vendor' and profile.approval_status == 'pending':
                profile.approval_status = 'approved'
                profile.user.is_active = True
                profile.save()
                profile.user.save() 
                updated_count += 1

                try:
                    print(f"Sending approval email to {profile.user.username} at {profile.user.email}")
                    email_message = EmailMessage(
                        f'Your Vendor Account on Eventive has been Approved!',
                        f'Hello {profile.user.username},\n\nCongratulations! Your vendor account has been approved. '
                        f'You can now log in and access vendor features.\n\n'
                        f'Login here: {request.build_absolute_uri("/users/vendor/login")}',
                        settings.EMAIL_HOST_USER,
                        [profile.user.email],
                    )
                    email_message.fail_silently = True
                    email_message.send()
                except Exception as e:
                    self.message_user(request, f"Error sending approval email to {profile.user.username}: {e}", messages.ERROR)

        if updated_count > 0:
            self.message_user(request, f"{updated_count} vendor profile(s) successfully approved and user accounts activated.")
        else:
            self.message_user(request, "No pending vendor profiles were selected or eligible for approval.", level='WARNING')
    approve_selected_profiles.short_description = "Approve selected vendor profiles" # Action description in dropdow

    def reject_selected_profiles(self, request, queryset):
        updated_count = 0
        for profile in queryset:
            # Ensure we are only rejecting pending or already approved vendors (if re-evaluation is needed)
            if profile.user_type == 'vendor' and profile.approval_status in ['pending', 'approved']:
                profile.approval_status = 'rejected'
                profile.user.is_active = False # Ensure User account is inactive
                profile.save()
                profile.user.save()
                updated_count += 1

                # try:
                #     send_mail(
                #         subject=f'Update on Your Vendor Account on {settings.SITE_NAME}',
                #         message=f'Hello {profile.user.username},\n\nWe regret to inform you that your vendor application has been rejected at this time. '
                #                 f'If you have questions, please contact support at {settings.SUPPORT_EMAIL}.\n\n' # Add your support email
                #                 # You might want to give a reason if you have a system for that
                #         from_email=settings.DEFAULT_FROM_EMAIL,
                #         recipient_list=[profile.user.email],
                #         fail_silently=False,
                #     )
                # except Exception as e:
                #     self.message_user(request, f"Error sending rejection email to {profile.user.username}: {e}", messages.ERROR)

        if updated_count > 0:
            self.message_user(request, f"{updated_count} vendor profile(s) successfully rejected.")
        else:
            self.message_user(request, "No vendor profiles were selected or eligible for rejection.", level='WARNING')
    reject_selected_profiles.short_description = "Reject selected vendor profiles"