from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Company(TimeStampedModel):
    name = models.CharField(max_length=255)
    api_token = models.CharField(max_length=255)
    objects = models.Manager()

    def __str__(self) -> str:
        return str(self.name)


class Signer(models.Model):
    token = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=50, blank=True, default="")
    name = models.CharField(max_length=255)
    email = models.EmailField()
    external_id = models.CharField(max_length=255, blank=True, default="")
    objects = models.Manager()

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"


class Document(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="documents")
    open_id = models.IntegerField(null=True, blank=True)
    token = models.CharField(max_length=255, blank=True, default="")
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, blank=True, default="")
    created_by = models.CharField(max_length=150, blank=True, default="")
    external_id = models.CharField(max_length=255, blank=True, default="")

    # Associação: 1 documento -> * signatários (M2)
    signers = models.ManyToManyField(Signer, blank=True, related_name="documents")
    objects = models.Manager()

    def __str__(self) -> str:
        return str(self.name)

