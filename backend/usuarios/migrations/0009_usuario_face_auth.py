# Generated manually for face authentication fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0008_documentoproceso'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='face_embedding',
            field=models.BinaryField(
                blank=True,
                null=True,
                verbose_name='Embedding facial'
            ),
        ),
        migrations.AddField(
            model_name='usuario',
            name='face_registered_at',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Rostro registrado en'
            ),
        ),
        migrations.AddField(
            model_name='usuario',
            name='face_2fa_enabled',
            field=models.BooleanField(
                default=False,
                verbose_name='2FA facial habilitado'
            ),
        ),
        migrations.AddField(
            model_name='usuario',
            name='failed_face_attempts',
            field=models.PositiveSmallIntegerField(
                default=0,
                verbose_name='Intentos faciales fallidos'
            ),
        ),
        migrations.AddField(
            model_name='usuario',
            name='face_locked_until',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Verificación facial bloqueada hasta'
            ),
        ),
    ]
