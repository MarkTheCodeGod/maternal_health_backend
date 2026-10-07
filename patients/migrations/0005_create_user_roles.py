from django.db import migrations
from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions


def create_roles(apps, schema_editor):
    # 1. Force Django to generate all model permissions in the database right now!
    for app_config in global_apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # 2. Create the 3 groups
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    editor_group, _ = Group.objects.get_or_create(name='Editor')
    viewer_group, _ = Group.objects.get_or_create(name='Viewer')

    # 3. Fetch app permissions now that they are generated
    app_perms = Permission.objects.filter(
        content_type__app_label__in=['patients', 'patient_activity', 'activity_logs']
    )

    # Admin: Full access (create, view, update, delete)
    admin_group.permissions.set(app_perms)

    # Editor: Can create, view, update, but CANNOT delete
    editor_perms = app_perms.exclude(codename__startswith='delete_')
    editor_group.permissions.set(editor_perms)

    # Viewer: Read-only access (view permissions only)
    viewer_perms = app_perms.filter(codename__startswith='view_')
    viewer_group.permissions.set(viewer_perms)


def remove_roles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Admin', 'Editor', 'Viewer']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '__latest__'),
        ('auth', '__latest__'),
        ('patient_activity', '0005_alter_patientactivitylog_patient_and_more'),
        ('patients', '0004_content_image_file_content_stage_and_more'),
    ]

    operations = [
        migrations.RunPython(create_roles, remove_roles),
    ]