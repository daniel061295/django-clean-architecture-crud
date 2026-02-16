from django.test import TestCase, RequestFactory
from rest_framework import status
from rest_framework.exceptions import APIException
from core.exceptions import drf_exception_handler
from store.domain.exceptions import DomainError, PlantItemNotFoundError

class ExceptionHandlerTestCase(TestCase):
    def test_domain_error_handling(self):
        exc = DomainError("Domain logic failed")
        context = {} # Context can be mocked if needed
        
        response = drf_exception_handler(exc, context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Domain logic failed")

    def test_not_found_error_handling(self):
        exc = PlantItemNotFoundError("Item not found")
        context = {}
        
        response = drf_exception_handler(exc, context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Item not found")

    def test_standard_drf_exception(self):
        # Ensure standard exceptions are still handled by DRF default handler if passed through
        # Note: drf_exception_handler calls exception_handler internally.
        # We can test that it returns None for unhandled exceptions or handles DRF ones.
        pass
