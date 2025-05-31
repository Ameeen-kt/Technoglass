from django.db import models

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150)
    email = models.EmailField(null=True, blank=True)
    location = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    gst_no = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.username} | {self.location}"

class GlassSummary(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.customer} | {self.created_at}"


class Measurement(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    summary = models.ForeignKey(GlassSummary, on_delete=models.CASCADE, related_name='measurements')
    thickness = models.CharField(max_length=20)
    unit = models.CharField(max_length=10)
    height = models.FloatField()
    width = models.FloatField()
    quantity = models.IntegerField()
    area = models.FloatField()
    rate = models.FloatField()
    amount = models.FloatField()
    shape = models.CharField(max_length=50)

class ExtraCharge(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    summary = models.ForeignKey(GlassSummary, on_delete=models.CASCADE, related_name='extra_charges')
    label = models.CharField(max_length=100)
    amount = models.FloatField()
