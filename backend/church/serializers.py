from rest_framework import serializers
from .models import ChurchProfile
class ChurchProfileSerializer(serializers.ModelSerializer):
    class Meta: model=ChurchProfile; fields=('id','name','logo','address','phone','email','regular_schedule','updated_at'); read_only_fields=('id','updated_at')
