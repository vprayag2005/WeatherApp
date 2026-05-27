from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SubdivisionAlert",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subdivision_name", models.CharField(max_length=140, unique=True)),
                ("subdivision_slug", models.SlugField(max_length=160, unique=True)),
                ("source_date", models.DateField(blank=True, null=True)),
                ("source_updated_at", models.DateTimeField(blank=True, null=True)),
                ("geometry", models.JSONField(blank=True, default=dict)),
                ("properties", models.JSONField(blank=True, default=dict)),
                ("synced_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("subdivision_name",)},
        ),
    ]
