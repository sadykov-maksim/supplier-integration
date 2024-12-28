from django.db import models
from supplier.models import Supplier


# Create your models here.
class Report(models.Model):
    """Price Update Report"""

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    successful_updates = models.PositiveIntegerField(default=0)
    failed_updates = models.PositiveIntegerField(default=0)
    total_products = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Report from {self.created_at.date()} for {self.supplier.name}"


class ReportError(models.Model):
    """Detailed Error Information for Report"""

    report = models.ForeignKey(Report, related_name='errors', on_delete=models.CASCADE)
    product_title = models.CharField(max_length=255)
    error_message = models.TextField()
    occurred_at = models.DateTimeField(auto_now_add=True)  # Время возникновения ошибки

    @classmethod
    def create_report(cls, report, product_title, error_message):
        report.save()
        if not report.pk:
            raise ValueError("The 'report' object must be saved before creating a ReportError.")
        return cls.objects.create(report=report, product_title=product_title, error_message=error_message)


    def __str__(self):
        return f"Error in {self.report.supplier}"