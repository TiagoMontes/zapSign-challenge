from django.urls import reverse
from rest_framework.test import APITestCase


class ApiEndpointsTests(APITestCase):
    def test_companies_crud(self):
        # create
        resp = self.client.post("/api/companies/", {"name": "Acme"}, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        company_id = resp.data["id"]

        # list
        resp = self.client.get("/api/companies/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(item["id"] == company_id for item in resp.data))

    def test_documents_with_signers_flow(self):
        # company
        c = self.client.post("/api/companies/", {"name": "Beta"}, format="json").data
        # signer
        s = self.client.post(
            "/api/signers/", {"name": "Alice", "email": "alice@example.com"}, format="json"
        ).data
        # document with signer
        resp = self.client.post(
            "/api/documents/",
            {"company": c["id"], "name": "Contract", "signers": [s["id"]]},
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        # list documents
        resp = self.client.get("/api/documents/")
        self.assertEqual(resp.status_code, 200)
