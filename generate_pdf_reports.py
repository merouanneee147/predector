# -*- coding: utf-8 -*-
"""
Generateur de Rapports PDF - Systeme de Soutien Pedagogique
===============================================================
Genere des rapports PDF pour l'administration et les etudiants
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import os

# Chemin absolu basé sur l'emplacement de ce fichier
BASE_PATH = Path(__file__).parent.absolute()
OUTPUT_PATH = BASE_PATH / "output_projet4"
REPORTS_PATH = OUTPUT_PATH / "rapports_pdf"
REPORTS_PATH.mkdir(parents=True, exist_ok=True)

# Dictionnaire de traduction des modules (arabe → français)
TRADUCTION_MODULES = {
    # Mathématiques
    'رياضيات 1': 'Mathematiques 1',
    'رياضيات 2': 'Mathematiques 2',
    'رياضيات 3': 'Mathematiques 3',
    'رياضيات 4': 'Mathematiques 4',
    'التحليل الرياضي': 'Analyse Mathematique',
    'التحليل العددي': 'Analyse Numerique',
    'الجبر الخطي': 'Algebre Lineaire',
    'الجبر المنطقي': 'Algebre de Boole',
    'جبر المنطق': 'Algebre de Boole',
    'بحوث العمليات 1': 'Recherche Operationnelle 1',
    
    # Physique
    'الفيزياء الحديثة': 'Physique Moderne',
    'الفيزياء العامة': 'Physique Generale',
    
    # Langues
    'لغة انكليزية 1': 'Anglais 1',
    'لغة انكليزية 2': 'Anglais 2',
    'لغة انكليزية 4': 'Anglais 4',
    'اللغة الانكليزية 3': 'Anglais 3',
    'اللغة الانكليزية 4': 'Anglais 4',
    'لغة فرنسية 2': 'Francais 2',
    'اللغة الفرنسية 3': 'Francais 3',
    'اللغة الفرنسية 4': 'Francais 4',
    'اللغة العربية': 'Langue Arabe',
    
    # Informatique
    'برمجة': 'Programmation',
    'برمجة منطقية': 'Programmation Logique',
    'برمجة وتطبيقاتها': 'Programmation et Applications',
    'لغات برمجة': 'Langages de Programmation',
    'مبادئ حواسيب': 'Principes Informatiques',
    'الخوارزميات وبنى المعطيات': 'Algorithmes et Structures de Donnees',
    'برمجيات متقدمة في نظم التحكم 1': 'Logiciels Avances Controle 1',
    'برمجيات متقدمة في نظم التحكم 2': 'Logiciels Avances Controle 2',
    'النظم المنطقية والدارات الرقمية': 'Systemes Logiques et Circuits Numeriques',
    
    # Electronique
    'الدارات الالكترونية': 'Circuits Electroniques',
    'دارات الكترونية': 'Circuits Electroniques',
    'دارات الإلكترونية': 'Circuits Electroniques',
    'الأدوات الالكترونية': 'Composants Electroniques',
    'الأدوات نصف الناقلة': 'Semi-conducteurs',
    'هندسة الكترونية': 'Genie Electronique',
    'هندسة الكترونية 1': 'Genie Electronique 1',
    'هندسة الكترونية 2': 'Genie Electronique 2',
    'هندسة إلكترونية': 'Genie Electronique',
    'الهندسة الالكترونية 1': 'Ingenierie Electronique 1',
    'الهندسة الإلكترونية 2': 'Ingenierie Electronique 2',
    'القياسات الالكترونية': 'Mesures Electroniques',
    'القياسات الإلكترونية': 'Mesures Electroniques',
    
    # Electrique
    'نظرية الدارات الكهربائية': 'Theorie des Circuits Electriques',
    'نظرية الدارات الكهربائية 1': 'Theorie des Circuits 1',
    'نظرية الدارات الكهربائية 2': 'Theorie des Circuits 2',
    'الآلات الكهربائية': 'Machines Electriques',
    'الآلات الكهربائية 1': 'Machines Electriques 1',
    'الآلات الكهربائية 2': 'Machines Electriques 2',
    'الآلات والقيادة الكهربائية': 'Machines et Commande Electrique',
    'أسس الهندسة الكهربائية 1': 'Fondements Genie Electrique 1',
    'أسس الهندسة الكهربائية 2': 'Fondements Genie Electrique 2',
    'الهندسة الكهربائية': 'Genie Electrique',
    'هندسة كهربائية': 'Genie Electrique',
    'مبادئ الهندسة الكهربائية': 'Principes Genie Electrique',
    'القياسات الكهربائية وأجهزة القياس': 'Mesures Electriques',
    'تكنولوجيا المواد الكهربائية': 'Technologie Materiaux Electriques',
    'نظم القدرة الكهربائية': 'Systemes de Puissance',
    'الورش الكهربائية والالكترونية': 'Ateliers Electriques',
    
    # Electromagnétisme
    'الحقول الكهرومغناطيسية': 'Champs Electromagnetiques',
    'حقول الكهرومغناطيسية': 'Champs Electromagnetiques',
    'نظرية الحقول الكهرطيسية': 'Theorie des Champs EM',
    'الحقول المغناطيسية في الآلات الكهربائية': 'Champs Magnetiques Machines',
    
    # Signaux et Systèmes
    'إشارات ونظم': 'Signaux et Systemes',
    'مبادئ الاتصالات': 'Principes Telecommunications',
    
    # Contrôle/Commande
    'تحكم حديث': 'Controle Moderne',
    'تحكم حديث 1': 'Controle Moderne 1',
    
    # Mécanique
    'الهندسة الميكانيكية': 'Genie Mecanique',
    'هندسة ميكانيكية': 'Genie Mecanique',
    'هندسة ميكانيكية ': 'Genie Mecanique',
    'هندسة ميكانيكية 1': 'Genie Mecanique 1',
    'هندسة ميكانيكية 2': 'Genie Mecanique 2',
    'ميكانيك هندسي': 'Mecanique de l\'Ingenieur',
    'مقاومة المواد وخواصها': 'Resistance des Materiaux',
    
    # Chimie et Matériaux
    'الكيمياء الصناعية': 'Chimie Industrielle',
    
    # Dessin
    'الرسم الهندسي': 'Dessin Technique',
    
    # Autres
    'الثقافة القومية الاشتراكية': 'Culture Nationale',
    'الأمن الصناعي والاقتصاد الهندسي': 'Securite Industrielle et Economie',
    'Unknown': 'Inconnu'
}

def traduire_module(nom):
    """Traduit le nom du module de l'arabe vers le français"""
    if pd.isna(nom):
        return 'Inconnu'
    nom_str = str(nom).strip()
    # Chercher une correspondance exacte
    if nom_str in TRADUCTION_MODULES:
        return TRADUCTION_MODULES[nom_str]
    # Chercher une correspondance partielle
    for ar, fr in TRADUCTION_MODULES.items():
        if ar in nom_str or nom_str in ar:
            return fr
    # Si le nom contient des caractères arabes, retourner un placeholder
    if any('\u0600' <= c <= '\u06FF' for c in nom_str):
        return f'Module ({nom_str[:10]}...)'
    return nom_str

