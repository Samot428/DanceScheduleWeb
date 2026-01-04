from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def assign_owner(apps, schema_editor):
    # Choose an existing user to own legacy rows.
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    owner = (
        User.objects.filter(is_superuser=True).order_by("id").first()
        or User.objects.order_by("id").first()
    )
    if not owner:
        # No users exist yet; nothing to assign.
        return

    target_models = [
        "Group",
        "Day",
        "Couple",
        "Trainer",
        "GroupLesson",
        "TrainerDayAvailability",
        "DancersAvailability",
    ]

    for model_name in target_models:
        Model = apps.get_model("main", model_name)
        Model.objects.filter(user__isnull=True).update(user=owner)


def noop_reverse(apps, schema_editor):
    # Data-only migration; nothing to reverse safely.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0019_remove_group_primary_group_index_grouplesson_groups_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="couple",
            name="user",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="couple", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="day",
            name="user",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="day", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="group",
            name="user",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="owned_groups", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="grouplesson",
            name="user",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="group_lessons", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="trainer",
            name="user",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="trainer", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="trainerdayavailability",
            name="user",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="trainer_availabilities", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="dancersavailability",
            name="user",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="dancer_availabilities", to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(assign_owner, noop_reverse),
        migrations.AlterField(
            model_name="couple",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="couple", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="day",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="day", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="group",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="owned_groups", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="grouplesson",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="group_lessons", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="trainer",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="trainer", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="trainerdayavailability",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="trainer_availabilities", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="dancersavailability",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dancer_availabilities", to=settings.AUTH_USER_MODEL),
        ),
    ]
