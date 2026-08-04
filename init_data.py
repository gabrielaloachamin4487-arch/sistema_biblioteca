import os
import sys
import django
from datetime import timedelta
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca_project.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps'))
django.setup()

from django.contrib.auth.models import User
from catalogo.models import Categoria, Libro
from usuarios.models import Lector
from prestamos.models import Prestamo
from prestamos.utils_pdf import generar_comprobante_pdf

def crear_imagen_portada(titulo, color):
    img = Image.new('RGB', (400, 600), color=color)
    draw = ImageDraw.Draw(img)
    # Dibujar texto
    draw.rectangle([20, 20, 380, 580], outline=(255, 255, 255), width=3)
    draw.text((40, 280), titulo[:25], fill=(255, 255, 255))
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return ContentFile(buffer.getvalue())

def crear_pdf_muestra(titulo):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, f"MUESTRA GRATUITA - {titulo}")
    p.drawString(100, 730, "==================================================")
    p.drawString(100, 700, "Este es un fragmento de lectura autorizado para la biblioteca.")
    p.drawString(100, 680, "No debe superar los 8 MB de acuerdo con la norma de negocio.")
    p.showPage()
    p.save()
    return ContentFile(buffer.getvalue())

def run():
    print("🚀 Inicializando base de datos con datos de demostración...")

    # 1. Superusuario / Bibliotecario
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser('admin', 'admin@biblioteca.edu', 'admin123', first_name='Carlos', last_name='Bibliotecario')
        print("✔ Superusuario 'admin' (pass: admin123) creado.")
    else:
        admin_user = User.objects.get(username='admin')

    # 2. Lectores (Docente y Estudiantes)
    lectores_data = [
        {'username': 'estudiante1', 'first_name': 'Ana', 'last_name': 'Gómez', 'email': 'ana.gomez@estudiante.edu', 'codigo': 'EST-2026-001', 'tipo': 'Estudiante'},
        {'username': 'estudiante2', 'first_name': 'Luis', 'last_name': 'Martínez', 'email': 'luis.martinez@estudiante.edu', 'codigo': 'EST-2026-002', 'tipo': 'Estudiante'},
        {'username': 'docente1', 'first_name': 'Dra. Elena', 'last_name': 'Ríos', 'email': 'elena.rios@docente.edu', 'codigo': 'DOC-2026-099', 'tipo': 'Docente'},
    ]

    lectores_objs = []
    for ldata in lectores_data:
        u, created = User.objects.get_or_create(
            username=ldata['username'],
            defaults={
                'email': ldata['email'],
                'first_name': ldata['first_name'],
                'last_name': ldata['last_name'],
            }
        )
        if created:
            u.set_password('usuario123')
            u.save()

        lector, _ = Lector.objects.get_or_create(
            user=u,
            defaults={
                'codigo_institucional': ldata['codigo'],
                'tipo': ldata['tipo'],
                'estado': 'Habilitado'
            }
        )
        lectores_objs.append(lector)
    print("✔ Lectores de prueba creados.")

    # 3. Categorías
    cats = ['Tecnología & Programación', 'Ciencias Exactas', 'Literatura Hispana', 'Historia Universal']
    cat_objs = {}
    for cname in cats:
        cat, _ = Categoria.objects.get_or_create(nombre=cname)
        cat_objs[cname] = cat

    # 4. Libros
    libros_data = [
        {
            'titulo': 'Python a Fondo y Arquitectura Django',
            'autor': 'Guido van Rossum',
            'isbn': '978-0134685991',
            'cat': cat_objs['Tecnología & Programación'],
            'color': (37, 99, 235),
            'total': 5,
            'disp': 4
        },
        {
            'titulo': 'Cien Años de Soledad',
            'autor': 'Gabriel García Márquez',
            'isbn': '978-0307474728',
            'cat': cat_objs['Literatura Hispana'],
            'color': (245, 158, 11),
            'total': 3,
            'disp': 2
        },
        {
            'titulo': 'Principios de Física Cuántica',
            'autor': 'Richard Feynman',
            'isbn': '978-0465024933',
            'cat': cat_objs['Ciencias Exactas'],
            'color': (16, 185, 129),
            'total': 2,
            'disp': 1
        },
        {
            'titulo': 'Breve Historia del Siglo XX',
            'autor': 'Eric Hobsbawm',
            'isbn': '978-8484320470',
            'cat': cat_objs['Historia Universal'],
            'color': (239, 68, 68),
            'total': 4,
            'disp': 4
        }
    ]

    libros_objs = []
    for l in libros_data:
        libro, created = Libro.objects.get_or_create(
            isbn=l['isbn'],
            defaults={
                'titulo': l['titulo'],
                'autor': l['autor'],
                'categoria': l['cat'],
                'cantidad_total': l['total'],
                'copias_disponibles': l['disp'],
            }
        )
        if created:
            # Asignar imagen y PDF muestra
            img_file = crear_imagen_portada(l['titulo'], l['color'])
            pdf_file = crear_pdf_muestra(l['titulo'])
            libro.portada.save(f"portada_{l['isbn']}.jpg", img_file, save=False)
            libro.muestra_pdf.save(f"muestra_{l['isbn']}.pdf", pdf_file, save=True)
        libros_objs.append(libro)
    print("✔ Libros de prueba creados con portadas y muestras PDF.")

    # 5. Préstamos de Demostración
    hoy = timezone.now().date()
    
    # Préstamo Activo
    p1, _ = Prestamo.objects.get_or_create(
        libro=libros_objs[0],
        lector=lectores_objs[0],
        defaults={
            'fecha_prestamo': hoy - timedelta(days=2),
            'fecha_limite': hoy + timedelta(days=5),
            'estado': 'Activo'
        }
    )
    if p1.comprobante_pdf == '':
        generar_comprobante_pdf(p1)

    # Préstamo Atrasado (Para probar morosos)
    p2, created_p2 = Prestamo.objects.get_or_create(
        libro=libros_objs[1],
        lector=lectores_objs[1],
        defaults={
            'fecha_prestamo': hoy - timedelta(days=12),
            'fecha_limite': hoy - timedelta(days=5),
            'estado': 'Atrasado',
            'dias_retraso': 5
        }
    )
    if created_p2:
        lectores_objs[1].estado = 'Sancionado'
        lectores_objs[1].save()
        generar_comprobante_pdf(p2)

    print("✔ Préstamos de prueba y comprobantes PDF generados.")
    print("🎉 Demostración inicializada con éxito.")

if __name__ == '__main__':
    run()