# Styles personnalisés - Design professionnel moderne
def get_custom_styles():
    styles = getSampleStyleSheet()
    
    # Couleurs professionnelles
    PRIMARY_BLUE = colors.HexColor('#1e3a8a')
    SECONDARY_BLUE = colors.HexColor('#3b82f6')
    DARK_TEXT = colors.HexColor('#1e293b')
    LIGHT_TEXT = colors.HexColor('#64748b')
    SUCCESS_GREEN = colors.HexColor('#059669')
    WARNING_ORANGE = colors.HexColor('#d97706')
    DANGER_RED = colors.HexColor('#dc2626')
    
    styles.add(ParagraphStyle(
        name='TitleMain',
        parent=styles['Title'],
        fontSize=28,
        textColor=PRIMARY_BLUE,
        spaceAfter=8,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=32
    ))
    
    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=LIGHT_TEXT,
        spaceAfter=25,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=PRIMARY_BLUE,
        spaceBefore=25,
        spaceAfter=12,
        fontName='Helvetica-Bold',
        leftIndent=0,
        borderPadding=0
    ))
    
    styles.add(ParagraphStyle(
        name='BodyTextCustom',
        parent=styles['BodyText'],
        fontSize=10,
        leading=16,
        spaceAfter=8,
        textColor=DARK_TEXT,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='AlertRed',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=DANGER_RED,
        backColor=colors.HexColor('#fef2f2'),
        borderColor=DANGER_RED,
        borderWidth=1,
        borderPadding=10,
        borderRadius=4,
        spaceBefore=12,
        spaceAfter=12,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='AlertGreen',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=SUCCESS_GREEN,
        backColor=colors.HexColor('#ecfdf5'),
        borderColor=SUCCESS_GREEN,
        borderWidth=1,
        borderPadding=10,
        borderRadius=4,
        spaceBefore=12,
        spaceAfter=12,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='AlertOrange',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=WARNING_ORANGE,
        backColor=colors.HexColor('#fffbeb'),
        borderColor=WARNING_ORANGE,
        borderWidth=1,
        borderPadding=10,
        spaceBefore=12,
        spaceAfter=12,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=LIGHT_TEXT,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    ))
    
    styles.add(ParagraphStyle(
        name='StatValue',
        parent=styles['Normal'],
        fontSize=24,
        textColor=PRIMARY_BLUE,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=4
    ))
    
    styles.add(ParagraphStyle(
        name='StatLabel',
        parent=styles['Normal'],
        fontSize=9,
        textColor=LIGHT_TEXT,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    return styles


def create_header_banner():
    """Cree une banniere d'en-tete professionnelle"""
    from reportlab.graphics.shapes import Drawing, Rect, String
    
    d = Drawing(500, 60)
    # Bande bleue en haut
    d.add(Rect(0, 0, 500, 60, fillColor=colors.HexColor('#1e3a8a'), strokeColor=None))
    # Bande claire en bas
    d.add(Rect(0, 0, 500, 4, fillColor=colors.HexColor('#3b82f6'), strokeColor=None))
    return d


def generate_header(title, subtitle=None):
    """Genere l'en-tete du rapport avec design professionnel"""
    styles = get_custom_styles()
    elements = []
    
    # Banniere
    elements.append(create_header_banner())
    elements.append(Spacer(1, 15))
    
    # Logo/Titre institution
    elements.append(Paragraph("UNIVERSITE - FACULTE DE GENIE ELECTRIQUE ET ELECTRONIQUE", styles['FooterStyle']))
    elements.append(Spacer(1, 8))
    
    # Titre principal
    elements.append(Paragraph("Systeme de Soutien Pedagogique", styles['TitleMain']))
    elements.append(Paragraph(title, styles['Subtitle']))
    
    if subtitle:
        elements.append(Paragraph(subtitle, styles['BodyTextCustom']))
    
    # Ligne de separation
    elements.append(Spacer(1, 5))
    
    # Date de generation
    date_str = datetime.now().strftime("%d/%m/%Y a %H:%M")
    elements.append(Paragraph(f"Rapport genere le {date_str}", styles['FooterStyle']))
    elements.append(Spacer(1, 25))
    
    return elements


def create_stat_box(value, label, color=None):
    """Cree une boite de statistique stylisee"""
    if color is None:
        color = colors.HexColor('#1e3a8a')
    
    data = [[value], [label]]
    t = Table(data, colWidths=[4*cm])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 22),
        ('TEXTCOLOR', (0, 0), (0, 0), color),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (0, 1), 9),
        ('TEXTCOLOR', (0, 1), (0, 1), colors.HexColor('#64748b')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    return t


def get_professional_table_style(header_color=None):
    """Retourne un style de tableau professionnel"""
    if header_color is None:
        header_color = colors.HexColor('#1e3a8a')
    
    return TableStyle([
        # En-tete
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        # Corps
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        # Lignes alternees
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        # Bordures
        ('LINEBELOW', (0, 0), (-1, 0), 2, header_color),
        ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.HexColor('#e2e8f0')),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        # Bordure exterieure
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
    ])


