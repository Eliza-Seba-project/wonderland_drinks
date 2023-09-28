import random
import string
import os

from PIL import Image
from io import BytesIO
from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

def random_string(length):
    """Generates a random string of given length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

class Ingredient(models.Model):
    unit_type = (('ml', 'mililitry'), ('szt', 'sztuk'))
    name = models.CharField(max_length=220)
    amount = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(300)], blank=True)
    unit = models.CharField(default='ml', choices=unit_type, max_length=3)

    def __str__(self):
        return f'{self.name}  |  {self.amount} {self.unit}'


class Drink(models.Model):
    name = models.CharField(max_length=100, blank=False)
    ingredients = models.ManyToManyField(Ingredient)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/', blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    drink_publish = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Zmiana nazwy zdjęcia głównego na losową

        self.image.name = random_string(10) + '.jpg'


        # Tworzenie miniaturki (thumbnail) na podstawie obrazu przy każdym zapisie
        self.thumbnail = self.create_thumbnail()


        super(Drink, self).save(*args, **kwargs)

    def create_thumbnail(self):
        # Otwórz obraz główny
        image = Image.open(self.image)

        # Ustaw maksymalny rozmiar miniaturki (300x200)
        max_size = (300, 200)

        # Warunek, który sprawdzi, czy obraz jest większy niż maksymalny rozmiar
        if image.width > max_size[0] or image.height > max_size[1]:
            # Skaluj obraz zachowując proporcje
            image.thumbnail(max_size, Image.LANCZOS)

        # Tworzenie miniaturki
        thumbnail_io = BytesIO()
        image.save(thumbnail_io, 'JPEG', quality=85)

        # Wygeneruj losową nazwę dla miniaturki
        thumbnail_filename = random_string(10) + '.jpg'

        # Zapisz miniaturkę z losową nazwą w katalogu "thumbnails/"

        self.thumbnail.save(thumbnail_filename,
                            InMemoryUploadedFile(thumbnail_io, None, thumbnail_filename, 'image/jpeg', thumbnail_io.tell(),
                                                 None), save=False)

        return self.thumbnail

    def __str__(self):
        return f'{self.name} | {self.creation_date} | {self.description}'
