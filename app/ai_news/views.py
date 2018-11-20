# from django.http import HttpResponse, HttpResponseRedirect
# from django.shortcuts import get_object_or_404, render
# from django.urls import reverse
# from django.views import generic
#
# from .models import Article
#
#
# class IndexView(generic.ListView):
#     model = Article
#     template_name = 'ai_news/templates/index.html'
#     # context_object_name = 'latest_question_list'
#     #
#     # def get_queryset(self):
#     #     """Return the last five published questions."""
#     #     return Article.objects.order_by('-pub_date')[:5]
#
#
# class DetailView(generic.DetailView):
#     model = Article
#     template_name = 'ai_news/templates/detail.html'
#
#
# class ResultsView(generic.DetailView):
#     model = Article
#     template_name = 'ai_news/results.html'
#
#
# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")
#
#
# def detail(request, pk):
#     return HttpResponse("You're looking at question %s." % pk)
#
#
# def results(request, article_id):
#     question = get_object_or_404(Article, pk=article_id)
#     return render(request, 'ai_news/results.html', {'question': question})
#
#
# def vote(request, article_id):
#     article = get_object_or_404(Article, pk=article_id)
#     try:
#         selected_choice = article.choice_set.get(pk=request.POST['article'])
#     except (KeyError, Article.DoesNotExist):
#         # Redisplay the article voting form.
#         return render(request, 'ai_news/detail.html', {
#             'article': article,
#             'error_message': "You didn't select a choice.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse('polls:results', args=(article.id,)))

from django.http import HttpResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Article
from .serializers import EntrySerializer


def index(request):
    latest_question_list = Article.score.order_by('score')[:5]
    output = ', '.join([q.question_text for q in latest_question_list])
    return HttpResponse(output)


class EntryListAPIView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = EntrySerializer
    queryset = Article.objects.all()
