from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from catalogo.models import Categoria, Libro
from usuarios.models import Lector
from prestamos.models import Prestamo

class BibliotecaLogicTestCase(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Tecnología")
        self.user1 = User.objects.create_user('estudiante1', 'e1@test.com', 'pass123')
        self.lector1 = Lector.objects.create(
            user=self.user1,
            codigo_institucional='EST-101',
            tipo='Estudiante',
            estado='Habilitado'
        )

        self.user2 = User.objects.create_user('estudiante2', 'e2@test.com', 'pass123')
        self.lector2 = Lector.objects.create(
            user=self.user2,
            codigo_institucional='EST-102',
            tipo='Estudiante',
            estado='Sancionado'
        )

        self.libro_disponible = Libro.objects.create(
            titulo="Django para Profesionales",
            autor="Autor Test",
            isbn="111-222-333",
            categoria=self.categoria,
            cantidad_total=2,
            copias_disponibles=2
        )

        self.libro_agotado = Libro.objects.create(
            titulo="Libro Agotado Test",
            autor="Autor Test",
            isbn="999-888-777",
            categoria=self.categoria,
            cantidad_total=1,
            copias_disponibles=0
        )

    def test_creacion_prestamo_exitoso(self):
        """Verifica que al crear un préstamo disminuye en 1 la copia disponible del libro."""
        prestamo = Prestamo.objects.create(
            libro=self.libro_disponible,
            lector=self.lector1,
            fecha_limite=timezone.now().date() + timedelta(days=7)
        )
        self.libro_disponible.refresh_from_db()
        self.assertEqual(self.libro_disponible.copias_disponibles, 1)
        self.assertEqual(prestamo.estado, 'Activo')
        self.assertTrue(prestamo.codigo_verificacion.startswith('BIB-'))

    def test_no_prestar_si_copias_cero(self):
        """Validación de negocio 1: No se puede prestar un libro si copias disponibles = 0."""
        with self.assertRaises(ValidationError):
            p = Prestamo(
                libro=self.libro_agotado,
                lector=self.lector1,
                fecha_limite=timezone.now().date() + timedelta(days=7)
            )
            p.clean()

    def test_no_prestar_a_lector_sancionado(self):
        """Validación de negocio 2: Lector sancionado no puede realizar nuevos préstamos."""
        with self.assertRaises(ValidationError):
            p = Prestamo(
                libro=self.libro_disponible,
                lector=self.lector2,
                fecha_limite=timezone.now().date() + timedelta(days=7)
            )
            p.clean()

    def test_devolucion_con_calculo_de_mora(self):
        """Validación de negocio 3: Al devolver con retraso se calcula días de mora y se sanciona."""
        hoy = timezone.now().date()
        prestamo = Prestamo.objects.create(
            libro=self.libro_disponible,
            lector=self.lector1,
            fecha_prestamo=hoy - timedelta(days=10),
            fecha_limite=hoy - timedelta(days=3),
            estado='Activo'
        )
        
        prestamo.registrar_devolucion()
        self.assertEqual(prestamo.estado, 'Atrasado')
        self.assertEqual(prestamo.dias_retraso, 3)
        self.lector1.refresh_from_db()
        self.assertEqual(self.lector1.estado, 'Sancionado')
        self.libro_disponible.refresh_from_db()
        self.assertEqual(self.libro_disponible.copias_disponibles, 2)
