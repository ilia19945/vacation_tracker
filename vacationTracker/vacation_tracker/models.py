# from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.html import format_html
from django.contrib.auth.models import User

class Employee(models.Model):
    DEPARTMENT_CHOICES =(
        ('it','IT'),
        ('sales','Sales'),
        ('finance','Finance'),
        ('leadership','Leadership'),
        ('resident_support','Resident Support'),
        ('business_development','BD'),
        ('people_team','People Team'),
        ('performance_marketing','Performance Marketing'),
        ('product','Product'),
    )

    start_date = models.DateField(help_text='first day according to employment contract')
    end_date = models.DateField(blank=True,null=True, help_text='last workday according to submitted termination form')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Username', limit_choices_to={'is_staff': True, 'is_active': True},)
    department = models.CharField(max_length=64, choices=DEPARTMENT_CHOICES, default="it", blank=False, null=False)
    days_per_year = models.FloatField(verbose_name='Vacation days per year',blank=False, null=False, editable=True,auto_created=True, db_index=True)
    extra_days = models.FloatField(blank=False, null=False, default=0, editable=True, db_index=True, help_text="For submissions out of this app")
    supervisor = models.ForeignKey(User, on_delete=models.DO_NOTHING, limit_choices_to=Q(groups__name='Supervisors', is_staff=True, is_active=True), blank=True, null=True, related_name='employee_supervisor')
    extra_supervisors = models.ManyToManyField(User,blank=True, limit_choices_to=Q(groups__name = 'Leadership', is_staff=True, is_active=True), related_name='extra_svs',
                                               help_text='Other users, apart from direct SV who supposed to see emps vacations (from Leadership)')

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return self.user.username


class VacationRequest(models.Model):
    STATUS_CHOICES = (
        ('approved','Approved'),
        ('rejected','Rejected'),
        ('in_progress','In Progress'),
        ('initial','Initial'),
    )

    submitted_on = models.DateField(auto_now=True)
    request_date = models.DateField(blank=True, auto_now=True)
    start_date = models.DateField(auto_now=False, auto_now_add=False, null=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)
    status = models.CharField(max_length=64, verbose_name='Request status', choices=STATUS_CHOICES, default="initial",)
    user = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, verbose_name='user', blank=False,)
    comment = models.TextField(blank=True, help_text='Any useful information related to the request, such as: reasons / details / etc.',
                               default='Example:\n\n'
                               'My dog ate my homework :\'('
                               '\nI need a day off to prepare for the class tmr.')
    class Meta:
        verbose_name = 'My Vacation Requests'
        verbose_name_plural = 'My Vacation Requests'
        permissions = (
            ("can_approve_myself_vacation", "Can Approve myself vacation"),
        )
    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Dates are incorrect! Start date can't be more than End date.")

    def number_of_vacation_days(self):
        return (self.end_date - self.start_date).days


    def supervisor(self):
        return self.user.supervisor

    def __str__(self):
        return format_html(f"{self.user} | {self.start_date} : {self.end_date} | {(self.end_date - self.start_date).days} days.")



class VacationRequestSupervisorView(VacationRequest):
    class Meta:
        proxy = True
        verbose_name = 'My employees vacations submissions (Supervisor View)'
        verbose_name_plural = 'My employees vacations submissions (Supervisor View)'
        permissions = (
            ("can_approve_vacations", "Can approve vacations"),
        )

