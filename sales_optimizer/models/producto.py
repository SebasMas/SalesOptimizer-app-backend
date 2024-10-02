from django.db import models
from django.utils import timezone

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    categoria = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    ventas_ultimo_mes = models.IntegerField(default=0)
    conf_tax_relation = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return self.nombre

    def actualizar_stock(self, cantidad):
        self.stock += cantidad
        self.save()

    def registrar_venta(self, cantidad):
        if self.stock >= cantidad:
            self.stock -= cantidad
            self.ventas_ultimo_mes += cantidad
            self.save()
        else:
            raise ValueError("Stock insuficiente para realizar la venta")