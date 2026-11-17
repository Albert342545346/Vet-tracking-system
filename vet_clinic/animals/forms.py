"""Формы приложения animals (ПР11)."""
from django import forms

from .models import Animal

MAX_PHOTO_SIZE = 2 * 1024 * 1024  # 2 МБ
ALLOWED_PHOTO_FORMATS = {"JPEG", "PNG", "WEBP"}


class AnimalForm(forms.ModelForm):
    """Создание животного с загрузкой фотографии."""

    class Meta:
        model = Animal
        fields = ["name", "species", "age", "owner", "photo"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "species": forms.TextInput(attrs={"class": "form-control"}),
            "age": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "owner": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
        }
        help_texts = {
            "photo": "JPEG, PNG или WEBP, не более 2 МБ.",
        }

    def clean_photo(self):
        """Ограничить размер и формат изображения."""
        photo = self.cleaned_data.get("photo")
        if photo and hasattr(photo, "size"):
            if photo.size > MAX_PHOTO_SIZE:
                raise forms.ValidationError(
                    "Файл слишком большой (максимум 2 МБ)."
                )
            image = getattr(photo, "image", None)
            if image is not None and image.format not in (
                ALLOWED_PHOTO_FORMATS
            ):
                raise forms.ValidationError(
                    "Допустимы только JPEG, PNG и WEBP."
                )
        return photo
