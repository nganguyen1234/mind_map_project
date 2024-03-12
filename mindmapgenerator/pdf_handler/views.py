import logging
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
from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType
import os.path
import zipfile
import json
import shutil

# import pdb
# from .templates
# Create your views here.

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

def extractText(request):
    zip_file = "media/output/ExtractTextInfoFromPDF.zip"

    if os.path.isfile(zip_file):
        os.remove(zip_file)    
    path = 'Thi_Thuy_Nga_Nguyen_resume (1).pdf'
    try:
    # get base path.
        base_path = "D:\study-cs\mind_map_generator\mindmapgenerator\media"

    # Initial setup, create credentials instance.
        credentials = Credentials.service_principal_credentials_builder() \
    .with_client_id('4eba74b2d7014067a838a07e02300fae') \
    .with_client_secret('p8e-58y6jzANKrBi9pHzUEeJmngHcDqELp-W') \
    .build()

    # Create an ExecutionContext using credentials and create a new operation instance.
        execution_context = ExecutionContext.create(credentials)
        extract_pdf_operation = ExtractPDFOperation.create_new()

    # Set operation input from a source file.
        source = FileRef.create_from_local_file(path)
        extract_pdf_operation.set_input(source)

    # Build ExtractPDF options and set them into the operation
        extract_pdf_options: ExtractPDFOptions = ExtractPDFOptions.builder() \
        .with_element_to_extract(ExtractElementType.TEXT) \
        .build()
        extract_pdf_operation.set_options(extract_pdf_options)

    # Execute the operation.
        result: FileRef = extract_pdf_operation.execute(execution_context)

#Save the result to the specified location.
        try:
            result.save_as(zip_file)
        except OSError:
            shutil.move(result._file_path, zip_file)
    except (ServiceApiException, ServiceUsageException, SdkException):
        logging.exception("Exception encountered while executing operation")
    # template = loader.get_template("openFile.html")
    # return HttpResponse( template.render({}, request))
    archive = zipfile.ZipFile(zip_file, 'r')
    jsonentry = archive.open('structuredData.json')
    jsondata = jsonentry.read()
    data = json.loads(jsondata)

