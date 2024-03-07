from rest_framework.response import Response
from rest_framework.decorators import api_view
from pdf_handler.models import Text
from .serializers import TextSerializer, FileUploadedSerializer
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser,FileUploadParser
from rest_framework import status
from pdf_handler import views
from django.http import HttpResponse
from django.template import loader
@api_view(["GET"])
def getData(request):
    content1 = Text('omeerwer') 
    serializer = TextSerializer(content1)
    return Response(serializer.data)


class FileUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser,FileUploadParser)
    serializer_class = FileUploadedSerializer

    def post(self,request,*arg, **kwargs):
        print(request.data)
        serializer = self.serializer_class(data = request.data)
        if (serializer.is_valid()):
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        print(serializer.errors)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        # template = loader.get_template("openFile.html")
        # return HttpResponse( template.render({}, request))