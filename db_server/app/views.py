from django.http import HttpResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Article
from .serializers import EntrySerializer


def index(request):
    latest_question_list = Article.objects.order_by()
    output = ', '.join([q.question_text for q in latest_question_list])
    return HttpResponse(output)


class EntryListAPIView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = EntrySerializer
    queryset = Article.objects.order_by('score').reverse()