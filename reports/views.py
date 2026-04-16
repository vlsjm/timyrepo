from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime, timedelta, date
from io import BytesIO, StringIO
import csv
import json
from calendar import monthrange
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from logging_app.models import HourLog
from .models import Report
from users.decorators import intern_required
from users.models import CustomUser


def convert_to_12hour(time_obj):
    """Convert time object to 12-hour format with AM/PM."""
    if not time_obj:
        return ''
    if isinstance(time_obj, str):
        try:
            time_obj = datetime.strptime(time_obj, '%H:%M:%S').time()
        except:
            return time_obj
    return time_obj.strftime('%I:%M %p')


@intern_required
def reports_dashboard(request):
    """View reports dashboard and generate new reports."""
    
    # Get user's reports
    user_reports = Report.objects.filter(intern=request.user)
    
    context = {
        'reports': user_reports,
    }
    return render(request, 'reports/dashboard.html', context)


@intern_required
def generate_timesheet(request):
    """Generate a monthly timesheet."""
    
    if request.method == 'POST':
        year = int(request.POST.get('year', date.today().year))
        month = int(request.POST.get('month', date.today().month))
        report_format = request.POST.get('format', 'pdf')
        
        if report_format == 'csv':
            return _generate_timesheet_csv(request.user, year, month)
        elif report_format == 'pdf':
            return _generate_timesheet_pdf(request.user, year, month)
    
    # Get current year and month for defaults
    today = date.today()
    years = list(range(today.year - 5, today.year + 1))
    months = [(i, datetime(today.year, i, 1).strftime('%B')) for i in range(1, 13)]
    
    context = {
        'years': years,
        'months': months,
        'current_year': today.year,
        'current_month': today.month,
    }
    return render(request, 'reports/generate_timesheet.html', context)