def create_bar_chart(data, labels, title="", width=400, height=200):
    """
    Cree un graphique en barres professionnel
    data: liste de valeurs
    labels: liste de labels pour chaque barre
    """
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.legends import Legend
    from reportlab.graphics.shapes import Drawing, String
    
    drawing = Drawing(width, height + 40)
    
    # Titre du graphique
    if title:
        drawing.add(String(width/2, height + 25, title, 
                          textAnchor='middle', 
                          fontSize=11, 
                          fontName='Helvetica-Bold',
                          fillColor=colors.HexColor('#1e3a8a')))
    
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 30
    bc.height = height - 40
    bc.width = width - 80
    bc.data = [data]
    bc.strokeColor = None
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = max(data) * 1.2 if data else 100
    bc.valueAxis.valueStep = max(data) // 5 if data and max(data) > 5 else 10
    bc.valueAxis.labels.fontSize = 8
    bc.valueAxis.labels.fontName = 'Helvetica'
    bc.valueAxis.strokeColor = colors.HexColor('#e2e8f0')
    bc.valueAxis.gridStrokeColor = colors.HexColor('#f1f5f9')
    bc.valueAxis.gridStrokeWidth = 0.5
    bc.valueAxis.visibleGrid = True
    
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = -5
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.labels.fontSize = 8
    bc.categoryAxis.labels.fontName = 'Helvetica'
    bc.categoryAxis.categoryNames = labels
    bc.categoryAxis.strokeColor = colors.HexColor('#e2e8f0')
    
    # Couleurs des barres - degradé bleu
    bc.bars[0].fillColor = colors.HexColor('#3b82f6')
    bc.bars[0].strokeColor = colors.HexColor('#1d4ed8')
    bc.bars[0].strokeWidth = 1
    
    # Barres arrondies (simule avec strokeWidth)
    bc.barWidth = 0.7
    bc.groupSpacing = 10
    
    drawing.add(bc)
    return drawing


def create_pie_chart(data, labels, chart_colors=None, title="", width=300, height=200):
    """
    Cree un graphique en camembert professionnel
    data: liste de valeurs
    labels: liste de labels
    chart_colors: liste de couleurs (optionnel)
    """
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.legends import Legend
    from reportlab.graphics.shapes import Drawing, String
    
    drawing = Drawing(width, height + 30)
    
    # Titre
    if title:
        drawing.add(String(width/2, height + 15, title,
                          textAnchor='middle',
                          fontSize=11,
                          fontName='Helvetica-Bold',
                          fillColor=colors.HexColor('#1e3a8a')))
    
    pie = Pie()
    pie.x = 30
    pie.y = 20
    pie.width = 120
    pie.height = 120
    pie.data = data
    pie.labels = None  # On utilise la legende
    pie.slices.strokeWidth = 1
    pie.slices.strokeColor = colors.white
    
    # Couleurs par defaut
    if chart_colors is None:
        chart_colors = [
            colors.HexColor('#3b82f6'),  # Bleu
            colors.HexColor('#10b981'),  # Vert
            colors.HexColor('#f59e0b'),  # Orange
            colors.HexColor('#ef4444'),  # Rouge
            colors.HexColor('#8b5cf6'),  # Violet
            colors.HexColor('#06b6d4'),  # Cyan
            colors.HexColor('#ec4899'),  # Rose
        ]
    
    for i, color in enumerate(chart_colors[:len(data)]):
        pie.slices[i].fillColor = color
        pie.slices[i].popout = 3 if i == 0 else 0  # Premier segment ressort
    
    drawing.add(pie)
    
    # Legende
    legend = Legend()
    legend.x = 170
    legend.y = height - 40
    legend.dx = 8
    legend.dy = 8
    legend.fontName = 'Helvetica'
    legend.fontSize = 8
    legend.boxAnchor = 'nw'
    legend.columnMaximum = 10
    legend.strokeWidth = 0.5
    legend.strokeColor = colors.HexColor('#e2e8f0')
    legend.deltax = 75
    legend.deltay = 12
    legend.autoXPadding = 5
    legend.yGap = 0
    legend.dxTextSpace = 5
    legend.alignment = 'right'
    legend.dividerLines = 1|2|4
    legend.dividerOffsY = 4.5
    legend.subCols.rpad = 30
    
    # Items de la legende avec pourcentages
    total = sum(data) if data else 1
    legend_items = []
    for i, (label, value) in enumerate(zip(labels, data)):
        pct = (value / total * 100) if total > 0 else 0
        legend_items.append((chart_colors[i % len(chart_colors)], f"{label}: {pct:.1f}%"))
    
    legend.colorNamePairs = legend_items
    drawing.add(legend)
    
    return drawing


def create_horizontal_bar_chart(data, labels, chart_colors=None, title="", width=450, height=180):
    """
    Cree un graphique en barres horizontales (utile pour les comparaisons)
    """
    from reportlab.graphics.charts.barcharts import HorizontalBarChart
    from reportlab.graphics.shapes import Drawing, String
    
    drawing = Drawing(width, height + 30)
    
    if title:
        drawing.add(String(width/2, height + 15, title,
                          textAnchor='middle',
                          fontSize=11,
                          fontName='Helvetica-Bold',
                          fillColor=colors.HexColor('#1e3a8a')))
    
    bc = HorizontalBarChart()
    bc.x = 80
    bc.y = 20
    bc.height = height - 30
    bc.width = width - 120
    bc.data = [data]
    bc.strokeColor = None
    
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = max(data) * 1.15 if data else 100
    bc.valueAxis.labels.fontSize = 8
    bc.valueAxis.strokeColor = colors.HexColor('#e2e8f0')
    
    bc.categoryAxis.labels.fontSize = 8
    bc.categoryAxis.labels.dx = -5
    bc.categoryAxis.categoryNames = labels
    bc.categoryAxis.strokeColor = colors.HexColor('#e2e8f0')
    
    # Couleurs
    if chart_colors is None:
        chart_colors = [colors.HexColor('#3b82f6')]
    
    bc.bars[0].fillColor = chart_colors[0]
    bc.barWidth = 0.8
    
    drawing.add(bc)
    return drawing


