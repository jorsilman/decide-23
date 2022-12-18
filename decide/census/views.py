from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
import csv
import xml
from base.perms import UserIsStaff
from .models import Census
from voting.models import Voting, VotingBinary, ScoreVoting
from django.core import serializers
from .forms import NameForm


def first_view(request):
    print('Entro view')
    print(request.method)
    census_list = Census.objects.all()
    if request.method == 'POST':
        print('Entro post')
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        
        if 'exportar' in request.POST:
            print('Hola que tal')
        if 'buscar' in request.POST:
            print('Hola que tal cabron')
        # check whether it's valid:
        
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
        print('Entro is valid')
        #id= form.cleaned_data['q']
        #v= form.cleaned_data['x']
        id= request.POST.get('q','')
        v= request.POST.get('x','')
        print(v)
        print(id)
        if id:
            census_list = Census.objects.all()
                #voter=get_object_or_404(User,id=id)
            like=User.objects.filter(username__contains=id)
            for u in like:
                   census_list = census_list.filter(voter_id=u.id)
        else:
            census_list = Census.objects.all()
        if v:
                
                #voter=get_object_or_404(User,id=id)
            like=Voting.objects.filter(name__contains=v)
            for vo in like:
                census_list = census_list.filter(voting_id=vo.id)
        if 'exportar' in request.POST:
            #type= form.cleaned_data['t']
            print('Emtro exportar')
            type= request.POST.get('t','')
            if type:
                if type == 'CSV':
                    return exportcsvFilter(census_list)
                if type == 'JSON':
                    return exportjsonFilter(census_list)
                if type == 'XML':
                    return exportxmlFiltered(census_list)

        
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
        census_list = Census.objects.all()
    #voting_list=Voting.objects.all()
    #user_list=User.objects.all()
    #t=len(voting_list)
    #t1=len(user_list)
    #user=User.objects.get(id=1).username
    #voting=Voting.objects.get(id=2).name
    context = {'object_list': census_list,'form':form,'action':''}
    return render(request, 'census/census.html',context)
def exportcsv(request):
    #print('entro')
    lista_census = Census.objects.all()
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename=censo.csv'
    writer = csv.writer(response)
    writer.writerow(['VotingID', 'VoterID','Tipo'])
    
    #print(user)
    #print(voting)
    
    #censos = lista_census.values_list('voting_id','voter_id')
    for c in lista_census:
       user=User.objects.get(id=c.voter_id).username
       voting=Voting.objects.get(id=c.voting_id).name
       writer.writerow([voting, user,c.type])
    return response 


def exportcsvFilter(list_filter):
    #print('entro')
    lista_census = list_filter
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename=censo.csv'
    writer = csv.writer(response)
    writer.writerow(['VotingID', 'VoterID','Tipo'])
    
    #print(user)
    #print(voting)
    
    #censos = lista_census.values_list('voting_id','voter_id')
    for c in lista_census:
       user=User.objects.get(id=c.voter_id).username
       voting=Voting.objects.get(id=c.voting_id).name
       writer.writerow([voting, user,c.type])
    return response    

def exportjson(request):
    all_census = Census.objects.all()
    cenus_list = serializers.serialize('json', all_census)
    response = HttpResponse(cenus_list, content_type="text/json-comment-filtered")
    response['Content-Disposition'] = 'attachment; filename=censo.json'
    
    return response
def exportjsonFilter(list_filtered):
    all_census = list_filtered
    cenus_list = serializers.serialize('json', all_census)
    response = HttpResponse(cenus_list, content_type="text/json-comment-filtered")
    response['Content-Disposition'] = 'attachment; filename=censo.json'
    
    return response
def exportxml(request):
    all_census = Census.objects.all()
    cenus_list = serializers.serialize('xml', all_census)
    response=HttpResponse(cenus_list, content_type="text/xml")
    response['Content-Disposition'] = 'attachment; filename=censo.xml'
    return response
def exportxmlFiltered(list_filtered):
    all_census = list_filtered
    cenus_list = serializers.serialize('xml', all_census)
    response=HttpResponse(cenus_list, content_type="text/xml")
    response['Content-Disposition'] = 'attachment; filename=censo.xml'
    return response




from voting.models import Voting, VotingBinary
from base.perms import UserIsStaff
from .models import Census
from django.contrib.auth.models import User

class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (UserIsStaff,)

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        type = request.data.get('type')
        try:
            for voter in voters:

                census = Census(voting_id=voting_id, voter_id=voter, type=type)

                census.save()
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})

def reuseCensusV2(request):
    census = Census.objects.all()
    set_censos=set();
    for censo in census:
        set_censos.add(censo.voting_id)


    votings = Voting.objects.all()
    set_voting=set();
    for v in votings:
        set_voting.add(v)


    if request.method == 'GET':
        return render(request, 'reuseCensus.html', {
        'choice1': set_censos, 'choice2':set_voting
    })
    else:
        oldVotingId = request.POST.get('OldVotingId', False)
        newVotingId = request.POST.get('NewVotingId', False)

        census = Census.objects.filter(voting_id=oldVotingId)
    try:
        for censo in census:
            censo_repe = Census.objects.filter(voting_id=newVotingId,voter_id=censo.voter_id)
            if len(censo_repe) == 0:
                voter = censo.voter_id
                reuseCenso = Census(voting_id=newVotingId, voter_id=voter)
                reuseCenso.save()
    except IntegrityError:
            return HttpResponse('no se ha podido crear el censo')
            
    return render(request, 'indexCensus.html', {'boleano':True})


