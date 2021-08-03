from django.test import TestCase, Client
from django.urls import reverse


class AboutTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    urls_templates = {
        reverse('about:author'): 'author.html',
        reverse('about:tech'): 'tech.html',
    }

    def setUp(self):
        self.guest_client = Client()

    def test_using_templates_of_pages(self):
        for url, template in AboutTests.urls_templates.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
