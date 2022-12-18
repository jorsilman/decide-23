import itertools
from pyexpat import model
import random
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


from base import mods

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from mixnet.models import Auth
from django.conf import settings
from django.contrib.auth.models import User
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt

from django.utils import timezone

from base.tests import BaseTestCase
from voting.models import Question, QuestionBinary, QuestionOptionBinary, Voting, ScoreQuestionOption, QuestionOption, VotingBinary, ScoreQuestion, ScoreVoting



class VisualizerTestCase(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()
        
       

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()    

        #self.create_voting()        
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)
    
    def create_voters(self, v):
        for i in range(101, 200):
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
        voters = list(Census.objects.filter(voting_id=v.id, type=v.type))
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
                self.base.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

   

    def complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.base.login()  # set token
        v.tally_votes(self.base.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        return v

    #Crea votacion binaria

    def create_votingB(self):
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

    

    def complete_votingB(self):
        v = self.create_votingB()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.base.login()  # set token
        v.tally_votes(self.base.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        return v
    
    #Crea votacion score

    def create_votingS(self):
        q = ScoreQuestion(desc='test score question')
        q.save()
        opt1 = ScoreQuestionOption(question=q, option=True)
        opt1.save()
        opt2 = ScoreQuestionOption(question=q, option=False)
        opt2.save()

        v = ScoreVoting(name='test score voting', question=q,type='SV')
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def complete_votingS(self):
        v = self.create_votingS()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.base.login()  # set token
        v.tally_votes(self.base.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        return v
    
    def test_simpleVisualizerNoComenzada(self):        
        q = Question(desc='test question')
        q.save()
        v = Voting(name='test voting', question=q)
        v.save()
        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState, "Votación no comenzada")
    
    def test_simpleVisualizerEnCurso(self):
        q = Question(desc='test question')
        q.save()
        v = Voting(name='test voting', question=q)
        v.start_date = timezone.now()
        v.save()
       
        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState, "Votación en curso")
    
    def test_simpleVisualizerCorrect(self):
        v = self.complete_voting()
        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState, "Resultados:")

    """def test_simpleVisualizerNoComenzadaBinary(self):        
        q = QuestionBinary(desc='test question')
        q.save()
        v = VotingBinary(name='test binary voting', question=q,type='BV')
        v.save()
        response =self.driver.get(f'{self.live_server_url}/visualizer/binaryVoting/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState, "Votación no comenzada")
    
    def test_simpleVisualizerEnCursoBinary(self):
        q = QuestionBinary(desc='test question')
        q.save()
        v = VotingBinary(name='test binary voting', question=q,type='BV')
        v.start_date = timezone.now()
        v.save()
       
        response =self.driver.get(f'{self.live_server_url}/visualizer/binaryVoting/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState, "Votación en curso")"""

    def test_simpleVisualizerCorrectBinary(self):
        v = self.complete_votingB()
        response =self.driver.get(f'{self.live_server_url}/visualizer/binaryVoting/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState, "Resultados:")
    
    def test_simpleVisualizerCorrectScore(self):
        v = self.complete_votingS()
        response =self.driver.get(f'{self.live_server_url}/visualizer/scoreVoting/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState, "Resultados:")

    
    