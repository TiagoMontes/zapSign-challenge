from django.test import SimpleTestCase
from core.domain.entities.document import Document


class DocumentEntityTests(SimpleTestCase):
    def test_can_be_signed_with_signers_and_valid_status(self):
        doc = Document(company_id=1, name="Doc 1", signer_ids=[1, 2], status="draft")
        self.assertTrue(doc.can_be_signed())

    def test_cannot_be_signed_without_signers(self):
        doc = Document(company_id=1, name="Doc 1", signer_ids=[], status="draft")
        self.assertFalse(doc.can_be_signed())

