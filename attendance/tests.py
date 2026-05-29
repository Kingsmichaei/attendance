from django.test import TestCase
from django.urls import reverse


class AttendanceSmokeTests(TestCase):
	def test_home_page_loads(self):
		response = self.client.get(reverse('attendance:home'))
		self.assertEqual(response.status_code, 200)
