from django.db import models


class Campana(models.Model):
    codigo = models.SlugField(unique=True)


class Productor(models.Model):
    codigo = models.SlugField(unique=True)


class Cupo(models.Model):
    campana = models.ForeignKey(Campana, on_delete=models.CASCADE)
    productor = models.ForeignKey(Productor, on_delete=models.PROTECT)
    limite_kg = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["campana", "productor"], name="cupo_unico_por_campana_y_productor"
            )
        ]


class Entrega(models.Model):
    cupo = models.ForeignKey(Cupo, on_delete=models.CASCADE, related_name="entregas")
    peso_kg = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(peso_kg__gt=0), name="entrega_peso_positivo")
        ]
