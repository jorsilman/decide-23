import json
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404

from voting.models import ScoreVoting, VotingBinary

from base import mods

from django.views.generic.base import View




class VisualizerView(TemplateView):
    template_name = 'visualizer/visualizer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            context['voting'] = json.dumps(r[0])
        except:
            raise Http404

        return context

    
class VisualizerViewBinary(TemplateView):
    template_name = 'visualizer/visualizer1.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            voting = get_object_or_404(VotingBinary,pk=vid)
            context['voting'] = json.dumps(VotingBinary.toJson(voting))
        except:
            raise Http404

        return context

class VisualizerViewScore(TemplateView):
    template_name = 'visualizer/visualizer2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            voting = get_object_or_404(ScoreVoting,pk=vid)
            context['voting'] = json.dumps(VotingBinary.toJson(voting))
        except:
            raise Http404

        return context


        