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


class Signer(TimeStampedModel):
    token = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=50, blank=True, default="")
    name = models.CharField(max_length=255)
    email = models.EmailField()
    external_id = models.CharField(max_length=255, blank=True, default="")
    sign_url = models.URLField(blank=True, default="")
    # ZapSign sync fields
    times_viewed = models.IntegerField(null=True, blank=True)
    last_view_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
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

    # PDF processing fields
    url_pdf = models.URLField(null=True, blank=True)
    processing_status = models.CharField(
        max_length=20,
        default="UPLOADED",
        choices=[
            ("UPLOADED", "Uploaded"),
            ("PROCESSING", "Processing"),
            ("INDEXED", "Indexed"),
            ("FAILED", "Failed"),
        ],
        db_index=True
    )
    checksum = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    version_id = models.CharField(max_length=36, null=True, blank=True)

    # Soft delete fields
    is_deleted = models.BooleanField(default=False, db_index=True)  # type: ignore[arg-type]
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.CharField(max_length=150, blank=True, default="")

    # Associação: 1 documento -> * signatários (M2)
    signers = models.ManyToManyField(Signer, blank=True, related_name="documents")
    objects = models.Manager()

    def __str__(self) -> str:
        return str(self.name)


class DocumentAnalysis(models.Model):
    """ORM model for document analysis results."""

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="analyses"
    )
    missing_topics = models.JSONField(default=list, blank=True)
    summary = models.TextField(blank=True, default="")
    insights = models.JSONField(default=list, blank=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['document', '-analyzed_at']),
        ]

    def __str__(self) -> str:
        return f"Analysis of {self.document.name} at {self.analyzed_at}"