def _generate_timesheet_csv(user, year, month):
    """Generate CSV timesheet format."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="timesheet_{year}_{month:02d}.csv"'
    
    writer = csv.writer(response)
    
    # Header info
    writer.writerow(['TIMESHEET'])
    writer.writerow([])
    writer.writerow(['Name:', user.get_full_name()])
    
    # Get user's profile info if available
    try:
        profile = user.internprofile
        writer.writerow(['Department:', profile.department or 'N/A'])
        writer.writerow(['Position:', profile.position or 'N/A'])
    except:
        writer.writerow(['Department:', 'N/A'])
        writer.writerow(['Position:', 'N/A'])
    
    # Month and year
    month_name = datetime(year, month, 1).strftime('%B')
    writer.writerow(['Month:', f'{month_name} {year}'])
    writer.writerow([])
    
    # Get all logs for this month
    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)
    
    logs = HourLog.objects.filter(
        intern=user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    # Create a dictionary for quick lookup
    logs_dict = {log.date: log for log in logs}
    
    # Table headers
    writer.writerow(['Day', 'Date', 'Time In (AM)', 'Time Out (AM)', 'Time In (PM)', 'Time Out (PM)', 'Total Hours', 'Signature'])
    
    # Populate timesheet rows
    total_hours = 0
    for day in range(1, last_day + 1):
        current_date = date(year, month, day)
        log = logs_dict.get(current_date)
        
        if log:
            if log.logging_mode == 'split':
                time_in_am = log.time_in or ''
                time_out_am = log.time_out or ''
                time_in_pm = log.time_in_afternoon or ''
                time_out_pm = log.time_out_afternoon or ''
            else:  # single mode
                time_in_am = log.time_in or ''
                time_out_am = log.time_out or ''
                time_in_pm = ''
                time_out_pm = ''
            
            hours = log.total_hours()
            total_hours += hours
            
            writer.writerow([
                day,
                current_date.strftime('%m/%d/%Y'),
                time_in_am,
                time_out_am,
                time_in_pm,
                time_out_pm,
                round(hours, 2),
                ''
            ])
        else:
            writer.writerow([
                day,
                current_date.strftime('%m/%d/%Y'),
                '', '', '', '',
                '',
                ''
            ])
    
    # Total row
    writer.writerow([])
    writer.writerow(['Total Hours:', '', '', '', '', '', round(total_hours, 2), ''])
    writer.writerow([])
    writer.writerow(["Intern's Signature:", '', 'Date:', ''])
    writer.writerow(["Supervisor's Signature:", '', 'Date:', ''])
    
    return response


def _generate_timesheet_html(user, year, month):
    """Generate HTML timesheet that can be printed."""
    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)
    
    logs = HourLog.objects.filter(
        intern=user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    # Create a dictionary for quick lookup
    logs_dict = {log.date: log for log in logs}
    
    # Get user profile info
    try:
        profile = user.internprofile
        department = profile.department or 'N/A'
        position = profile.position or 'N/A'
    except:
        department = 'N/A'
        position = 'N/A'
    
    # Prepare timesheet data
    month_name = datetime(year, month, 1).strftime('%B')
    timesheet_data = []
    total_hours = 0
    
    for day in range(1, last_day + 1):
        current_date = date(year, month, day)
        log = logs_dict.get(current_date)
        
        if log:
            if log.logging_mode == 'split':
                time_in_am = str(log.time_in or '')
                time_out_am = str(log.time_out or '')
                time_in_pm = str(log.time_in_afternoon or '')
                time_out_pm = str(log.time_out_afternoon or '')
            else:
                time_in_am = str(log.time_in or '')
                time_out_am = str(log.time_out or '')
                time_in_pm = ''
                time_out_pm = ''
            
            hours = log.total_hours()
            total_hours += hours
            
            timesheet_data.append({
                'day': day,
                'time_in_am': time_in_am,
                'time_out_am': time_out_am,
                'time_in_pm': time_in_pm,
                'time_out_pm': time_out_pm,
                'total_hours': round(hours, 2),
            })
        else:
            timesheet_data.append({
                'day': day,
                'time_in_am': '',
                'time_out_am': '',
                'time_in_pm': '',
                'time_out_pm': '',
                'total_hours': '',
            })
    
    context = {
        'user': user,
        'month': month_name,
        'year': year,
        'department': department,
        'position': position,
        'total_hours': round(total_hours, 2),
        'timesheet_data': timesheet_data,
    }
    
    return render(request, 'reports/timesheet_view.html', context)


def _generate_timesheet_pdf(user, year, month):
    """Generate PDF timesheet format using reportlab - A4 landscape with better spacing."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="timesheet_{user.id}_{year}_{month:02d}.pdf"'
    
    # Create PDF document with A4 landscape
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=0.3*inch, bottomMargin=0.3*inch, leftMargin=0.3*inch, rightMargin=0.3*inch)
    story = []
    
    # Get user profile info
    try:
        profile = user.intern_profile
        department = profile.department or 'N/A'
    except:
        department = 'N/A'
    
    # Prepare timesheet data
    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)
    
    logs = HourLog.objects.filter(
        intern=user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    logs_dict = {log.date: log for log in logs}
    month_name = datetime(year, month, 1).strftime('%B')
    
    # Calculate total hours for the entire month
    total_hours_month = 0
    for log in logs:
        total_hours_month += log.total_hours()
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.black,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Helper function to create a page
    def create_page(story, start_day, end_day, is_page2=False):
        # Title
        story.append(Paragraph('INTERNSHIP TIMESHEET', title_style))
        story.append(Spacer(1, 0.05*inch))
        
        # Header Info Table - align with main table columns
        # Columns: Days(0.6) | In AM(1.2) | Out AM(1.2) | In PM(1.2) | Out PM(1.2) | Total(0.9) | Signature(1.2)
        header_data = [
            ['Name:', user.get_full_name(), 'Month:', f'{month_name} {year}', '', ''],
            ['Department:', department, 'Total Hours:', str(round(total_hours_month, 1)), '', ''],
        ]
        
        header_table = Table(header_data, colWidths=[0.6*inch, 3.4*inch, 0.8*inch, 2.8*inch, 0.9*inch, 1.2*inch])
        header_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.05*inch))
        
        # Main timesheet table
        table_data = [
            ['Days', 'In', 'Out', 'In', 'Out', 'Total', 'Signature'],
            ['', 'AM', 'AM', 'PM', 'PM', 'Hours', ''],
        ]
        
        page_total_hours = 0
        for day in range(start_day, end_day + 1):
            current_date = date(year, month, day)
            log = logs_dict.get(current_date)
            
            if log:
                if log.logging_mode == 'split':
                    time_in_am = convert_to_12hour(log.time_in or '')
                    time_out_am = convert_to_12hour(log.time_out or '')
                    time_in_pm = convert_to_12hour(log.time_in_afternoon or '')
                    time_out_pm = convert_to_12hour(log.time_out_afternoon or '')
                else:
                    time_in_am = convert_to_12hour(log.time_in or '')
                    time_out_am = convert_to_12hour(log.time_out or '')
                    time_in_pm = ''
                    time_out_pm = ''
                
                hours = log.total_hours()
                page_total_hours += hours
                
                table_data.append([
                    str(day),
                    time_in_am,
                    time_out_am,
                    time_in_pm,
                    time_out_pm,
                    str(round(hours, 2)),
                    '',
                ])
            else:
                table_data.append([str(day), '', '', '', '', '', ''])
        
        # Add total row
        table_data.append(['', '', '', '', 'TOTAL:', str(round(page_total_hours, 2)), ''])
        
        # Create main table with same column widths for alignment
        timesheet_table = Table(table_data, colWidths=[0.6*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 0.9*inch, 1.2*inch])
        timesheet_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, 1), 'Helvetica-Bold', 11),
            ('FONT', (0, 2), (-1, -2), 'Helvetica', 10),
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 11),
            ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#D3D3D3')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D3D3D3')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('HEIGHT', (0, 2), (-1, -2), 0.35*inch),
            ('HEIGHT', (0, -1), (-1, -1), 0.35*inch),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(timesheet_table)
        story.append(Spacer(1, 0.08*inch))
        
        # Signature section
        sig_data = [
            ["Employee's Signature", 'Date', "Supervisor's Signature", 'Date'],
            ['', '', '', ''],
        ]
        
        sig_table = Table(sig_data, colWidths=[2*inch, 1.3*inch, 2*inch, 1.3*inch])
        sig_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('HEIGHT', (0, 1), (-1, 1), 0.4*inch),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('BOTTOMPADDING', (0, 0), (-1, 1), 4),
        ]))
        
        story.append(sig_table)
        
        return story
    
    # Page 1: Days 1-15
    story = create_page(story, 1, min(15, last_day))
    
    # Add page break if month has more than 15 days
    if last_day > 15:
        story.append(PageBreak())
        # Page 2: Days 16-31
        story = create_page(story, 16, last_day)
    
    # Build PDF
    doc.build(story)
    return response


