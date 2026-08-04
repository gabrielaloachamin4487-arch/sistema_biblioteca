import os
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generar_comprobante_pdf(prestamo):
    """Genera un archivo PDF elegante con el comprobante de entrega del préstamo."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        alignment=1 # Centrado
    )

    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#64748B'),
        alignment=1
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A')
    )

    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    elements = []

    # Encabezado del documento
    elements.append(Paragraph("SISTEMA INSTITUCIONAL DE BIBLIOTECA", title_style))
    elements.append(Paragraph("Comprobante de Préstamo de Recurso Bibliográfico", subtitle_style))
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563EB'), spaceAfter=15))

    # Información del comprobante
    data_resumen = [
        [Paragraph("<b>Código de Verificación:</b>", normal_style), Paragraph(f"<font color='#2563EB'><b>{prestamo.codigo_verificacion}</b></font>", normal_style)],
        [Paragraph("<b>Fecha de Emisión:</b>", normal_style), Paragraph(prestamo.fecha_prestamo.strftime('%d/%m/%Y'), normal_style)],
        [Paragraph("<b>Fecha Límite de Devolución:</b>", normal_style), Paragraph(f"<font color='#DC2626'><b>{prestamo.fecha_limite.strftime('%d/%m/%Y')}</b></font>", normal_style)],
        [Paragraph("<b>Estado de Préstamo:</b>", normal_style), Paragraph(prestamo.estado, normal_style)],
    ]
    t_resumen = Table(data_resumen, colWidths=[200, 300])
    t_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(t_resumen)
    elements.append(Spacer(1, 20))

    # Datos del Lector
    elements.append(Paragraph("Datos del Lector Beneficiario", h2_style))
    elements.append(Spacer(1, 5))
    nombre_lector = prestamo.lector.user.get_full_name() or prestamo.lector.user.username
    data_lector = [
        [Paragraph("<b>Nombre Completo:</b>", normal_style), Paragraph(nombre_lector, normal_style)],
        [Paragraph("<b>Código Institucional:</b>", normal_style), Paragraph(prestamo.lector.codigo_institucional, normal_style)],
        [Paragraph("<b>Tipo de Lector:</b>", normal_style), Paragraph(prestamo.lector.tipo, normal_style)],
        [Paragraph("<b>Correo Electrónico:</b>", normal_style), Paragraph(prestamo.lector.user.email or "No registrado", normal_style)],
    ]
    t_lector = Table(data_lector, colWidths=[200, 300])
    t_lector.setStyle(TableStyle([
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    elements.append(t_lector)
    elements.append(Spacer(1, 20))

    # Datos del Libro
    elements.append(Paragraph("Detalles del Libro Prestado", h2_style))
    elements.append(Spacer(1, 5))
    data_libro = [
        [Paragraph("<b>Título:</b>", normal_style), Paragraph(prestamo.libro.titulo, normal_style)],
        [Paragraph("<b>Autor:</b>", normal_style), Paragraph(prestamo.libro.autor, normal_style)],
        [Paragraph("<b>ISBN:</b>", normal_style), Paragraph(prestamo.libro.isbn, normal_style)],
        [Paragraph("<b>Categoría:</b>", normal_style), Paragraph(str(prestamo.libro.categoria or "Sin categoría"), normal_style)],
    ]
    t_libro = Table(data_libro, colWidths=[200, 300])
    t_libro.setStyle(TableStyle([
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    elements.append(t_libro)
    elements.append(Spacer(1, 30))

    # Cláusula y Firmas
    clausula_text = (
        "El lector compromete su responsabilidad a conservar en óptimo estado el material recibido y realizar la "
        "devolución a más tardar en la fecha límite señalada. De exceder el plazo, la cuenta quedará temporalmente sancionada."
    )
    elements.append(Paragraph(clausula_text, subtitle_style))
    elements.append(Spacer(1, 40))

    data_firmas = [
        [Paragraph("_______________________________<br/>Firma del Lector", subtitle_style),
         Paragraph("_______________________________<br/>Firma y Sello de Biblioteca", subtitle_style)]
    ]
    t_firmas = Table(data_firmas, colWidths=[250, 250])
    t_firmas.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    elements.append(t_firmas)

    # Construir PDF
    doc.build(elements)

    pdf_content = buffer.getvalue()
    buffer.close()

    # Guardar en FileField del modelo
    filename = f"comprobante_{prestamo.codigo_verificacion}.pdf"
    prestamo.comprobante_pdf.save(filename, ContentFile(pdf_content), save=True)
    return prestamo.comprobante_pdf
