from rest_framework import serializers
from .models import Article

class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = (
            'id',
            'url',
            'score',
            'h1',
            'paragraph'
        )
