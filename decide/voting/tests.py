import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import QuestionBinary, QuestionOptionBinary, Voting, Question, QuestionOption, VotingBinary, ScoreQuestion, ScoreQuestionOption, ScoreVoting


class VotingTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q,type='V')
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id,type =v.type)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id,type=v.type))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'type': v.type,
                    'vote': { 'a': a, 'b': b },
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])
    
    def test_create_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)
    
        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)
    
        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Example',
            'desc': 'Description example',
            'question': 'I want a ',
            'question_opt': ['cat', 'dog', 'horse'],
            'type':'V'
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}
        response = self.client.post('/voting/?id={}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.post('/voting/?id={}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)
        
        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.post('/voting/?id={}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
       

##TEST VOTACIÓN SI O NO


class BinaryVotingTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = QuestionBinary(desc='test binary question')
        q.save()
        opt1 = QuestionOptionBinary(question=q, option=True)
        opt1.save()
        opt2 = QuestionOptionBinary(question=q, option=False)
        opt2.save()

        v = VotingBinary(name='test binary voting', question=q,type='BV')
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id, type=v.type)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id, type='BV'))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 2)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                    'type': v.type,
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])
    
    def test_create_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/votingbinary/', data, format='json')
        self.assertEqual(response.status_code, 401)
    
        # login with user no admin
        self.login(user='noadmin')
        response = self.client.post('/voting/votingbinary/', data, format='json')
        self.assertEqual(response.status_code, 403)
    
        # login with user admin
        self.login()
        response = self.client.post('/voting/votingbinary/', data, format='json')
        self.assertEqual(response.status_code, 400)
        
        data = {
            'name': 'Example',
            'desc': 'Description example',
            'question': 'Michael Jordan is the best basketball player ',
            'question_opt': ['True', 'False'],
            'type':'BV',
        }

        response = self.client.post('/voting/votingbinary/', data, format='json')
        self.assertEqual(response.status_code, 201)
    
    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}
        response = self.client.post('/voting/votingbinary/?id={}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 401)
    
        # login with user no admin
        self.login(user='noadmin')
        response = self.client.post('/voting/votingbinary/?id={}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.post('/voting/votingbinary/?id={}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)



    
##TEST SCOREVOTING


class ScoreVotingTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
    
    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = ScoreQuestion(desc='test score question')
        q.save()
        opt1 = ScoreQuestionOption(question=q, option=20)
        opt1.save()
        opt2 = ScoreQuestionOption(question=q, option=24)
        opt2.save()

        v = ScoreVoting(name='test score voting', question=q,type='SV')
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id, type=v.type)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id, type='SV'))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 2)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                    'type': v.type,
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])


    def test_create_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/scoreVoting/?id={}', data, format='json')
        self.assertEqual(response.status_code, 401)
    
        # login with user no admin
        self.login(user='noadmin')
        response = self.client.post('/voting/scoreVoting/?id={}', data, format='json')
        self.assertEqual(response.status_code, 403)
    
        # login with user admin
        self.login()
        response = self.client.post('/voting/scoreVoting/?id={}', data, format='json')
        self.assertEqual(response.status_code, 400)
        
        data = {
            'name': 'Example',
            'desc': 'Description example',
            'question': 'Número de Champions ganadas por el Betis ',
            'question_opt': ["0", "1", "13"],
            'type':'SV',
        }

        response = self.client.post('/voting/scoreVoting/?id={}', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}
        response = self.client.post('/voting/scoreVoting/?id={}'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 401)
    
        # login with user no admin
        self.login(user='noadmin')
        response = self.client.post('/voting/scoreVoting/?id={}'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.post('/voting/scoreVoting/?id={}'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
