from rest_framework import generics
from .models import ControllerPreset
from .serializers import ControllerPresetSerializer

class PresetListCreateView(generics.ListCreateAPIView):
    queryset = ControllerPreset.objects.all()
    serializer_class = ControllerPresetSerializer

class PresetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ControllerPreset.objects.all()
    serializer_class = ControllerPresetSerializer
