# Generated by Django 5.2.1 on 2025-05-18 20:07

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Formulario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('unidade_nome', models.CharField(blank=True, max_length=50, null=True)),
                ('unidade_quantidade', models.IntegerField(blank=True, null=True)),
                ('titulo', models.CharField(blank=True, max_length=255, null=True)),
                ('data_entrega', models.DateField(blank=True, null=True)),
                ('observacoes', models.TextField(blank=True)),
                ('formato', models.CharField(blank=True, choices=[('A4', 'A4'), ('A5', 'A5'), ('A3', 'A3'), ('CARTA', 'Carta'), ('OFICIO', 'Ofício'), ('OUTRO', 'Outro')], default='A4', max_length=10, null=True)),
                ('cor_impressao', models.CharField(blank=True, choices=[('PB', 'Preto e Branco'), ('COLOR', 'Colorido')], default='PB', max_length=10, null=True)),
                ('impressao', models.CharField(blank=True, choices=[('1_LADO', 'Um lado'), ('2_LADOS', 'Frente e verso'), ('LIVRETO', 'Livreto')], default='1_LADO', max_length=20, null=True)),
                ('arquivo', models.FileField(blank=True, null=True, upload_to='pdfs/')),
                ('cod_op', models.CharField(blank=True, max_length=10, null=True)),
                ('link_download', models.URLField(blank=True, max_length=500, null=True)),
                ('json_link', models.URLField(blank=True, max_length=500, null=True)),
                ('criado_em', models.DateTimeField(default=django.utils.timezone.now)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