def create_progress_bars(data_dict, title="", width=400, height=None):
    """
    Cree des barres de progression stylisees
    data_dict: {label: (value, max_value, color)}
    """
    from reportlab.graphics.shapes import Drawing, Rect, String
    
    bar_height = 18
    spacing = 8
    if height is None:
        height = len(data_dict) * (bar_height + spacing + 20) + 40
    
    drawing = Drawing(width, height)
    
    if title:
        drawing.add(String(width/2, height - 15, title,
                          textAnchor='middle',
                          fontSize=11,
                          fontName='Helvetica-Bold',
                          fillColor=colors.HexColor('#1e3a8a')))
    
    y_pos = height - 50
    for label, (value, max_val, color) in data_dict.items():
        # Label
        drawing.add(String(5, y_pos + 5, label,
                          textAnchor='start',
                          fontSize=9,
                          fontName='Helvetica',
                          fillColor=colors.HexColor('#475569')))
        
        # Valeur
        pct = (value / max_val * 100) if max_val > 0 else 0
        drawing.add(String(width - 5, y_pos + 5, f"{pct:.1f}%",
                          textAnchor='end',
                          fontSize=9,
                          fontName='Helvetica-Bold',
                          fillColor=color))
        
        y_pos -= 15
        
        # Barre de fond
        bar_width = width - 20
        drawing.add(Rect(10, y_pos, bar_width, bar_height,
                        fillColor=colors.HexColor('#e2e8f0'),
                        strokeColor=None,
                        rx=4, ry=4))
        
        # Barre de progression
        progress_width = (value / max_val * bar_width) if max_val > 0 else 0
        if progress_width > 0:
            drawing.add(Rect(10, y_pos, progress_width, bar_height,
                            fillColor=color,
                            strokeColor=None,
                            rx=4, ry=4))
        
        y_pos -= (bar_height + spacing)
    
    return drawing


def generate_student_report(student_id, df):
    """
    Génère un rapport PDF individuel pour un étudiant
    """
    styles = get_custom_styles()
    
    # Filtrer les donnees de l'etudiant
    student_data = df[df['ID'] == str(student_id)]
    
    if len(student_data) == 0:
        print(f"[ERREUR] Etudiant {student_id} non trouve")
        return None
    
    # Informations de base
    filiere = student_data['Filiere'].iloc[0]
    moyenne = student_data['Note_sur_20'].mean()
    nb_modules = len(student_data)
    modules_echec = student_data[student_data['Needs_Support'] == 1]
    taux_echec = len(modules_echec) / nb_modules * 100
    
    # Déterminer le profil
    if moyenne >= 14:
        profil = "Excellence"
        profil_color = colors.HexColor('#16a34a')
    elif moyenne >= 12:
        profil = "Régulier"
        profil_color = colors.HexColor('#22c55e')
    elif moyenne >= 10:
        profil = "En Progression"
        profil_color = colors.HexColor('#eab308')
    elif moyenne >= 7:
        profil = "En Difficulté"
        profil_color = colors.HexColor('#f97316')
    else:
        profil = "À Risque"
        profil_color = colors.HexColor('#dc2626')
    
    # Créer le PDF
    filename = REPORTS_PATH / f"rapport_etudiant_{student_id}.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    
    # En-tête
    elements.extend(generate_header(
        f"Fiche Individuelle - Étudiant {student_id}",
        f"Filière: {filiere}"
    ))
    
    # Section: Resume
    elements.append(Paragraph("RESUME DES PERFORMANCES", styles['SectionTitle']))
    
    summary_data = [
        ['Indicateur', 'Valeur'],
        ['Moyenne Generale', f'{moyenne:.2f}/20'],
        ['Nombre de Modules', str(nb_modules)],
        ['Modules en Difficulte', str(len(modules_echec))],
        ['Taux de Reussite', f'{100-taux_echec:.1f}%'],
        ['Profil Academique', profil]
    ]
    
    summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
    summary_table.setStyle(get_professional_table_style())
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Section: Diagnostic
    elements.append(Paragraph("DIAGNOSTIC", styles['SectionTitle']))
    
    if profil in ["À Risque", "En Difficulté"]:
        elements.append(Paragraph(
            f"<b>ATTENTION:</b> Cet etudiant presente un profil '{profil}' avec une moyenne de {moyenne:.2f}/20. "
            f"Une intervention pedagogique urgente est recommandee.",
            styles['AlertRed']
        ))
    else:
        elements.append(Paragraph(
            f"Cet etudiant presente un profil '{profil}' avec une moyenne de {moyenne:.2f}/20.",
            styles['AlertGreen']
        ))
    
    elements.append(Spacer(1, 15))
    
    # Section: Detail des modules
    elements.append(Paragraph("DETAIL PAR MODULE", styles['SectionTitle']))
    
    modules_data = [['Module', 'Note', 'Statut', 'Soutien']]
    for _, row in student_data.iterrows():
        # Traduire le nom du module
        module_name_traduit = traduire_module(row['Module'])
        module_name = module_name_traduit[:35] + ('...' if len(module_name_traduit) > 35 else '')
        note = f"{row['Note_sur_20']:.1f}/20"
        statut = row['Status']
        soutien = "Oui" if row['Needs_Support'] == 1 else "Non"
        modules_data.append([module_name, note, statut, soutien])
    
    modules_table = Table(modules_data, colWidths=[7*cm, 2.5*cm, 3*cm, 2.5*cm])
    modules_table.setStyle(get_professional_table_style())
    elements.append(modules_table)
    elements.append(Spacer(1, 20))
    
    # Graphique: Performances par module
    elements.append(Paragraph("VISUALISATION DES PERFORMANCES", styles['SectionTitle']))
    
    # Preparer les donnees pour le graphique
    chart_notes = []
    chart_labels = []
    for _, row in student_data.iterrows():
        module_court = traduire_module(row['Module'])[:12]
        chart_labels.append(module_court)
        chart_notes.append(float(row['Note_sur_20']))
    
    # Limiter a 6 modules pour lisibilite
    if len(chart_notes) > 6:
        chart_notes = chart_notes[:6]
        chart_labels = chart_labels[:6]
    
    if chart_notes:
        # Creer un conteneur centre pour le graphique
        bar_chart = create_bar_chart(
            chart_notes, 
            chart_labels, 
            title="Notes par Module (/20)",
            width=420,
            height=160
        )
        # Centrer le graphique dans un tableau
        chart_table = Table([[bar_chart]], colWidths=[14*cm])
        chart_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(chart_table)
        elements.append(Spacer(1, 20))
    
    # Section: Recommandations
    elements.append(Paragraph("RECOMMANDATIONS", styles['SectionTitle']))
    
    recommandations = []
    if profil == "À Risque":
        recommandations = [
            "• Convocation urgente par le conseiller pédagogique",
            "• Tutorat individuel (minimum 2h/semaine)",
            "• Contrat pédagogique personnalisé",
            "• Suivi psychologique si nécessaire"
        ]
    elif profil == "En Difficulté":
        recommandations = [
            "• Inscription obligatoire aux TD de soutien",
            "• Groupes de travail dirigés",
            "• Suivi bi-hebdomadaire par le tuteur"
        ]
    elif profil == "En Progression":
        recommandations = [
            "• Sessions de révision recommandées",
            "• Auto-évaluation régulière",
            "• Permanences des enseignants"
        ]
    else:
        recommandations = [
            "• Continuer les efforts actuels",
            "• Ressources complémentaires disponibles",
            "• Possibilité de devenir tuteur pair"
        ]
    
    for rec in recommandations:
        elements.append(Paragraph(rec, styles['BodyTextCustom']))
    
    # Generer le PDF
    doc.build(elements)
    print(f"[OK] Rapport genere: {filename}")
    
    return filename


