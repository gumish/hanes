
"""
TEST LIDE
"""

# from django.test import TestCase
from test_plus.test import TestCase

from .models import Clovek, _get_sorting_slug

# def create_clovek(jmeno, prijmeni, narozen, pohlavi=None):
#     Clovek.objects.create(
#         jmeno=jmeno,
#         prijmeni=prijmeni,
#         narozen=narozen)

class ClovekModelTest(TestCase):
    fixtures = ['fixtures.json']
    # def setUp(self):
    #     create_clovek(u'Martin Hruška 1981')

    def test_get_sorting_slug(self):
        slovo = 'Martin Hruška'
        self.assertEqual(_get_sorting_slug(slovo), 'martin-hruszka')

    def test_testplus_get(self):
        url = self.reverse('lide:clovek_detail', slug='adamek-petr-1993_2')
        self.get(url)
        self.response_200()