from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from .models import Producto

class ProductoModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre="Laptop",
            descripcion="Laptop gaming",
            precio=Decimal('1000.00'),
            stock=10,
            categoria="Electrónicos"
        )

    def test_creacion_producto(self):
        self.assertEqual(self.producto.nombre, "Laptop")
        self.assertEqual(self.producto.descripcion, "Laptop gaming")
        self.assertEqual(self.producto.precio, Decimal('1000.00'))
        self.assertEqual(self.producto.stock, 10)
        self.assertEqual(self.producto.categoria, "Electrónicos")
        self.assertIsInstance(self.producto.fecha_creacion, timezone.datetime)
        self.assertEqual(self.producto.ventas_ultimo_mes, 0)
        self.assertEqual(self.producto.conf_tax_relation, Decimal('0.00'))

    def test_str_representation(self):
        self.assertEqual(str(self.producto), "Laptop")

    def test_actualizar_stock(self):
        self.producto.actualizar_stock(5)
        self.assertEqual(self.producto.stock, 15)

        self.producto.actualizar_stock(-3)
        self.assertEqual(self.producto.stock, 12)

    def test_registrar_venta(self):
        self.producto.registrar_venta(2)
        self.assertEqual(self.producto.stock, 8)
        self.assertEqual(self.producto.ventas_ultimo_mes, 2)

    def test_registrar_venta_stock_insuficiente(self):
        with self.assertRaises(ValueError):
            self.producto.registrar_venta(11)