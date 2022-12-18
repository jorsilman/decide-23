from django import forms

TYPES = [('CSV','CSV'), ('JSON','JSON'), ('XML','XML')]
class NameForm(forms.Form):
    q = forms.CharField(required=False,label='Votante', max_length=100)
    x = forms.CharField(required=False,label='Votación', max_length=100)
    t = forms.ChoiceField(required=False,label=' Exportar a',choices=TYPES,widget=forms.RadioSelect)

   
    

    