@login_required
def view_report(request, pk):
    """View a previously generated report."""
    report = get_object_or_404(Report, pk=pk)
    
    if report.intern != request.user and not request.user.is_admin():
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('dashboard')
    
    context = {'report': report}
    return render(request, 'reports/view_report.html', context)


@intern_required
def generate_journal_report(request):
    """Generate a journal report with task descriptions for selected dates."""
    
    if request.method == 'POST':
        # Get filter mode
        filter_mode = request.POST.get('filter_mode', 'range')
        report_format = request.POST.get('format', 'pdf')
        
        # Determine date range based on filter mode
        start_date = None
        end_date = None
        
        if filter_mode == 'single_day':
            single_date = request.POST.get('single_date')
            if not single_date:
                messages.error(request, 'Please select a date.')
                return redirect('reports:generate_journal')
            start_date = single_date
            end_date = single_date
            
        elif filter_mode == 'month':
            year = request.POST.get('year')
            month = request.POST.get('month')
            if not year or not month:
                messages.error(request, 'Please select a month and year.')
                return redirect('reports:generate_journal')
            year = int(year)
            month = int(month)
            _, last_day = monthrange(year, month)
            start_date = date(year, month, 1)
            end_date = date(year, month, last_day)
            
        elif filter_mode == 'range':
            range_start = request.POST.get('range_start')
            range_end = request.POST.get('range_end')
            if not range_start or not range_end:
                messages.error(request, 'Please select both start and end dates.')
                return redirect('reports:generate_journal')
            start_date = range_start
            end_date = range_end
        
        # Get logs for the selected date range
        logs = HourLog.objects.filter(
            intern=request.user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        if not logs.exists():
            messages.warning(request, 'No logs found for the selected date range.')
            return redirect('reports:generate_journal')
        
        if report_format == 'csv':
            return _generate_journal_csv(request.user, logs, start_date, end_date, filter_mode)
        elif report_format == 'pdf':
            return _generate_journal_pdf(request.user, logs, start_date, end_date, filter_mode)
    
    # Get available dates for dropdown and date pickers
    available_dates = HourLog.objects.filter(intern=request.user).values_list('date', flat=True).distinct().order_by('-date')
    
    today = date.today()
    years = list(range(today.year - 5, today.year + 1))
    months = [(i, datetime(today.year, i, 1).strftime('%B')) for i in range(1, 13)]
    
    context = {
        'available_dates': available_dates,
        'years': years,
        'months': months,
        'current_year': today.year,
        'current_month': today.month,
    }
    return render(request, 'reports/generate_journal.html', context)


def _generate_journal_csv(user, logs, start_date, end_date, filter_mode):
    """Generate CSV journal report."""
    response = HttpResponse(content_type='text/csv')
    
    if filter_mode == 'single_day':
        filename = f'journal_{start_date}.csv'
    elif filter_mode == 'month':
        try:
            month_date = datetime.strptime(str(start_date), '%Y-%m-%d')
            filename = f'journal_{month_date.strftime("%B_%Y")}.csv'
        except:
            filename = f'journal_{start_date}_to_{end_date}.csv'
    else:
        filename = f'journal_{start_date}_to_{end_date}.csv'
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(['JOURNAL REPORT - TASK LOG'])
    writer.writerow([])
    writer.writerow(['Employee Name:', user.get_full_name()])
    writer.writerow(['Report Period:', f'{start_date} to {end_date}'])
    writer.writerow([])
    writer.writerow(['Date', 'Day of Week', 'Time In', 'Time Out', 'Total Hours', 'Tasks/Description'])
    
    total_hours = 0
    for log in logs:
        hours = log.total_hours()
        total_hours += hours
        day_of_week = datetime.strptime(str(log.date), '%Y-%m-%d').strftime('%A')
        writer.writerow([
            log.date,
            day_of_week,
            log.time_in,
            log.time_out,
            round(hours, 2),
            log.description
        ])
    
    writer.writerow([])
    writer.writerow(['Total Hours:', '', '', '', round(total_hours, 2), ''])
    
    return response


def _generate_journal_pdf(user, logs, start_date, end_date, filter_mode):
    """Generate PDF journal report with task descriptions."""
    response = HttpResponse(content_type='application/pdf')
    
    if filter_mode == 'single_day':
        filename = f'journal_{start_date}.pdf'
    elif filter_mode == 'month':
        try:
            month_date = datetime.strptime(str(start_date), '%Y-%m-%d')
            filename = f'journal_{month_date.strftime("%B_%Y")}.pdf'
        except:
            filename = f'journal_{start_date}_to_{end_date}.pdf'
    else:
        filename = f'journal_{start_date}_to_{end_date}.pdf'
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, 
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    story = []
    
    # Get user profile info
    try:
        profile = user.intern_profile
        department = profile.department or 'N/A'
        position = getattr(profile, 'position', 'N/A') or 'N/A'
    except:
        department = 'N/A'
        position = 'N/A'
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#003366'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=2,
        fontName='Helvetica'
    )
    
    date_header_style = ParagraphStyle(
        'DateHeader',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#003366'),
        spaceAfter=4,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    task_style = ParagraphStyle(
        'Task',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=6,
        leading=14,
        leftIndent=20
    )
    
    # Title
    story.append(Paragraph('INTERNSHIP JOURNAL REPORT', title_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Header Info
    header_data = [
        ['Name:', user.get_full_name(), 'Department:', department],
        ['Position:', position, 'Report Period:', f'{start_date} to {end_date}'],
    ]
    
    header_table = Table(header_data, colWidths=[1.2*inch, 2.5*inch, 1.2*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#F0F0F0')),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Journal entries
    total_hours = 0
    for log in logs:
        hours = log.total_hours()
        total_hours += hours
        day_of_week = datetime.strptime(str(log.date), '%Y-%m-%d').strftime('%A')
        
        # Date and time header
        time_in_12h = convert_to_12hour(log.time_in)
        time_out_12h = convert_to_12hour(log.time_out)
        
        date_header = f"{log.date.strftime('%B %d, %Y')} ({day_of_week}) | {time_in_12h} - {time_out_12h} | {round(hours, 2)} hrs"
        story.append(Paragraph(date_header, date_header_style))
        
        # Task description box
        task_box_data = [[log.description]]
        task_table = Table(task_box_data, colWidths=[7*inch])
        task_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFACD')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ]))
        story.append(task_table)
        story.append(Spacer(1, 0.2*inch))
    

    
    # Build PDF
    doc.build(story)
    return response
