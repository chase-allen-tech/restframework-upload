from django.db import models


class Genre(models.Model):
    name = models.CharField('Name', max_length=80)

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'
        ordering = ['name']

    def __str__(self):
        return self.name

def upload_location(instance, filename):
    file_path = 'uploaded_data/{filename}'.format(
        filename=filename
    )
    return file_path

class FileUpload(models.Model):
    name     = models.FileField(upload_to=upload_location)
    # date_published  = models.DateTimeField(auto_now_add=True, verbose_name="date published")
    # date_updated    = models.DateTimeField(auto_now=True, verbose_name="date updated")

    class Meta:
        verbose_name = 'FileUpload'
        verbose_name_plural = 'FildUploads'
        ordering = ['name']

    def __str__(self):
        # print(str(self.name))
        # print("^^" * 30)
        return str(self.name)
        # return "self.name"


class Artist(models.Model):
    name = models.CharField('Name', max_length=80)

    class Meta:
        verbose_name = 'Artist'
        verbose_name_plural = 'Artists'
        ordering = ['name']

    def __str__(self):
        return self.name


class Album(models.Model):
    name = models.CharField('Name', max_length=80)
    rank = models.PositiveIntegerField('Rank')
    year = models.PositiveIntegerField('Year')

    file = models.ForeignKey(
        FileUpload,
        models.CASCADE,
        verbose_name='FileUpload',
        related_name="albums",
        default=None, blank=True, null=True
    )

    artist = models.ForeignKey(
        Artist,
        models.CASCADE,
        verbose_name='Artist',
        related_name='albums'
    )
    genres = models.ManyToManyField(
        Genre,
        verbose_name='Genres',
        related_name='albums'
    )

    class Meta:
        verbose_name = 'Album'
        verbose_name_plural = 'Albums'
        ordering = ['name']

    def __str__(self):
        return self.name
