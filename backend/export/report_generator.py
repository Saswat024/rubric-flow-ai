"""
Generate evaluation reports in various formats
Supports: PDF, CSV, JSON
"""
import io
import json
import csv
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_pdf_report(evaluation_data: Dict[str, Any], user_email: str) -> bytes:
    """Generate a comprehensive PDF evaluation report"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    elements.append(Paragraph("Evaluation Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Metadata section
    metadata_data = [
        ["Student Email:", user_email],
        ["Evaluation Type:", evaluation_data.get('type', 'N/A').upper()],
        ["Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Overall Score:", f"{evaluation_data.get('total_score', 0)}/100"]
    ]
    
    metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#edf2f7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0'))
    ]))
    
    elements.append(metadata_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Score breakdown section
    elements.append(Paragraph("Score Breakdown", heading_style))
    
    breakdown = evaluation_data.get('breakdown', [])
    breakdown_data = [["Criterion", "Score", "Max Score", "Percentage"]]
    
    for item in breakdown:
        percentage = (item['score'] / item['max_score'] * 100) if item['max_score'] > 0 else 0
        breakdown_data.append([
            item['criterion'],
            str(item['score']),
            str(item['max_score']),
            f"{percentage:.1f}%"
        ])
    
    breakdown_table = Table(breakdown_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
    ]))
    
    elements.append(breakdown_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Detailed feedback section
    elements.append(Paragraph("Detailed Feedback by Criterion", heading_style))
    
    for item in breakdown:
        criterion_title = Paragraph(f"<b>{item['criterion']}</b> ({item['score']}/{item['max_score']})", 
                                   styles['Heading3'])
        elements.append(criterion_title)
        
        feedback_text = item['feedback'].replace('✅', '[+]').replace('⚠️', '[!]').replace('💡', '[*]')
        feedback_para = Paragraph(feedback_text, styles['BodyText'])
        elements.append(feedback_para)
        elements.append(Spacer(1, 0.2*inch))
    
    # General feedback section
    elements.append(PageBreak())
    elements.append(Paragraph("Recommendations for Improvement", heading_style))
    
    feedback_items = evaluation_data.get('feedback', [])
    for i, item in enumerate(feedback_items, 1):
        clean_item = item.replace('✅', '[+]').replace('⚠️', '[!]').replace('💡', '[*]')
        feedback_para = Paragraph(f"{i}. {clean_item}", styles['BodyText'])
        elements.append(feedback_para)
        elements.append(Spacer(1, 0.15*inch))
    
    # Complexity analysis if available
    if 'complexity_analysis' in evaluation_data:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Complexity Analysis", heading_style))
        
        complexity = evaluation_data['complexity_analysis']
        complexity_text = f"""
        <b>Time Complexity:</b> {complexity.get('time_complexity', 'N/A')}<br/>
        <b>Space Complexity:</b> {complexity.get('space_complexity', 'N/A')}
        """
        elements.append(Paragraph(complexity_text, styles['BodyText']))
        
        if complexity.get('optimization_suggestions'):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("<b>Optimization Suggestions:</b>", styles['BodyText']))
            for sugg in complexity['optimization_suggestions']:
                elements.append(Paragraph(f"• {sugg}", styles['BodyText']))
    
    # Build PDF
    doc.build(elements)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def generate_csv_report(evaluations: List[Dict[str, Any]]) -> str:
    """Generate CSV report of multiple evaluations"""
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Date', 'Type', 'Total Score', 
        'Correctness', 'Edge Cases', 'Clarity', 
        'Efficiency', 'Best Practices'
    ])
    
    # Data rows
    for eval_data in evaluations:
        breakdown = {item['criterion']: item['score'] 
                    for item in eval_data.get('breakdown', [])}
        
        writer.writerow([
            eval_data.get('created_at', ''),
            eval_data.get('type', ''),
            eval_data.get('total_score', 0),
            breakdown.get('Correctness & Logic', breakdown.get('Correctness', 0)),
            breakdown.get('Edge Case Handling & Robustness', breakdown.get('Edge Case Handling', 0)),
            breakdown.get('Clarity & Documentation', breakdown.get('Clarity', 0)),
            breakdown.get('Algorithm Efficiency', breakdown.get('Complexity', 0)),
            breakdown.get('Best Practices & Design', 0)
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    return csv_content