def generate_filiere_report(filiere, df):
    """
    Genere un rapport PDF pour une filiere
    """
    styles = get_custom_styles()
    
    filiere_data = df[df['Filiere'] == filiere]
    
    if len(filiere_data) == 0:
        print(f"[ERREUR] Filiere {filiere} non trouvee")
        return None
    
    # Statistiques
    nb_etudiants = filiere_data['ID'].nunique()
    nb_modules = filiere_data['Module'].nunique()
    moyenne = filiere_data['Note_sur_20'].mean()
    taux_echec = filiere_data['Needs_Support'].mean() * 100
    
    # Créer le PDF
    filename = REPORTS_PATH / f"rapport_filiere_{filiere}.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    
    # En-tête
    elements.extend(generate_header(
        f"Rapport de la Filière {filiere}",
        f"Analyse des performances et besoins de soutien"
    ))
    
    # Section: Statistiques generales
    elements.append(Paragraph("STATISTIQUES GENERALES", styles['SectionTitle']))
    
    stats_data = [
        ['Indicateur', 'Valeur'],
        ['Nombre d\'étudiants', f'{nb_etudiants:,}'],
        ['Nombre de modules', str(nb_modules)],
        ['Moyenne générale', f'{moyenne:.2f}/20'],
        ['Taux de besoin de soutien', f'{taux_echec:.1f}%'],
        ['Étudiants nécessitant un soutien', f'{int(nb_etudiants * taux_echec / 100):,}']
    ]
    
    stats_table = Table(stats_data, colWidths=[8*cm, 6*cm])
    stats_table.setStyle(get_professional_table_style())
    elements.append(stats_table)
    elements.append(Spacer(1, 20))
    
    # Section: Modules critiques
    elements.append(Paragraph("MODULES CRITIQUES (Taux d'echec > 50%)", styles['SectionTitle']))
    
    modules_stats = filiere_data.groupby('Module').agg({
        'Note_sur_20': 'mean',
        'Needs_Support': 'mean',
        'ID': 'count'
    }).reset_index()
    modules_stats.columns = ['Module', 'Moyenne', 'Taux_Echec', 'Effectif']
    modules_stats['Taux_Echec'] = modules_stats['Taux_Echec'] * 100
    modules_critiques = modules_stats[modules_stats['Taux_Echec'] >= 50].sort_values('Taux_Echec', ascending=False)
    
    if len(modules_critiques) > 0:
        critical_data = [['Module', 'Moyenne', 'Taux Echec', 'Effectif']]
        for _, row in modules_critiques.head(10).iterrows():
            # Traduire le nom du module
            module_name_traduit = traduire_module(row['Module'])
            module_name = module_name_traduit[:30] + ('...' if len(module_name_traduit) > 30 else '')
            critical_data.append([
                module_name,
                f"{row['Moyenne']:.1f}/20",
                f"{row['Taux_Echec']:.1f}%",
                str(int(row['Effectif']))
            ])
        
        critical_table = Table(critical_data, colWidths=[6*cm, 2.5*cm, 3*cm, 2.5*cm])
        critical_table.setStyle(get_professional_table_style(colors.HexColor('#dc2626')))
        elements.append(critical_table)
    else:
        elements.append(Paragraph("Aucun module avec un taux d'echec superieur a 50%", styles['AlertGreen']))
    
    elements.append(Spacer(1, 20))
    
    # Section: Repartition par profil
    elements.append(Paragraph("REPARTITION DES ETUDIANTS PAR PROFIL", styles['SectionTitle']))
    
    student_avg = filiere_data.groupby('ID')['Note_sur_20'].mean().reset_index()
    
    def get_profil(moy):
        if moy >= 14: return "Excellence"
        elif moy >= 12: return "Régulier"
        elif moy >= 10: return "En Progression"
        elif moy >= 7: return "En Difficulté"
        else: return "À Risque"
    
    student_avg['Profil'] = student_avg['Note_sur_20'].apply(get_profil)
    profils_count = student_avg['Profil'].value_counts()
    
    profils_data = [['Profil', 'Nombre', 'Pourcentage']]
    for profil in ["Excellence", "Régulier", "En Progression", "En Difficulté", "À Risque"]:
        count = profils_count.get(profil, 0)
        pct = count / nb_etudiants * 100
        profils_data.append([profil, str(count), f"{pct:.1f}%"])
    
    profils_table = Table(profils_data, colWidths=[5*cm, 4*cm, 4*cm])
    profils_table.setStyle(get_professional_table_style())
    elements.append(profils_table)
    elements.append(Spacer(1, 15))
    
    # Graphique: Camembert de repartition des profils
    elements.append(Paragraph("VISUALISATION: Repartition des Profils", styles['SectionTitle']))
    
    pie_data = []
    pie_labels = []
    pie_colors_list = [
        colors.HexColor('#16a34a'),  # Excellence - vert fonce
        colors.HexColor('#22c55e'),  # Regulier - vert
        colors.HexColor('#eab308'),  # En Progression - jaune
        colors.HexColor('#f97316'),  # En Difficulte - orange
        colors.HexColor('#dc2626'),  # A Risque - rouge
    ]
    
    for profil in ["Excellence", "Régulier", "En Progression", "En Difficulté", "À Risque"]:
        count = profils_count.get(profil, 0)
        if count > 0:
            pie_data.append(count)
            pie_labels.append(profil)
    
    if pie_data:
        pie_chart = create_pie_chart(
            pie_data,
            pie_labels,
            chart_colors=pie_colors_list[:len(pie_data)],
            title="Distribution des Profils Academiques",
            width=420,
            height=180
        )
        # Centrer le graphique
        chart_table = Table([[pie_chart]], colWidths=[14*cm])
        chart_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(chart_table)
        elements.append(Spacer(1, 20))
    
    # Graphique: Barres pour les modules critiques (top 5)
    if len(modules_critiques) > 0:
        elements.append(Paragraph("VISUALISATION: Modules les Plus Critiques", styles['SectionTitle']))
        
        top_modules = modules_critiques.head(5)
        bar_data = top_modules['Taux_Echec'].tolist()
        bar_labels = [traduire_module(m)[:10] for m in top_modules['Module'].tolist()]
        
        bar_chart = create_bar_chart(
            bar_data,
            bar_labels,
            title="Taux d'Echec par Module (%)",
            width=400,
            height=150
        )
        # Centrer le graphique
        chart_table2 = Table([[bar_chart]], colWidths=[14*cm])
        chart_table2.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef2f2')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#fecaca')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(chart_table2)
        elements.append(Spacer(1, 20))
    
    # Section: Plan d'action
    elements.append(Paragraph("PLAN D'ACTION RECOMMANDE", styles['SectionTitle']))
    
    risque_count = profils_count.get("À Risque", 0)
    difficulte_count = profils_count.get("En Difficulté", 0)
    
    actions = [
        f"• Convoquer les {risque_count} étudiants à risque pour un entretien individuel",
        f"• Inscrire les {difficulte_count} étudiants en difficulté aux TD de soutien",
        f"• Ouvrir des sessions de soutien pour les {len(modules_critiques)} modules critiques",
        f"• Affecter {max(1, (risque_count + difficulte_count) // 15)} tuteurs pour cette filière",
        "• Mettre en place un suivi hebdomadaire des étudiants prioritaires"
    ]
    
    for action in actions:
        elements.append(Paragraph(action, styles['BodyTextCustom']))
    
    # Generer le PDF
    doc.build(elements)
    print(f"[OK] Rapport genere: {filename}")
    
    return filename


