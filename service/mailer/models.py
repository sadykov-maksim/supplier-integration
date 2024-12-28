from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.template import Context, Template
from django.template.loader import render_to_string


# Create your models here.
class EmailTemplate(models.Model):
    """
    Модель для хранения шаблонов электронных писем.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Template Name"),
        help_text=_("Unique name for the email template.")
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_("Subject"),
        help_text=_("Subject of the email.")
    )
    body = models.TextField(
        verbose_name=_("Body"),
        help_text=_("HTML content of the email.")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def render_body(self, context):
        """
        Renders the body of the email with the context data.
        """
        template = Template(self.body)
        context = Context(context)
        return template.render(context)

    class Meta:
        verbose_name = _("Email Template")
        verbose_name_plural = _("Email Templates")

    def __str__(self):
        return self.name


class Email(models.Model):
    """
    Модель для хранения информации о письмах, готовых к отправке или уже отправленных.
    """
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("sent", _("Sent")),
        ("failed", _("Failed")),
    ]

    to_email = models.EmailField(
        verbose_name=_("Recipient"),
        help_text=_("Recipient's email address.")
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_("Subject"),
        help_text=_("Subject of the email.")
    )
    body = models.TextField(
        verbose_name=_("Body"),
        help_text=_("HTML content of the email.")
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
        help_text=_("Status of the email.")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Sent At"),
        help_text=_("Timestamp of when the email was sent.")
    )

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")

    def __str__(self):
        return f"{self.subject} -> {self.to_email}"

class EmailUser(models.Model):
    """
    Модель для хранения информации о пользователе, включая имя, фамилию и email.
    """
    first_name = models.CharField(
        max_length=100,
        verbose_name=_("First Name"),
        help_text=_("User's first name.")
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_("Last Name"),
        help_text=_("User's last name.")
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_("Email"),
        help_text=_("User's email address.")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

class ScheduledEmail(models.Model):
    """
    Модель для хранения запланированных писем.
    """
    email_template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.CASCADE,
        verbose_name=_("Email Template"),
        help_text=_("Template to use for the scheduled email.")
    )
    user_profile = models.ForeignKey(
        EmailUser,
        on_delete=models.CASCADE,
        verbose_name=_("User Profile"),
        help_text=_("User profile associated with the email.")
    )
    scheduled_time = models.DateTimeField(
        verbose_name=_("Scheduled Time"),
        help_text=_("Time when the email should be sent.")
    )
    is_sent = models.BooleanField(
        default=False,
        verbose_name=_("Is Sent"),
        help_text=_("Whether the email has been sent.")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Scheduled Email")
        verbose_name_plural = _("Scheduled Emails")

    def __str__(self):
        return f"{self.email_template.name} -> {self.user_profile.email}"