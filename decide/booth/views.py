import json
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404

from base import mods
from voting.models import Voting, VotingBinary


# TODO: check permissions and census
class BoothView(TemplateView):
    template_name = 'booth/booth.html'

    def get_context_data(self,voting_id, **kwargs):
        context = super().get_context_data(**kwargs)
        #vid = kwargs.get('voting_id', 0)

        try:
            voting = get_object_or_404(Voting,pk=voting_id)
        
            context['voting'] = json.dumps(voting.toJson())
            
        except:
            raise Http404

        context['KEYBITS'] = settings.KEYBITS

        return context

class BoothBinaryView(TemplateView):
    template_name = 'booth/booth.html'

    def get_context_data(self,voting_id, **kwargs):
        context = super().get_context_data(**kwargs)
        #vid = kwargs.get('voting_id', 0)

        try:
            voting = get_object_or_404(VotingBinary,pk=voting_id)
        
            context['voting'] = json.dumps(voting.toJson())
            
        except:
            raise Http404

        context['KEYBITS'] = settings.KEYBITS

        return context