def generate_global_report(df):
    """
    Genere un rapport PDF global pour l'administration
    """
    styles = get_custom_styles()
    
    # Créer le PDF
    filename = REPORTS_PATH / "rapport_global_administration.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    
    # En-tête
    elements.extend(generate_header(
        "Rapport Global - Administration",
        "Vue d'ensemble du système de soutien pédagogique"
    ))
    
    # Statistiques globales
    nb_total = len(df)
    nb_etudiants = df['ID'].nunique()
    nb_modules = df['Module'].nunique()
    nb_filieres = df['Filiere'].nunique()
    moyenne_globale = df['Note_sur_20'].mean()
    taux_soutien = df['Needs_Support'].mean() * 100
    
    elements.append(Paragraph("VUE D'ENSEMBLE", styles['SectionTitle']))
    
    global_data = [
        ['Indicateur', 'Valeur'],
        ['Total des inscriptions', f'{nb_total:,}'],
        ['Étudiants uniques', f'{nb_etudiants:,}'],
        ['Modules', str(nb_modules)],
        ['Filières', str(nb_filieres)],
        ['Moyenne générale', f'{moyenne_globale:.2f}/20'],
        ['Taux de besoin de soutien', f'{taux_soutien:.1f}%']
    ]
    
    global_table = Table(global_data, colWidths=[8*cm, 6*cm])
    global_table.setStyle(get_professional_table_style())
    elements.append(global_table)
    elements.append(Spacer(1, 25))
    
    # Statistiques par filiere
    elements.append(Paragraph("PERFORMANCE PAR FILIERE", styles['SectionTitle']))
    
    filiere_stats = df.groupby('Filiere').agg({
        'ID': 'nunique',
        'Note_sur_20': 'mean',
        'Needs_Support': 'mean'
    }).reset_index()
    filiere_stats.columns = ['Filière', 'Étudiants', 'Moyenne', 'Taux_Soutien']
    filiere_stats = filiere_stats.sort_values('Taux_Soutien', ascending=False)
    
    filiere_data = [['Filiere', 'Etudiants', 'Moyenne', 'Taux Soutien', 'Statut']]
    for _, row in filiere_stats.iterrows():
        taux = row['Taux_Soutien'] * 100
        if taux >= 60:
            statut = "CRITIQUE"
        elif taux >= 45:
            statut = "ATTENTION"
        else:
            statut = "NORMAL"
        
        filiere_data.append([
            row['Filière'],
            str(row['Étudiants']),
            f"{row['Moyenne']:.1f}/20",
            f"{taux:.1f}%",
            statut
        ])
    
    filiere_table = Table(filiere_data, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 3*cm, 3*cm])
    filiere_table.setStyle(get_professional_table_style())
    elements.append(filiere_table)
    elements.append(Spacer(1, 20))
    
    # Graphique: Barres pour moyennes par filiere
    elements.append(Paragraph("VISUALISATION: Moyennes par Filiere", styles['SectionTitle']))
    
    bar_moyennes = filiere_stats['Moyenne'].tolist()
    bar_filieres = filiere_stats['Filière'].tolist()
    
    # Limiter a 8 filieres pour lisibilite
    if len(bar_moyennes) > 8:
        bar_moyennes = bar_moyennes[:8]
        bar_filieres = bar_filieres[:8]
    
    if bar_moyennes:
        filiere_bar_chart = create_bar_chart(
            bar_moyennes,
            bar_filieres,
            title="Moyenne Generale par Filiere (/20)",
            width=420,
            height=160
        )
        # Conteneur stylise pour le graphique
        chart_container = Table([[filiere_bar_chart]], colWidths=[14*cm])
        chart_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bae6fd')),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(chart_container)
        elements.append(Spacer(1, 20))
    
    # Graphique: Camembert pour repartition globale des profils
    elements.append(Paragraph("VISUALISATION: Repartition Globale des Profils", styles['SectionTitle']))
    
    student_avg_global = df.groupby('ID')['Note_sur_20'].mean().reset_index()
    
    def get_profil_global(moy):
        if moy >= 14: return "Excellence"
        elif moy >= 12: return "Regulier"
        elif moy >= 10: return "En Progression"
        elif moy >= 7: return "En Difficulte"
        else: return "A Risque"
    
    student_avg_global['Profil'] = student_avg_global['Note_sur_20'].apply(get_profil_global)
    profils_global = student_avg_global['Profil'].value_counts()
    
    pie_data_global = []
    pie_labels_global = []
    pie_colors_global = [
        colors.HexColor('#16a34a'),  # Excellence
        colors.HexColor('#22c55e'),  # Regulier
        colors.HexColor('#eab308'),  # En Progression
        colors.HexColor('#f97316'),  # En Difficulte
        colors.HexColor('#dc2626'),  # A Risque
    ]
    
    for i, profil in enumerate(["Excellence", "Regulier", "En Progression", "En Difficulte", "A Risque"]):
        count = profils_global.get(profil, 0)
        if count > 0:
            pie_data_global.append(count)
            pie_labels_global.append(profil)
    
    if pie_data_global:
        global_pie_chart = create_pie_chart(
            pie_data_global,
            pie_labels_global,
            chart_colors=pie_colors_global[:len(pie_data_global)],
            title="Distribution Globale des Profils Academiques",
            width=420,
            height=180
        )
        # Conteneur stylise
        pie_container = Table([[global_pie_chart]], colWidths=[14*cm])
        pie_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(pie_container)
        elements.append(Spacer(1, 25))
    
    # Etudiants prioritaires
    elements.append(Paragraph("ETUDIANTS PRIORITAIRES", styles['SectionTitle']))
    
    student_avg = df.groupby('ID').agg({
        'Note_sur_20': 'mean',
        'Filiere': 'first',
        'Needs_Support': 'sum',
        'Module': 'count'
    }).reset_index()
    student_avg.columns = ['ID', 'Moyenne', 'Filiere', 'Modules_Echec', 'Total_Modules']
    
    critiques = student_avg[student_avg['Moyenne'] < 7].sort_values('Moyenne')
    
    elements.append(Paragraph(
        f"<b>{len(critiques)} etudiants a risque critique</b> (moyenne < 7/20) necessitent une intervention urgente.",
        styles['AlertRed']
    ))
    
    if len(critiques) > 0:
        crit_data = [['ID', 'Filière', 'Moyenne', 'Modules Échec']]
        for _, row in critiques.head(15).iterrows():
            crit_data.append([
                str(row['ID']),
                row['Filiere'],
                f"{row['Moyenne']:.1f}/20",
                f"{int(row['Modules_Echec'])}/{int(row['Total_Modules'])}"
            ])
        
        crit_table = Table(crit_data, colWidths=[3.5*cm, 3*cm, 3*cm, 4*cm])
        crit_table.setStyle(get_professional_table_style(colors.HexColor('#dc2626')))
        elements.append(crit_table)
    
    elements.append(Spacer(1, 25))
    
    # Ressources necessaires
    elements.append(Paragraph("RESSOURCES NECESSAIRES", styles['SectionTitle']))
    
    nb_critiques = len(critiques)
    nb_difficulte = len(student_avg[(student_avg['Moyenne'] >= 7) & (student_avg['Moyenne'] < 10)])
    nb_progression = len(student_avg[(student_avg['Moyenne'] >= 10) & (student_avg['Moyenne'] < 12)])
    tuteurs_necessaires = max(1, (nb_critiques + nb_difficulte) // 15)
    
    # Tableau des ressources
    ressources_data = [
        ['Ressource', 'Quantite', 'Details'],
        ['Tuteurs necessaires', str(tuteurs_necessaires), 'Ratio 1 tuteur pour 15 etudiants'],
        ['Etudiants a convoquer (urgence)', str(nb_critiques), 'Moyenne < 7/20'],
        ['Etudiants pour TD soutien', str(nb_difficulte), 'Moyenne entre 7 et 10/20'],
        ['Modules a couvrir', str(df['Module'].nunique()), 'Sessions de soutien'],
        ['Budget mensuel estime', f'{tuteurs_necessaires * 200} DH', 'Base 200 DH/tuteur/mois']
    ]
    
    ressources_table = Table(ressources_data, colWidths=[5.5*cm, 3*cm, 5.5*cm])
    ressources_table.setStyle(get_professional_table_style(colors.HexColor('#059669')))
    elements.append(ressources_table)
    elements.append(Spacer(1, 20))
    
    # Graphique: Repartition des besoins de soutien
    elements.append(Paragraph("VISUALISATION: Repartition des Besoins de Soutien", styles['SectionTitle']))
    
    # Donnees pour le camembert des ressources
    ressources_pie_data = [nb_critiques, nb_difficulte, nb_progression]
    ressources_pie_labels = ['A Risque (urgent)', 'En Difficulte', 'En Progression']
    ressources_pie_colors = [
        colors.HexColor('#dc2626'),  # Rouge - urgent
        colors.HexColor('#f97316'),  # Orange - difficulte
        colors.HexColor('#eab308'),  # Jaune - progression
    ]
    
    # Filtrer les valeurs nulles
    filtered_data = []
    filtered_labels = []
    filtered_colors = []
    for d, l, c in zip(ressources_pie_data, ressources_pie_labels, ressources_pie_colors):
        if d > 0:
            filtered_data.append(d)
            filtered_labels.append(l)
            filtered_colors.append(c)
    
    if filtered_data:
        ressources_pie = create_pie_chart(
            filtered_data,
            filtered_labels,
            chart_colors=filtered_colors,
            title="Etudiants Necessitant un Accompagnement",
            width=400,
            height=170
        )
        # Conteneur stylise
        ressources_container = Table([[ressources_pie]], colWidths=[14*cm])
        ressources_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef3c7')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#fbbf24')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(ressources_container)
        elements.append(Spacer(1, 15))
    
    # Graphique en barres horizontales pour la charge de travail
    elements.append(Paragraph("VISUALISATION: Charge de Travail par Type d'Intervention", styles['SectionTitle']))
    
    intervention_data = [
        nb_critiques * 2,  # 2h/semaine par etudiant critique
        nb_difficulte * 1,  # 1h/semaine par etudiant en difficulte
        nb_progression * 0.5  # 0.5h/semaine par etudiant en progression
    ]
    intervention_labels = ['Tutorat individuel', 'TD de soutien', 'Suivi leger']
    
    if sum(intervention_data) > 0:
        intervention_bar = create_horizontal_bar_chart(
            intervention_data,
            intervention_labels,
            title="Heures de Soutien Hebdomadaires Estimees",
            width=420,
            height=140
        )
        # Conteneur
        intervention_container = Table([[intervention_bar]], colWidths=[14*cm])
        intervention_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecfdf5')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#6ee7b7')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(intervention_container)
        elements.append(Spacer(1, 15))
    
    # Resume des actions recommandees
    elements.append(Paragraph("RESUME DES ACTIONS", styles['SectionTitle']))
    
    actions = [
        f"1. Recruter {tuteurs_necessaires} tuteurs pour assurer le ratio 1:15",
        f"2. Convoquer en urgence les {nb_critiques} etudiants a risque critique",
        f"3. Organiser les TD de soutien pour {nb_difficulte} etudiants en difficulte",
        f"4. Prevoir un budget mensuel de {tuteurs_necessaires * 200} DH"
    ]
    
    for action in actions:
        elements.append(Paragraph(action, styles['BodyTextCustom']))
    
    # Generer le PDF
    doc.build(elements)
    print(f"[OK] Rapport global genere: {filename}")

    return filename
