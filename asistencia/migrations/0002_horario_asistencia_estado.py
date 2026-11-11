from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asistencia', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('hora_inicio', models.TimeField(verbose_name='Inicio de la clase')),
                ('hora_tardanza', models.TimeField(verbose_name='Tardanza desde')),
                ('hora_fin', models.TimeField(verbose_name='Fin de la clase')),
            ],
            options={
                'ordering': ['hora_inicio'],
            },
        ),
        migrations.AddField(
            model_name='asistencia',
            name='estado',
            field=models.CharField(choices=[('presente', 'Presente'), ('tardanza', 'Tardanza')], default='presente', max_length=20),
        ),
        migrations.AddField(
            model_name='asistencia',
            name='horario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asistencias', to='asistencia.horario'),
        ),
    ]
