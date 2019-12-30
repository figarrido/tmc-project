from rest_framework import serializers

class TMCSerializer(serializers.Serializer):
    tmc = serializers.FloatField(read_only=True)
