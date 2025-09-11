from typing import Any, cast

from rest_framework.test import APITestCase
from rest_framework.response import Response


class ApiEndpointsTests(APITestCase):
    def test_companies_crud(self):
        # create
        resp = cast(
            Response, self.client.post("/api/companies/", {"name": "Acme"}, format="json")
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        company_data = cast(dict[str, Any], resp.data)
        company_id = cast(int, company_data["id"])

        # list
        resp = cast(Response, self.client.get("/api/companies/"))
        self.assertEqual(resp.status_code, 200)
        items = cast(list[dict[str, Any]], resp.data)
        self.assertTrue(any(item["id"] == company_id for item in items))

    def test_documents_with_signers_flow(self):
        # company
        resp = cast(Response, self.client.post("/api/companies/", {"name": "Beta"}, format="json"))
        c = cast(dict[str, Any], resp.data)
        # signer
        resp = cast(
            Response,
            self.client.post(
                "/api/signers/", {"name": "Alice", "email": "alice@example.com"}, format="json"
            ),
        )
        s = cast(dict[str, Any], resp.data)
        # document with signer
        resp = cast(
            Response,
            self.client.post(
                "/api/documents/",
                {"company": c["id"], "name": "Contract", "signers": [s["id"]]},
                format="json",
            ),
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        # list documents
        resp = cast(Response, self.client.get("/api/documents/"))
        self.assertEqual(resp.status_code, 200)

