from django.conf import settings
from django.db import migrations


def fill_user(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    owner = (
        User.objects.filter(is_superuser=True).order_by("id").first()
        or User.objects.order_by("id").first()
    )
    if not owner:
        return

    model_names = [
        "Couple",
        "Trainer",
        "Day",
        "Group",
        "GroupLesson",
        "TrainerDayAvailability",
        "DancersAvailability",
    ]
    for name in model_names:
        Model = apps.get_model("main", name)
        Model.objects.filter(user__isnull=True).update(user=owner)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0020_assign_existing_rows_to_default_user"),
    ]

    operations = [
        migrations.RunPython(fill_user, noop),
    ]
