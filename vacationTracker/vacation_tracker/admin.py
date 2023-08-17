import calendar
from datetime import datetime, date

from django.contrib import admin
from django.db.models import Q, F, Sum
from django.utils.html import format_html

# from front.models import Template
from .models import Employee, VacationRequest, VacationRequestSupervisorView
# from communications.tasks import send_templated_mail


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'start_date', 'supervisor', 'department', 'number_of_vacation_days']
    fields = [ 'start_date', 'end_date', 'user','days_per_year', 'extra_days', 'department', 'supervisor', 'extra_supervisors']
    filter_horizontal = ('extra_supervisors',)
    autocomplete_fields = ['user','supervisor']
    list_select_related = ['user']
    list_filter = ['supervisor','department']
    readonly_fields = ['number_of_vacation_days']

    def number_of_vacation_days(self, obj=None):

        days_in_year = 365 + calendar.isleap(datetime.now().year)
        if obj is not None:
            pto_per_day = obj.days_per_year / days_in_year

        if obj.end_date: # for terminated employees
                if obj.start_date < date(2021, 9, 1) and obj.department == 'it':  # it hired before 1st sept 2021
                    if obj.end_date > date(2021, 9, 1):  # need to calculate old and new policy
                        new_rate_workdays_vacation_days = (obj.end_date - date(2021, 9, 1)).days * pto_per_day
                        old_rate_workdays_vacation_days = (date(2021, 9, 1) - obj.start_date).days * (21 / days_in_year)  # according to the old pto policy
                        total_vacation_days = old_rate_workdays_vacation_days + new_rate_workdays_vacation_days
                    else: # it hired after 1st sept 2021
                        total_vacation_days = (obj.end_date - obj.start_date).days * (21 / days_in_year)
                else:
                    total_vacation_days = (obj.end_date - obj.start_date).days * pto_per_day
        else: # for current employees
            if obj.start_date < date(2021,9,1) and obj.department == 'it': # it hired before 1st sept 2021
                new_rate_workdays_vacation_days = (datetime.today().date() - date(2021,9,1)).days * pto_per_day
                old_rate_workdays_vacation_days = (date(2021,9,1) - obj.start_date).days * (21 / days_in_year) # according to the old pto policy
                total_vacation_days = old_rate_workdays_vacation_days + new_rate_workdays_vacation_days
            else:
                total_vacation_days = (datetime.today().date() - obj.start_date).days * pto_per_day

        submitted_vac_days = obj.vacationrequest_set.filter(status='approved').values('user').annotate(vac_days_sum=Sum(F('end_date') - F('start_date')))
        total_left_vacation_days = round((total_vacation_days - obj.extra_days - (submitted_vac_days.get(user=obj.id)['vac_days_sum'].days if submitted_vac_days.exists() else 0)),3)

        if total_left_vacation_days < 0:
            return format_html(f"<b><font color='red'>{total_left_vacation_days}</font color> <br>Attention - Negative days left!</b>")

        return format_html(f'{total_left_vacation_days}')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name__in=['People Team', 'IT support']).exists():
            return qs
        return qs.filter(Q(user=request.user.pk) | Q(supervisor=request.user.pk) | Q(extra_supervisors=request.user.pk))


