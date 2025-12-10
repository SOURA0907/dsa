from django.db import models

class Location(models.Model):
    pincode = models.CharField(max_length= 10 , unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()


    def __str__(self):
        return self.pincode
    
class Edge(models.Model):
    from_loc = models.ForeignKey(Location,related_name='edges_from',on_delete=models.CASCADE)
    to_loc = models.ForeignKey(Location,related_name='edges_to',on_delete=models.CASCADE)
    distance_km = models.FloatField()
    bidirectional = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.from_loc} -> {self.to_loc} ({self.distance_km} km)"