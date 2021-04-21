from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Album, Artist, FileUpload

class UploadSerializer(serializers.Serializer):
    name = serializers.FileField()

    class Meta:
        model = FileUpload
        fields = ('id', 'name')
        datatables_always_serialize = ('id',)

    def to_internal_value(self, data):
        print("*1" * 30, data["name"])
        print(data, type(data["name"]))
        # return get_object_or_404(FileUpload, pk=FileUpload.objects.count())
        if type(data["name"]) is str:
            return get_object_or_404(FileUpload, pk=FileUpload.objects.count())
        else:
            return super().to_internal_value(data=data)

    def create(self, validated_data):
        # print(FileUpload.objects)
        return FileUpload.objects.create(name = validated_data["name"])


class ArtistSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    # if we need to edit a field that is a nested serializer,
    # we must override to_internal_value method
    def to_internal_value(self, data):
        return get_object_or_404(Artist, pk=data['id'])

    class Meta:
        model = Artist
        fields = (
            'id', 'name',
        )
        # Specifying fields in datatables_always_serialize
        # will also force them to always be serialized.
        datatables_always_serialize = ('id',)


class AlbumSerializer(serializers.ModelSerializer):
    file = UploadSerializer()

    artist_name = serializers.ReadOnlyField(source='artist.name')
    
    # DRF-Datatables can deal with nested serializers as well.
    artist = ArtistSerializer()
    genres = serializers.SerializerMethodField()
    artist_view = ArtistSerializer(source="artist", read_only=True)

    @staticmethod
    def get_genres(album):
        return ', '.join([str(genre) for genre in album.genres.all()])

    # If you want, you can add special fields understood by Datatables,
    # the fields starting with DT_Row will always be serialized.
    # See: https://datatables.net/manual/server-side#Returned-data
    DT_RowId = serializers.SerializerMethodField()
    DT_RowAttr = serializers.SerializerMethodField()

    def create(self, validated_data):
        print("CREATE " * 20)
        file_name = validated_data.pop('file')
        artist_id = validated_data.pop('artist')
        rank = validated_data.pop('rank')
        name = validated_data.pop('name')
        year = validated_data.pop('year')

        print(file_name)
        # print(Album.objects.filter(rank=rank))
        if self.help_text == 'edit':
            albums = Album.objects.filter(rank=rank).update(file=file_name, artist = artist_id, name=name, year=year)
        elif self.help_text == 'create':
            print("Creating")
            albums = Album.objects.create(file=file_name, artist = artist_id, rank=rank, name=name, year=year)
        elif self.help_text == 'remove':
            albums = Album.objects.filter(rank=rank).delete()

        return albums
        # return FileUpload.objects.create(name = validated_data['file']['upload_file'])

    @staticmethod
    def get_DT_RowId(album):
        return album.pk

    @staticmethod
    def get_DT_RowAttr(album):
        return {'data-pk': album.pk}

    class Meta:
        model = Album
        fields = [
            'DT_RowId', 'DT_RowAttr', 'rank', 'name',
            'year', 'artist_name', 'genres', 'artist',
            'artist_view',
             'file'
        ]
    