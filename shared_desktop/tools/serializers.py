from rest_framework import serializers
from .models import ControllerPreset, PhaseParameterSet, Detector

class PhaseParameterSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhaseParameterSet
        fields = '__all__'


class DetectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detector
        fields = '__all__'


class ControllerPresetSerializer(serializers.ModelSerializer):
    # Переопределяем поле `name` и убираем UniqueValidator
    name = serializers.CharField()

    class Meta:
        model = ControllerPreset
        fields = '__all__'

    def create(self, validated_data):
        name = validated_data.get('name')
        instance, _ = ControllerPreset.objects.update_or_create(
            name=name,
            defaults=validated_data
        )
        return instance