@admin.register(VacationRequest)
class VacationRequestAdmin(admin.ModelAdmin):
    list_display = [
        'submitted_on',
        'start_date',
        'end_date',
        'number_of_vacation_days',
        'user',
        'supervisor',
        'status',
        'comment',
    ]

    search_fields = ('id', 'submitted_on', 'start_date', 'end_date', 'status', 'user',)
    fields = ('start_date',
            'end_date',
            'user',
            'status',
            'comment')
    list_filter = ('status',)
    list_display_links = ('submitted_on',)
    list_select_related = ['user__supervisor','user__user']

    add_form_template = 'vacation_app/custom_change_form.html'


    def add_view(self, request, form_url='', extra_context=None):
        extra_context = self.days_left_for_request_form(request)
        return super().add_view(request, form_url, extra_context=extra_context)

    def days_left_for_request_form(self, request):
        try:
            days_in_year = 365 + calendar.isleap(datetime.now().year)
            employee = Employee.objects.get(user=request.user)
            total_workdays = (datetime.today().date() - employee.start_date).days
            pto_per_day = employee.days_per_year / days_in_year

            submitted_vac_days_list = VacationRequest.objects.filter(status='approved').values('user').annotate(vac_days_sum=Sum(F('end_date') - F('start_date')))  # QS with sum days per employee
            vac_days_left_for_user = round((total_workdays * pto_per_day - employee.extra_days -
                                            (submitted_vac_days_list.get(user=employee.id)['vac_days_sum'].days if submitted_vac_days_list.filter(user=employee.id).exists() else 0)),
                                           3)
            if vac_days_left_for_user < 0:
                return {'days_left': format_html(f"<b><font color='red'>{vac_days_left_for_user}</font color> <br>Attention - Negative days left!</b>")}

            return {'days_left': vac_days_left_for_user}

        except Exception as e:
            return {'days_left': format_html("<b><font color='red'>You're not in Employees List!<br>Reach out to People Team and ask them to add you first.</font color></b>")}

    def has_change_permission(self, request, obj=None):
        if obj:
            if obj.status in ['approved','rejected']:
                if request.user.is_superuser or request.user.has_perm('vacation_tracker.can_approve_myself_vacation'):
                    return True
                return False
        return True

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.status in ['approved','rejected']:
                if request.user.is_superuser or request.user.groups.filter(name__in=['People Team', 'IT support']).exists():
                    return True
                return False
        return True

    def get_readonly_fields(self, request, obj=None, fields=None):
        if obj:  # on /change page
            if obj.status in ['approved', 'rejected']:
                if request.user.has_perm('vacation_tracker.can_approve_myself_vacation'):
                    return [ 'start_date', 'end_date', 'user', 'comment']
                return ['start_date', 'end_date', 'user', 'comment', 'status']
            else: # for initial and in_progress statuses
                if request.user.has_perm('vacation_tracker.can_approve_myself_vacation'):
                    return ['user']
        return ['status','user']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user__user=request.user.id)

    def save_model(self, request, obj, form, change):
         if employee:= request.user.employee_set.all().first():
            obj.user = employee
            return super().save_model(request, obj, form, change)


@admin.register(VacationRequestSupervisorView)
class VacationRequestSupervisorViewAdmin( admin.ModelAdmin):
    list_display = ['id',
                    'submitted_on',
                    'start_date',
                    'end_date',
                    'number_of_vacation_days',
                    'user',
                    'supervisor',
                    'status',
                    'comment'
                    ]
    search_fields = ('submitted_on', 'start_date', 'end_date', 'status', 'user')
    fields = ('start_date', 'end_date', 'user', 'status','comment')
    list_filter = ('status', 'user',)
    list_editable = ('status',)
    list_display_links = ('submitted_on',)
    ordering = ("-submitted_on",)
    list_select_related = ['user__supervisor', 'user__user']


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name__in=['People Team', 'IT support']).exists():
            return qs
        return qs.filter(Q(user__supervisor=request.user.pk) | Q(user__extra_supervisors=request.user.pk))

    def get_readonly_fields(self, request, obj=None, fields=None):
        if obj:  # on /change page
            if obj.status in ['approved', 'rejected']:
                if request.user.has_perm('vacation_tracker.can_approve_myself_vacation'):
                    return ['start_date', 'end_date', 'user', 'comment']
                else:
                    return ['start_date', 'end_date', 'user', 'comment', 'status']
            else:  # for initial and in progress statuses
                if request.user.has_perm('vacation_tracker.can_approve_vacations'):
                    return []
        return ['status']

    def save_model(self, request, obj, form, change):
        if obj:
            if form.initial['status'] != 'approved' and form.cleaned_data['status'] == 'approved':
                print('send email / slack message / notification using whatever way you want:)')
                # send_templated_mail.delay(Template.JUNE_EMPLOYEES_VACATION_NOTIFICATION,
                #                           to=(obj.user.user.email,),
                #                           **{'first_name': obj.user.user.first_name})

        return super().save_model(request, obj, form, change)


