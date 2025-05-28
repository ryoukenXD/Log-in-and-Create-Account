import datetime
import pandas as pd
import re
import io
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import connections
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import get_user_model
from .models import Account
from django.contrib import messages
from django.db import connection
from django.shortcuts import render, redirect
from .models import Personnel, EmploymentDetails, Dependent, Parent, Education, EmploymentHistory, Identification, Position, Attendance
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import connections, transaction
from django.contrib.auth.models import User
from django.http import HttpResponse, FileResponse
import os
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import get_user_model
from datetime import datetime, time
from django.contrib import messages
from django.contrib.auth import get_user_model



@login_required
def dashboard(request):
    return render(request, 'ui/dashboard.html', {'user': request.user})

def attendance(request):
   def attendance(request):
    # Get employee filter from query params or session
    employee_id = request.GET.get('employee_id')
    if employee_id:
        request.session['current_employee_id'] = employee_id
    else:
        employee_id = request.session.get('current_employee_id')
    
    # Get all personnel for navigation
    all_personnel = Personnel.objects.all().order_by('name')
    
    # Don't set any default employee - only show after explicit selection or upload
    
    # Get current employee index for navigation
    current_index = 0
    current_employee = None
    if employee_id:
        try:
            current_employee = Personnel.objects.get(id=employee_id)
            # Find index of current employee in the list
            for i, person in enumerate(all_personnel):
                if person.id == current_employee.id:
                    current_index = i
                    break
        except Personnel.DoesNotExist:
            current_employee = None
    
    # Calculate previous and next employee IDs
    prev_employee = None
    next_employee = None
    if all_personnel.count() > 1:
        if current_index > 0:
            prev_employee = all_personnel[current_index - 1]
        if current_index < all_personnel.count() - 1:
            next_employee = all_personnel[current_index + 1]
    
    # Filter attendance records by employee if one is selected
    if current_employee:
        # First get all records and calculate stats
        all_records = Attendance.objects.filter(personnel=current_employee)
        total_present = all_records.filter(status='present').count()
        total_absent = all_records.filter(status='absent').count()
        total_late = all_records.filter(status='late').count()
        
        # Then get the paginated records for display
        attendance_records = all_records.order_by('-date')[:50]
        
        # Check if this is the first employee in the list
        is_first_employee = Personnel.objects.order_by('id').first() == current_employee
    else:
        attendance_records = []
        total_present = 0
        total_absent = 0
        total_late = 0
        is_first_employee = False
    
    context = {
        'user': request.user,
        'attendance_records': attendance_records,
        'total_present': total_present,
        'total_absent': total_absent,
        'total_late': total_late,
        'upload_success': request.session.pop('upload_success', None),
        'upload_error': request.session.pop('upload_error', None),
        'current_employee': current_employee,
        'prev_employee': prev_employee,
        'next_employee': next_employee,
        'all_personnel': all_personnel,
        'is_first_employee': is_first_employee,
    }
    
    return render(request, 'ui/attendance.html', context)

