from rest_framework import serializers
from .models import PhaseParameterSet

class PhaseParameterSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhaseParameterSet
        fields = '__all__'
