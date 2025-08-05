from django.db import models

class DomainRank(models.Model):
    domain_name = models.CharField(max_length=255, unique=True, null=False)
    rank = models.IntegerField(null=False)

    def __str__(self):
        return f"{self.domain_name}: {self.rank}"
