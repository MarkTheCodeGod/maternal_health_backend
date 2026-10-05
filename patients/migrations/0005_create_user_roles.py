from django.db import migrations

def create_roles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # Create the 3 roles required by your specification
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    editor_group, _ = Group.objects.get_or_create(name='Editor')
    viewer_group, _ = Group.objects.get_or_create(name='Viewer')

    # Fetch app permissions
    app_perms = Permission.objects.filter(
        content_type__app_label__in=['patients', 'patient_activity', 'activity_logs']
    )

    # 1. Admin: Has all permissions (create, view, update, delete)
    admin_group.permissions.set(app_perms)

    # 2. Editor: Can create, view, update, but CANNOT delete
    editor_perms = app_perms.exclude(codename__startswith='delete_')
    editor_group.permissions.set(editor_perms)

    # 3. Viewer: Read-only access (view permissions only)
    viewer_perms = app_perms.filter(codename__startswith='view_')
    viewer_group.permissions.set(viewer_perms)

def remove_roles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Admin', 'Editor', 'Viewer']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0004_content_image_file_content_stage_and_more'),
    ]

    operations = [
        migrations.RunPython(create_roles, remove_roles),
    ]