def generate_all_reports():
    """
    Génère tous les rapports PDF
    """
    print("=" * 60)
    print("GENERATION DES RAPPORTS PDF")
    print("=" * 60)
    
    # Charger les donnees
    RAW_PATH = Path("raw")
    df1 = pd.read_csv(RAW_PATH / "1- one_clean.csv", encoding='utf-8')
    df2 = pd.read_csv(RAW_PATH / "2- two_clean.csv", encoding='utf-8')
    df = pd.concat([df1, df2], ignore_index=True)
    
    # Nettoyage
    df['ID'] = df['ID'].astype(str)
    df = df[~df['ID'].isin(['Unknown', 'unknown', 'nan', 'None', ''])].copy()
    df = df[~df['Major'].astype(str).str.lower().str.contains('unknown', na=False)].copy()
    df = df[~df['Subject'].astype(str).str.lower().str.contains('unknown', na=False)].copy()
    
    df = df.rename(columns={
        'Major': 'Filiere',
        'Subject': 'Module',
        'MajorYear': 'Annee',
        'OfficalYear': 'AnneUniversitaire'
    })
    
    df['Practical'] = pd.to_numeric(df['Practical'], errors='coerce').fillna(0)
    df['Theoretical'] = pd.to_numeric(df['Theoretical'], errors='coerce').fillna(0)
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(df['Practical'] + df['Theoretical'])
    df['Note_sur_20'] = df['Total'] / 5
    df['Needs_Support'] = ((df['Status'] == 'Fail') | 
                           (df['Total'] < 50) | 
                           (df['Status'].isin(['Absent', 'Debarred', 'Withdrawal']))).astype(int)
    
    print(f"\n[INFO] Donnees chargees: {len(df):,} enregistrements")
    
    # 1. Rapport global
    print("\n[GENERATION] Rapport global...")
    generate_global_report(df)
    
    # 2. Rapports par filiere
    print("\n[GENERATION] Rapports par filiere...")
    for filiere in df['Filiere'].unique():
        generate_filiere_report(filiere, df)
    
    # 3. Exemple de rapports etudiants (10 premiers)
    print("\n[GENERATION] Exemples de rapports etudiants...")
    sample_students = df['ID'].drop_duplicates().head(5).tolist()
    for student_id in sample_students:
        generate_student_report(student_id, df)
    
    print("\n" + "=" * 60)
    print(f"[OK] Tous les rapports generes dans: {REPORTS_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    generate_all_reports()