def indexCensus(request):
    return render(request, 'indexCensus.html')    
    
def reuseCensusV2BV(request):
    census2 = Census.objects.filter(type="BV")
    set_censos_bv=set();
    for censo in census2:
        set_censos_bv.add(censo.voting_id)


    votings = VotingBinary.objects.all()
    set_voting=set();
    for v in votings:
        set_voting.add(v)


    if request.method == 'GET':
        return render(request, 'reuseCensus.html', {
        'choice1': set_censos_bv, 'choice2':set_voting
    })
    else:
        oldVotingId = request.POST.get('OldVotingId', False)
        newVotingId = request.POST.get('NewVotingId', False)

        census = Census.objects.filter(voting_id=oldVotingId, type="BV")
    try:
        for censo in census:
            censo_repe = Census.objects.filter(voting_id=newVotingId,voter_id=censo.voter_id, type="BV")
            if len(censo_repe) == 0:
                voter = censo.voter_id
                reuseCenso = Census(voting_id=newVotingId, voter_id=voter, type="BV")
                reuseCenso.save()
    except IntegrityError:
            return HttpResponse('no se ha podido crear el censo')
    return render(request, 'indexCensus.html', {'boleano':True})        

def reuseCensusV2SV(request):
    census2 = Census.objects.filter(type="SV")
    set_censos_sv=set();
    for censo in census2:
        set_censos_sv.add(censo.voting_id)


    votings = ScoreVoting.objects.all()
    set_voting=set();
    for v in votings:
        set_voting.add(v)


    if request.method == 'GET':
        return render(request, 'reuseCensus.html', {
        'choice1': set_censos_sv, 'choice2':set_voting
    })
    else:
        oldVotingId = request.POST.get('OldVotingId', False)
        newVotingId = request.POST.get('NewVotingId', False)

        census = Census.objects.filter(voting_id=oldVotingId, type="SV")
    try:
        for censo in census:
            censo_repe = Census.objects.filter(voting_id=newVotingId,voter_id=censo.voter_id, type="SV")
            if len(censo_repe) == 0:
                voter = censo.voter_id
                reuseCenso = Census(voting_id=newVotingId, voter_id=voter, type="SV")
                reuseCenso.save()
    except IntegrityError:
            return HttpResponse('no se ha podido crear el censo')
    return render(request, 'indexCensus.html', {'boleano':True}) 

def censusForAll(request):
    voters = User.objects.all()
    votings=Voting.objects.filter(type="V")
    id_repetidas = ""
    set_votaciones = set()
    for voting in votings:
        set_votaciones.add(voting)
    
    
    if request.method=='GET':
        return render(request, './censusForAll.html', {'votaciones':votings, 'choice':set_votaciones})
    else:
        voting_id = request.POST.get('voting_id', False)

    try:
        for voter in voters:
            id = voter.id
            censo_repe=Census.objects.filter(voting_id=voting_id,voter_id=id, type="V")
            if len(censo_repe) == 0:     
                census = Census(voting_id=voting_id, voter_id=id, type="V")
                census.save()
            else: 
                id_repetidas += (str(id)+",")
    except IntegrityError:
            return HttpResponse('no se ha podido crear el censo')
    return render(request, 'indexCensus.html', {'boleano':True}) 

 
def censusForAllBV(request):
    voters = User.objects.all()
    votings=VotingBinary.objects.filter(type="BV")
    id_repetidas = ""
    set_votaciones = set()
    for voting in votings:
        set_votaciones.add(voting)
    
    
    if request.method=='GET':
        return render(request, './censusForAll.html', {'votaciones':votings, 'choice':set_votaciones})
    else:
        voting_id = request.POST.get('voting_id', False)

    try:
        for voter in voters:
            id = voter.id
            censo_repe=Census.objects.filter(voting_id=voting_id,voter_id=id, type="BV")
            if len(censo_repe) == 0:     
                census = Census(voting_id=voting_id, voter_id=id, type="BV")
                census.save()
            else: 
                id_repetidas += (str(id)+",")
    except IntegrityError:
            return HttpResponse('no se ha podido crear el censo')
    return render(request, 'indexCensus.html', {'boleano':True}) 


def censusForAllSV(request):
    voters = User.objects.all()
    votings=ScoreVoting.objects.filter(type="SV")
    id_repetidas = ""
    set_votaciones = set()
    for voting in votings:
        set_votaciones.add(voting)
    
    
    if request.method=='GET':
        return render(request, './censusForAll.html', {'votaciones':votings, 'choice':set_votaciones})
    else:
        voting_id = request.POST.get('voting_id', False)

    try:
        for voter in voters:
            id = voter.id
            censo_repe=Census.objects.filter(voting_id=voting_id,voter_id=id, type="SV")
            if len(censo_repe) == 0:     
                census = Census(voting_id=voting_id, voter_id=id, type="SV")
                census.save()
            else: 
                id_repetidas += (str(id)+",")
    except IntegrityError:
            return HttpResponse('no se ha podido crear el censo')
    return render(request, 'indexCensus.html', {'boleano':True})          
    
def prueba(request):
    census = Census.objects.filter(type="V")
    census2 = Census.objects.filter(type="BV")
    set_censos_v=set();
    set_censos_bv=set();
    for censo in census2:
        set_censos_bv.add(censo.voting_id)
    for censo in census:
        set_censos_v.add(censo.voting_id)
    return render(request, './prueba.html', {'voting':set_censos_v, 'binary':set_censos_bv})



class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        type= request.data.get('type')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters, type=type)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')
