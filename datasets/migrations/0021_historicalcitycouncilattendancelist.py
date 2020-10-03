# Generated by Django 3.0.8 on 2020-08-30 17:12

import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("datasets", "0020_auto_20200718_2347"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalCityCouncilAttendanceList",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        blank=True, editable=False, verbose_name="Criado em"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        blank=True, editable=False, verbose_name="Atualizado em"
                    ),
                ),
                ("crawled_at", models.DateTimeField(verbose_name="Coletado em")),
                ("crawled_from", models.URLField(verbose_name="Fonte")),
                (
                    "notes",
                    models.TextField(blank=True, null=True, verbose_name="Anotações"),
                ),
                ("date", models.DateField(verbose_name="Data")),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="Descrição"
                    ),
                ),
                (
                    "council_member",
                    models.CharField(
                        db_index=True, max_length=200, verbose_name="Vereador"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("presente", "Presente"),
                            ("falta_justificada", "Falta Justificada"),
                            ("licenca_justificada", "Licença Justificada"),
                            ("ausente", "Ausente"),
                        ],
                        db_index=True,
                        max_length=20,
                        verbose_name="Situação",
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField()),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Câmara de Vereadores - Lista de Presença",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]