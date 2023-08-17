# Generated by Django 4.1.5 on 2023-08-17 15:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days_per_year', models.FloatField(auto_created=True, db_index=True, verbose_name='Vacation days per year')),
                ('start_date', models.DateField(help_text='first day according to employment contract')),
                ('end_date', models.DateField(blank=True, help_text='last workday according to submitted termination form', null=True)),
                ('department', models.CharField(choices=[('it', 'IT'), ('sales', 'Sales'), ('finance', 'Finance'), ('leadership', 'Leadership'), ('resident_support', 'Resident Support'), ('business_development', 'BD'), ('people_team', 'People Team'), ('performance_marketing', 'Performance Marketing'), ('product', 'Product')], default='it', max_length=64)),
                ('extra_days', models.FloatField(db_index=True, default=0, help_text='For submissions out of this app')),
                ('extra_supervisors', models.ManyToManyField(blank=True, help_text='Other users, apart from direct SV who supposed to see emps vacations (from Leadership)', limit_choices_to=models.Q(('groups__name', 'Leadership'), ('is_active', True), ('is_staff', True)), related_name='extra_svs', to=settings.AUTH_USER_MODEL)),
                ('supervisor', models.ForeignKey(blank=True, limit_choices_to=models.Q(('groups__name', 'Supervisors'), ('is_active', True), ('is_staff', True)), null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='employee_supervisor', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(limit_choices_to={'is_active': True, 'is_staff': True}, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Username')),
            ],
            options={
                'verbose_name': 'Employee',
                'verbose_name_plural': 'Employees',
            },
        ),
        migrations.CreateModel(
            name='VacationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_on', models.DateField(auto_now=True)),
                ('request_date', models.DateField(auto_now=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('approved', 'Approved'), ('rejected', 'Rejected'), ('in_progress', 'In Progress'), ('initial', 'Initial')], default='initial', max_length=64, verbose_name='Request status')),
                ('comment', models.TextField(blank=True, default="Example:\n\nMy dog ate my homework :'(\nI need a day off to prepare for the class tmr.", help_text='Any useful information related to the request, such as: reasons / details / etc.')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='vacation_tracker.employee', verbose_name='user')),
            ],
            options={
                'verbose_name': 'My Vacation Requests',
                'verbose_name_plural': 'My Vacation Requests',
                'permissions': (('can_approve_myself_vacation', 'Can Approve myself vacation'),),
            },
        ),
        migrations.CreateModel(
            name='VacationRequestSupervisorView',
            fields=[
            ],
            options={
                'verbose_name': 'My employees vacations submissions (Supervisor View)',
                'verbose_name_plural': 'My employees vacations submissions (Supervisor View)',
                'permissions': (('can_approve_vacations', 'Can approve vacations'),),
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('vacation_tracker.vacationrequest',),
        ),
    ]
