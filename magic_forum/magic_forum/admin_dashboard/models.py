from django.db import models


class AdminDashboard(models.Model):
    total_pending_posts = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Admin Dashboard"
