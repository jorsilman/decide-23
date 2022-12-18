from django.db import models
from base.models import BigBigField


class Vote(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()
    votingTypes = (('V', 'Voting'), ('BV', 'BinaryVoting'),('SV', 'ScoreVoting'))
    type = models.CharField(max_length=2, choices=votingTypes, default='V')


    a = BigBigField()
    b = BigBigField()

    voted = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return '{}: {}'.format(self.voting_id, self.voter_id,self.type)
