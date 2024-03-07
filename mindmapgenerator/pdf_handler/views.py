from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import fitz
import pandas as pd
import os
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
# import pdb
# from .templates
# Create your views here.

def submitFile(request):
    template = loader.get_template("submitFile.html")
    return HttpResponse(template.render({},request))
def getFileTest():
    i = 0


class FileUploadView(APIView):
    parser_classes = [FileUploadParser]
    def put(self,request,format=None):
        if(request.method == 'POST'):
            file_obj = request.data['data']
            extractHighlightedInfo(file_obj)
        return Response(status=204)
        # template = loader.get_template("highlight.html")
        # return HttpResponse(template.render({},request))
    def post(self,request,format=None):
        file = request.data['file']
        filename = file.name
        extractHighlightedInfo(file)
        # return Response({'received data': request.data})
        return Response({'received data':{'filename':filename}})

def openFile(request):
    template = loader.get_template("openFile.html")
    return HttpResponse( template.render({}, request))


def extractHighlightedInfo(file):
    # document = os.path.join('Thi_Thuy_Nga_Nguyen_resume (1).pdf')
    # doc = fitz.open(document)
    doc = fitz.open(file)
    unique_color = checkColor(doc)
    color_definitions = {}
    data_by_color = {}
    key = 1
    for color in unique_color:
        color_definitions[key] = color
        data_by_color[key] = []
        key += 1
    for i in range(len(doc)):
        page = doc[i]
        annotations = page.annots()
        for annotation in annotations:
            if annotation.type[1] == "Highlight":
                color = annotation.colors["stroke"]
                if color in color_definitions.values():
                    structure = page.get_text("dict")
                    content = []
                    for block in structure["blocks"]:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                r = fitz.Rect(span["bbox"])
                                if r.intersects(annotation.rect):
                                    content.append(span["text"])
                    content =" ".join(content)
                    for color_name, color_rgb in color_definitions.items():
                        if color == color_rgb:
                            data_by_color[color_name].append(content)
    for color_name, data in data_by_color.items():
        if data:
            df = pd.DataFrame(data, columns = ["Text"])
            df.to_csv(f'highlighted_text_{color_name}.csv',index= False)
        print(str(color_name) + " : ")
        print(data)


def checkColor(doc):
    unique_colors = []
    for i in range(len(doc)):
        page = doc[i]
        annotations = page.annots()
        for annotation in annotations:
                color = annotation.colors["stroke"]
                unique_colors.append(color)
    return unique_colors
