from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import AdeConfig, Resource


class ResourceSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        if 'children' in obj.fields:
            for child in obj.fields['children']:
                child['id'] = reverse(
                    'api:resource',
                    kwargs={
                        'ext_id': child['id'],
                        'format': self.context['format']
                    },
                    request=self.context['request'])
        return obj.fields

    class Meta:
        model = Resource


class AdeConfigSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        return {
            'base_url': obj.ade_url,
            'params': obj.parameters
        }

    class Meta:
        model = AdeConfig
