import os, base64, uuid
from django.utils.deconstruct import deconstructible
from rest_framework.permissions import BasePermission, SAFE_METHODS


@deconstructible
class UniqueFilename:
    """
    Enforce unique upload file names.
    Usage:
    class MyModel(models.Model):
        file = ImageField(upload_to=unique_filename("path/to/upload/dir"))
    """
    def __init__(self, path):
        self.path = path
    def __call__(self, instance, filename):
        name, ext = os.path.splitext(filename)
        name = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8').replace('=', '')
        return os.path.join(self.path, f"{name}{ext}")


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
