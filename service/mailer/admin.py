from django.contrib import admin
from django.core.mail import send_mail



from .models import *

# Register your models here.
@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'created_at', 'updated_at')
    search_fields = ('name', 'subject')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('to_email', 'subject', 'status', 'created_at', 'sent_at')
    search_fields = ('to_email', 'subject')
    list_filter = ('status', 'created_at', 'sent_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'sent_at')

@admin.register(ScheduledEmail)
class ScheduledEmailAdmin(admin.ModelAdmin):
    list_display = ('email_template', 'user_profile', 'scheduled_time', 'is_sent', 'created_at')
    search_fields = ('user_profile__email', 'email_template__name')
    list_filter = ('is_sent', 'scheduled_time', 'created_at')
    ordering = ('-scheduled_time',)
    readonly_fields = ('created_at',)
    actions = ('send_selected_emails',)

    @admin.action(description="Отправить выбранные письма")
    def send_selected_emails(self, request, queryset):
        for email in queryset.filter(is_sent=False, scheduled_time__lte=now()):
            try:
                email_template = EmailTemplate.objects.get(name="welcome_email")

                # Извлекаем имя и фамилию пользователя
                user_profile = EmailUser.objects.filter(email=email.user_profile.email).first()

                # Подготовка контекста для подстановки в шаблон
                context_data = {
                    'first_name': user_profile.first_name,
                    'last_name': user_profile.last_name,
                }

                # Рендерим тело письма с подставленным именем и фамилией
                email_body = email_template.render_body(context_data)
                print(email_body)

                # Отправляем письмо
                send_mail(
                    subject=email.email_template.subject,
                    message=email.email_template.body,
                    from_email="sadykov-maksim-2003@yandex.ru",
                    recipient_list=[user_profile.email],
                    fail_silently=False,
                    html_message=email_body
                )
                email.is_sent = True
                email.save()
            except Exception as e:
                self.message_user(request, f"Ошибка: {e}", level="error")


@admin.register(EmailUser)
class EmailUserAdmin(admin.ModelAdmin):
    """
    Админка для модели EmailUser.
    """
    list_display = ('first_name', 'last_name', 'email', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    # Если нужно редактировать все поля на одной странице:
    fields = ('first_name', 'last_name', 'email', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    # Добавляем дополнительные возможности для пользователя:
    def save_model(self, request, obj, form, change):
        # Вы можете добавить кастомную логику сохранения, например:
        if not obj.id:
            # Логика для нового пользователя
            pass
        super().save_model(request, obj, form, change)

    # Настройка отображения для списка пользователей:
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')