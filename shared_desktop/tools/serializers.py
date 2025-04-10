from rest_framework import serializers
from .models import PhaseParameterSet, Detector

class PhaseParameterSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhaseParameterSet
        fields = '__all__'


class DetectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detector
        fields = '__all__'
