from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El Email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Django maneja esto internamente
    rol = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    objects = UsuarioManager()

    def __str__(self):
        return self.username

    def autenticar(self):
        """
        Método para autenticar al usuario.
        """
        pass

    def cambiar_contrasena(self, nueva_contrasena):
        """
        Método para cambiar la contraseña del usuario.
        """
        self.set_password(nueva_contrasena)
        self.save()