@csrf_exempt
def upload_attendance(request):
    """Handle batch upload of attendance records from Excel file"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    if 'attendance_file' not in request.FILES:
        request.session['upload_error'] = 'No file was uploaded.'
        return redirect('attendance')
    
    excel_file = request.FILES['attendance_file']
    if not excel_file.name.endswith(('.xls', '.xlsx')):
        request.session['upload_error'] = 'File must be an Excel file (.xls or .xlsx).'
        return redirect('attendance')
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file, header=None)
        
        # Check if the file has the expected structure
        if df.shape[1] < 7:  # At least 7 columns needed (A-G)
            request.session['upload_error'] = 'Invalid file format. The file must have at least 7 columns.'
            return redirect('attendance')
        
        # Clear the current employee selection
        if 'current_employee_id' in request.session:
            del request.session['current_employee_id']
        
        # Track all personnel created/updated during this upload
        processed_personnel = []
        attendance_count = 0
        current_personnel = None
        
        # Helper function to parse time values
        def parse_time(value):
            if pd.isna(value):
                return None
                
            if isinstance(value, str):
                try:
                    # Try to parse time strings like "7:30 AM" or "12:15 PM"
                    return datetime.strptime(value, '%I:%M %p').time()
                except ValueError:
                    try:
                        # Try alternate format like "07:30"
                        return datetime.strptime(value, '%H:%M').time()
                    except ValueError:
                        return None
            elif isinstance(value, datetime):
                return value.time()
            return None
        
        # Process each row in the Excel file
        for i in range(len(df)):
            row = df.iloc[i]
            cell_a = str(row[0]) if not pd.isna(row[0]) else ''
            
            # Check if this is an employee row (contains name and ID in parentheses)
            employee_match = re.search(r'(.+)\s*\((\d+)\)', cell_a)
            if employee_match:
                employee_name = employee_match.group(1).strip()
                employee_id = employee_match.group(2)
                
                # Get or create the personnel record
                # Get or create the personnel record
                personnel, created = Personnel.objects.get_or_create(
                    employee_id=employee_id,
                    defaults={
                        'name': employee_name
                    }
                )
                
                # Update name if it changed
                if not created and personnel.name != employee_name:
                    personnel.name = employee_name
                    personnel.save()
                
                current_personnel = personnel
                if personnel not in processed_personnel:
                    processed_personnel.append(personnel)
                continue
            
            # Skip if no personnel is set yet
            if not current_personnel:
                continue
            
            # Check if this is a date row (column A has a date format)
            date_match = re.match(r'(\d{1,2}/\d{1,2}/\d{4})\s*\w*', cell_a)
            if not date_match:
                continue
            
            date_str = date_match.group(1)
            try:
                date_obj = datetime.strptime(date_str, '%m/%d/%Y').date()
            except ValueError:
                continue
            
            # Extract time entries
            time_in_1 = parse_time(row[1]) if len(row) > 1 else None  # Column B - Time In 1
            time_out_1 = parse_time(row[2]) if len(row) > 2 else None  # Column C - Time Out 1
            time_in_2 = parse_time(row[3]) if len(row) > 3 else None  # Column D - Time In 2
            time_out_2 = parse_time(row[4]) if len(row) > 4 else None  # Column E - Time Out 2
            time_in_3 = parse_time(row[5]) if len(row) > 5 else None  # Column F - Time In 3
            time_out_3 = parse_time(row[6]) if len(row) > 6 else None  # Column G - Time Out 3
            
            # Skip if no time entries
            if not any([time_in_1, time_out_1, time_in_2, time_out_2, time_in_3, time_out_3]):
                continue
            
            # Create or update attendance record
            attendance, created = Attendance.objects.update_or_create(
                personnel=current_personnel,
                date=date_obj,
                defaults={
                    'time_in_1': time_in_1,
                    'time_out_1': time_out_1,
                    'time_in_2': time_in_2,
                    'time_out_2': time_out_2,
                    'time_in_3': time_in_3,
                    'time_out_3': time_out_3,
                }
            )
            
            attendance_count += 1
        
        # Set the first employee as the current one for viewing
        if processed_personnel:
            request.session['current_employee_id'] = str(processed_personnel[0].id)
            if len(processed_personnel) == 1:
                request.session['upload_success'] = f'Successfully uploaded {attendance_count} attendance records for {processed_personnel[0].name}.'
            else:
                employee_names = ', '.join([p.name for p in processed_personnel])
                request.session['upload_success'] = f'Successfully uploaded {attendance_count} attendance records for {len(processed_personnel)} employees: {employee_names}'
        else:
            request.session['upload_error'] = 'No valid employee data found in the uploaded file.'
        
        return redirect('attendance')
    
    except Exception as e:
        request.session['upload_error'] = f'Error processing file: {str(e)}'
        return redirect('attendance')

def add_employees(request):
    if request.method == 'POST':
        # Personnel
        name = request.POST.get('name')
        birthdate = request.POST.get('birthdate')
        
        # Ensure all dates are in YYYY-MM-DD format
        # This handles both MM/DD/YYYY format and existing YYYY-MM-DD format
        def format_date(date_str):
            if not date_str:
                return None
                
            # Already in YYYY-MM-DD format
            if date_str and len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
                return date_str
                
            # Handle MM/DD/YYYY format
            if date_str and '/' in date_str:
                try:
                    month, day, year = date_str.split('/')
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except ValueError:
                    pass
            
            # Return None for invalid formats to avoid validation errors
            return None
        
        # Format all dates
        birthdate = format_date(birthdate)
        
        birth_place = request.POST.get('birth_place')
        present_address = request.POST.get('present_address')
        provincial_address = request.POST.get('provincial_address')
        marital_status = request.POST.get('marital_status')
        spouse_name = request.POST.get('spouse_name')

        personnel = Personnel.objects.create(
            name=name,
            birthdate=birthdate,
            birth_place=birth_place,
            present_address=present_address,
            provincial_address=provincial_address,
            marital_status=marital_status,
            spouse_name=spouse_name,
            date_added=timezone.now()  # Use the current date and time
        )

        # Employment Details
        position_name = request.POST.get('position')
        position, created = Position.objects.get_or_create(position_name=position_name)
        status = request.POST.get('status')
        
        # Get and format date fields
        date_hired = format_date(request.POST.get('date_hired'))
        latest_evaluation = format_date(request.POST.get('latest_evaluation'))
        basic_salary = request.POST.get('basic_salary')

        EmploymentDetails.objects.create(
            personnel=personnel,
            position=position,
            status=status,
            date_hired=date_hired,
            latest_evaluation=latest_evaluation,
            basic_salary=basic_salary
        )

        # Identifications
        sss = request.POST.get('sss')
        philhealth = request.POST.get('philhealth')
        pag_ibig = request.POST.get('pag_ibig')
        tin = request.POST.get('tin')

        Identification.objects.create(
            personnel=personnel,
            sss=sss,
            philhealth=philhealth,
            pag_ibig=pag_ibig,
            tin=tin
        )

       # Parent Details
        mother_name = request.POST.get('mother_name')
        mother_occupation = request.POST.get('mother_occupation')
        father_name = request.POST.get('father_name')
        father_occupation = request.POST.get('father_occupation')
        contact_number = request.POST.get('contact_number')

        Parent.objects.create(
            personnel=personnel,
            parent_type='Mother',
            name=mother_name,
            occupation=mother_occupation,
            contact_number=contact_number,
        )

        Parent.objects.create(
            personnel=personnel,
            parent_type='Father',
            name=father_name,
            occupation=father_occupation,
            contact_number=contact_number,
        )

        # Education
        elementary = request.POST.get('elementary')
        high_school = request.POST.get('high_school')
        college = request.POST.get('college')
        other_skills = request.POST.get('other_skills')

        Education.objects.create(
            personnel=personnel,
            level='Elementary',
            school_name=elementary,
            other_skills=other_skills,
        )

        Education.objects.create(
            personnel=personnel,
            level='High School',
            school_name=high_school,
            other_skills=other_skills,
        )

        Education.objects.create(
            personnel=personnel,
            level='College',
            school_name=college
        )

        # Dependents
        dependents = []
        for i in range(1, 6):
            dependent_name = request.POST.get(f'dependent{i}')
            dependent_age = request.POST.get(f'age{i}')
            if dependent_name and dependent_age:
                dependents.append(Dependent(
                    personnel=personnel,
                    name=dependent_name,
                    age=dependent_age
                ))
        Dependent.objects.bulk_create(dependents)

        # Employment History
        company_name = request.POST.get('company_name')
        company_address = request.POST.get('company_address')
        company_year = request.POST.get('company_year')
        company_contact = request.POST.get('company_contact')

        # Only create employment history if company_name is provided
        if company_name:  # Check if company_name exists and is not empty
            if company_year:
                company_year = int(company_year)
            else:
                # Default to current year if not provided
                company_year = timezone.now().year

            EmploymentHistory.objects.create(
                personnel=personnel,
                company_name=company_name,
                job_title=position_name,
                address=company_address,
                start_year=company_year,
                contact_number=company_contact
            )

    date_filter = request.GET.get('date_filter')
    if date_filter:
        date_filter = datetime.datetime.strptime(date_filter, '%Y-%m-%d').date()
        employees = EmploymentDetails.objects.select_related('personnel', 'position').filter(personnel__date_added__date=date_filter)
    else:
        employees = EmploymentDetails.objects.select_related('personnel', 'position').all()    

    return render(request, 'ui/add_employees.html', {'employees': employees})

@csrf_exempt
def remove_employees(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ids = data.get('ids', [])
        Personnel.objects.using('personnel_db').filter(id__in=ids).delete()

        # Debug the query
        print(connection.queries)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def payroll_computations(request):
    return render(request, 'ui/payroll_computations.html', {'user': request.user})

def personnel_profile(request):
    return render(request, 'ui/personnel_profile.html')

def user_profile(request):
    return render(request, 'ui/user_profile.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log the user in
            login(request, user)
            messages.success(request, "Logged in successfully!")
            print(f"User {user.username} logged in successfully!")  # Debugging
            return redirect('dashboard')  # Redirect to the dashboard
        else:
            messages.error(request, "Invalid username or password")
            print("Invalid login attempt!")  # Debugging
    
    return render(request, 'ui/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')


def forgot_password(request):
    return render(request, 'ui/forgot_password.html')

def create_account(request):
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        contact = request.POST.get('contact_number')
        password = request.POST.get('password')
        email = request.POST.get('email')

        # Save the data to the database
        try:
            account = Account.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                contact=contact,
                password=password,  # Save the plain text password
                email=email
            )
            account.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')  # Redirect to login page after account creation
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")

    return render(request, 'ui/create_account.html')

def reports(request):
    return render(request, 'ui/reports.html', {'user': request.user})

def download_attendance_template(request):
    """Serve the attendance template file for download"""
    template_path = os.path.join(settings.BASE_DIR, 'ui', 'static', 'ui', 'templates', 'attendance_template.xlsx')
    
    if os.path.exists(template_path):
        response = FileResponse(open(template_path, 'rb'))
        response['Content-Disposition'] = 'attachment; filename="attendance_template.xlsx"'
        return response
    else:
        # If template doesn't exist, generate it first
        from django.core.management import call_command
        call_command('create_attendance_template')
        
        if os.path.exists(template_path):
            response = FileResponse(open(template_path, 'rb'))
            response['Content-Disposition'] = 'attachment; filename="attendance_template.xlsx"'
            return response
        else:
            return HttpResponse("Template file could not be generated.", status=500)
        
def clear_attendance(request):
    """Clear all attendance records from the database"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        # Delete all attendance records
        deleted_count = Attendance.objects.all().delete()[0]
        
        # Return success message
        request.session['upload_success'] = f'Successfully cleared {deleted_count} attendance records.'
        return redirect('attendance')
    except Exception as e:
        request.session['upload_error'] = f'Error clearing attendance records: {str(e)}'
        return redirect('attendance')
