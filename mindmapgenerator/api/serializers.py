from rest_framework import serializers
from pdf_handler.models import Text, UploadedFile

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = '__all__'

class FileUploadedSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ('file','uploaded_on',)

