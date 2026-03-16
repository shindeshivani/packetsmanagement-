from django.db import models

# Create your models here.
class PacketEntry(models.Model):
    packet_one_kg=models.IntegerField(verbose_name='One KG Packets')
    packet_half_kg=models.IntegerField(verbose_name='Half KG Packets')
    price_one_kg=models.IntegerField(verbose_name='One KG Price')
    price_half_kg=models.IntegerField(verbose_name='Half KG Price')

    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Entry {self.id} - {self.created_at.date()}"