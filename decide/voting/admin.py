from django.contrib import admin
from django.utils import timezone


from .models import QuestionOption, ScoreQuestionOption
from .models import Question, ScoreQuestion
from .models import Voting, ScoreVoting

from .models import QuestionBinary, QuestionOption, QuestionOptionBinary, VotingBinary
from .models import Question
from .models import Voting


from .filters import StartedFilter


def start(modeladmin, request, queryset):
    for v in queryset.all():
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()


def stop(ModelAdmin, request, queryset):
    for v in queryset.all():
        v.end_date = timezone.now()
        v.save()


def tally(ModelAdmin, request, queryset):
    for v in queryset.filter(end_date__lt=timezone.now()):
        token = request.session.get('auth-token', '')
        v.tally_votes(token)


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption

class ScoreQuestionOptionInline(admin.TabularInline):
    model = ScoreQuestionOption

class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]

class ScoreQuestionAdmin(admin.ModelAdmin):
    inlines = [ScoreQuestionOptionInline]


class VotingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    readonly_fields = ('start_date', 'end_date', 'pub_key','tally', 'postproc')
    date_hierarchy = 'start_date'
    list_filter = (StartedFilter,)
    search_fields = ('name', )

    actions = [ start, stop, tally ]

class QuestionOptionBinaryInline(admin.TabularInline):
    model = QuestionOptionBinary


class QuestionBinaryAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionBinaryInline]


class VotingBinaryAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    readonly_fields = ('start_date', 'end_date', 'pub_key','tally', 'postproc')
    date_hierarchy = 'start_date'
    list_filter = (StartedFilter,)
    search_fields = ('name', )

    actions = [ start, stop, tally ]

class ScoreVotingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    readonly_fields = ('start_date', 'end_date', 'pub_key',
                       'tally', 'postproc')
    date_hierarchy = 'start_date'
    list_filter = (StartedFilter,)
    search_fields = ('name', )

    actions = [ start, stop, tally ]


admin.site.register(Voting, VotingAdmin)
admin.site.register(Question, QuestionAdmin)

admin.site.register(ScoreVoting, ScoreVotingAdmin)
admin.site.register(ScoreQuestion, ScoreQuestionAdmin)

admin.site.register(VotingBinary, VotingBinaryAdmin)
admin.site.register(QuestionBinary, QuestionBinaryAdmin)

