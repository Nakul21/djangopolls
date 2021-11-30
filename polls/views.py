from django.http import HttpResponseRedirect
from .models import Choice, Question
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.db.models import F
from django.utils import timezone
# def index(request):
#     latest_questions_list = Question.objects.order_by('-pub_date')[:5]
#     context = {
#         'latest_questions_list': latest_questions_list
#     }
#     return render(request, 'polls/index.html', context)
#
# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})
#
# def results(request, question_id):
#     '''
#
#     This view displays the votes placed on each choice for a particular question
#     :param  request:
#     :param  question_id: unique id or the primary key which helps in uniquely identifying the question
#     :return: renders/displays the results html template, render takes in the url and the question
#              which is identified with the help of a primary key (django automatically generates pk for a
#              model/table) on which the page will be redirected.
#
#     '''
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/results.html', {'question': question})

class Indexview(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_questions_list'

    def get_queryset(self):
        """Returns the last 5 questions entered by the admin/ published by the admin"""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

class Detailview(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
           This methods excludes displaying any questions which are not
           published yet/future questions
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class Resultsview(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    """
    This view lets the user to enter the choice for a particular question,
    after entering the desired choice, the choice get's saved and it's counted/increemented
    which is counted as a vote on that question, lastly this view redirects the user to directly
    the resultsv view.
    :param request:
    :param question_id: unique id or the primary key which helps in uniquely identifying the question
    :return: result view , redirects it result view, as it contains the url which directs it to results view

    """
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except(KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't enter a choice"
        })
    else:
        """
        used the F() method to avoid race condition : A condition that occurs when two or more users try 
        to access the app/website at the same time and the data that is getting modified in the model/
        table is same, here in this case votes is an attribute of of choice class and if two users try
        to enter to vote for a same question at the same time the database fetches the updated and saved
        values rather than fetching the original(old value) from the database
        """
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        question = Question.objects.get(pk=question_id)
        selected_choice.refresh_from_db()

        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


