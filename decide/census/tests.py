import random
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Census
from voting.models import Voting
from voting.models import Question
from base import mods
from base.tests import BaseTestCase


class CensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        q = Question(desc='test question')
        q.save()
        v = Voting(name='test voting', question=q,type='V')
        v.save()
        self.census = Census(voting_id=1, voter_id=1, type='V')
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        response = self.client.get('/census/{}/?voter_id={}'.format(1, 2), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 'Invalid voter')

        response = self.client.get('/census/{}/?voter_id={}'.format(1, 1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Valid voter')

    def test_list_voting(self):
        

        self.login()
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)


    def test_add_new_voters(self):
        data = {'voting_id': 2, 'voters': [1,2,3,4]}

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 200)

    
    def test_reuseCensus(self):
        data = {'OldVotingId':1, 'NewVotingId':2}
        response = self.client.post('/census/reuseCensusV2/V/', data, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/census/reuseCensusV2/BV/', data, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/census/reuseCensusV2/SV/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_censusForAll(self):
        data = {'voting_id':1}
        response = self.client.post('/census/censusForAll/V/', data, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/census/censusForAll/BV/', data, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/census/censusForAll/SV/', data, format='json')
        self.assertEqual(response.status_code, 200)     


    def testExportJSON(self):
        response = self.client.get('/census/exportjson/')
        self.assertEqual(response.get('Content-Type'), 'text/json-comment-filtered')
        self.assertEqual(response.get('Content-Disposition'), 'attachment; filename=censo.json')
    def testExportXML(self):
        response = self.client.get('/census/exportxml/')
        self.assertEqual(response.get('Content-Type'), 'text/xml')
        self.assertEqual(response.get('Content-Disposition'), 'attachment; filename=censo.xml')
    """def testExportCSV(self):
        response = self.client.get('/census/exportcsv/')
        self.assertEqual(response.get('Content-Disposition'), 'attachment; filename=censo.csv')"""
        
