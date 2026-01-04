from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def fill_user(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    owner = (
        User.objects.filter(is_superuser=True).order_by("id").first()
        or User.objects.order_by("id").first()
    )
    if not owner:
        return

    UploadedScheduleFile = apps.get_model("schedule", "UploadedScheduleFile")
    UploadedScheduleFile.objects.filter(user__isnull=True).update(user=owner)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("schedule", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="uploadedschedulefile",
            name="user",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="UploadedScheduleFile", to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(fill_user, noop),
        migrations.AlterField(
            model_name="uploadedschedulefile",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="UploadedScheduleFile", to=settings.AUTH_USER_MODEL),
        ),
    ]
