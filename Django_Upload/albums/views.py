from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
import json
from django.http import JsonResponse

from rest_framework_datatables_editor.filters import DatatablesFilterBackend
from rest_framework_datatables_editor.pagination import (
    DatatablesPageNumberPagination)
from rest_framework_datatables_editor.renderers import (DatatablesRenderer)
from rest_framework_datatables_editor.viewsets import (
    DatatablesEditorModelViewSet)
from .models import Album, Artist, Genre, FileUpload
from .serializers import AlbumSerializer, ArtistSerializer, UploadSerializer


def index(request):
    return render(request, 'albums/albums.html')

def get_album_options():
    return "options", {
        "artist.id": [{'label': obj.name, 'value': obj.pk}
                      for obj in Artist.objects.all()],
        "genre": [{'label': obj.name, 'value': obj.pk}
                  for obj in Genre.objects.all()]
    }


class AlbumViewSet(DatatablesEditorModelViewSet):
    queryset = Album.objects.all().order_by('rank')
    serializer_class = AlbumSerializer
    
    file_s = None

    def get_options(self):
        return get_album_options()

    class Meta:
        datatables_extra_json = ('get_options', )

    def update(self, request):
        print("^^" * 30)

    def create(self, request):
        upload_file = request.FILES.get('upload')

        print(request.data['action'])

        if request.data["action"] == 'upload':
            print("*" * 50, "Upload/Create")


            if upload_file == None:
                return Response("Please select file")

            content_type = upload_file.content_type
            response = "POST API and you have uploaded a {} file".format(content_type)

            print("*" * 50)
            print(content_type)

            ct = content_type

            if ct != 'image/jpeg' and ct != 'image/png' and ct != 'image/jpg' and ct != 'application/pdf':
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

            serializer = UploadSerializer(data={'name': request.data["upload"]}, instance=None)

            if serializer.is_valid():
                serializer.save()

                print("*" * 50, "Upload/Create End")
                arr = []
                arr.append(serializer.data["name"])
                data_url = serializer.data
                data_url["name"] = "http://localhost:8000" + data_url["name"]
                data = {
                    "upload": {
                        "id": data_url
                    },
                    "files": {"tbl": arr},
                }
                return JsonResponse(data)
                # return Response(serializer.data, status=status.HTTP_200_OK, headers={"OK": "OK"})
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(response)

        elif request.data["action"] == 'edit' or request.data["action"] == 'create' or request.data["action"] == 'remove':
            print("*" * 50, "Album/Update Start")
            print(request.data)

            da = request.data
            # print(json.dumps(da)[0])
            das = json.dumps(da)
            START, index = False, 0
            for i in range(len(das)):
                if das[i] == ']':
                    break
                if START == True:
                    index = index * 10 + int(das[i])
                if das[i] == '[':
                    START = True
            
            index = str(index)

            filename = ''
            if 'data['+index+'][file][name]' in da:
                filename = da['data['+index+'][file][name]']
            print(filename)
            data = {
                "rank": da['data['+index+'][rank]'],
                "artist": {'id': int(da['data['+index+'][artist][id]'])},
                "name": da['data['+index+'][name]'],
                "year": da['data['+index+'][year]'],
                "file": {"name": filename},
            }


            print("-" * 5, data)

            album_s = AlbumSerializer(data=data, instance=None, help_text=request.data["action"])
            

            if album_s.is_valid():
                album_s.save()
                print("*" * 50, "Album/Update End")
                return Response({}, status=status.HTTP_200_OK)
            else:
                print("*" * 50, "Album/Update End")
                print(album_s.errors)
                return Response(album_s.errors, status=status.HTTP_400_BAD_REQUEST)
        # elif request.data["action"] == 'remove':
        #     print(request.data)


class ArtistViewSet(viewsets.ViewSet):
    queryset = Artist.objects.all().order_by('name')
    serializer_class = ArtistSerializer

    filter_backends = (DatatablesFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (DatatablesRenderer,)

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def get_options(self):
        return get_album_options()

    class Meta:
        datatables_extra_json = ('get_options', )


    
