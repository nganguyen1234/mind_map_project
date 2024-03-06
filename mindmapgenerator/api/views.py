from rest_framework.response import Response
from rest_framework.decorators import api_view
from pdf_handler.models import Text
from .serializers import TextSerializer


@api_view(["GET"])
def getData(request):
    content1 = Text('omeerwer')
    serializer = TextSerializer(content1)
    person = {'name':'Dennis','age':23}
    return Response(serializer.data)

