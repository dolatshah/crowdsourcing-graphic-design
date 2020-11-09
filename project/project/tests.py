"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from project.models import Project

class SimpleTest(TestCase):
	def is_running_is_finished(self):
		is_wrong=False
		for project in Project:
			if project.is_running and project.is_finished:
				is_wrong=True
		self.assertEqual(is_wrong,False)
		
	def is_running_choosedOffer_id(self):
		is_wrong=False
		for project in Project:
			if project.is_running and not project.choosedOffer_id:
				is_wrong=True
		self.assertEqual(is_wrong,False)
	
	def endDate_bigger_startDate(self):
		is_wrong=False
		for project in Project:
			seconds=project.endDate-project.startDate
			seconds=seconds.total_seconds()
			if seconds < 0:
				is_wrong=True
		self.assertEqual(is_wrong,False)
		
	def is_runnig_employee(self):
		is_wrong=False
		for project in Project:
			if project.is_running and not project.employee:
				is_wrong=True
		
		self.assertEqual(is_wrong,False)