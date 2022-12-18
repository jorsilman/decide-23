from django import template
from django.contrib.auth.models import User

from census.models import Census
from voting.models import Voting

register= template.Library()


@register.simple_tag
def getUsername(census):
    user=User.objects.get(id=census.voter_id).username
    return user

@register.simple_tag
def getName(census):
    voting=Voting.objects.get(id=census.voting_id).name
    return voting