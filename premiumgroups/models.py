from django.db import models

class PremiumGroup(models.Model):
    name = models.CharField(max_length=255)
    chat_id = models.CharField(max_length=255)
    sector = models.ForeignKey('Sector', on_delete=models.DO_NOTHING, null=True, related_name='sector_pgs')
    location = models.ForeignKey('Location', on_delete=models.DO_NOTHING, null=True, related_name='location_pgs')

    def __str__(self) -> str:
        return self.name
    

class Sector(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.sector
    

class Location(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.keyword
    

class SectorKeyword(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.DO_NOTHING, related_name='keywords')
    keyword = models.CharField(max_length=255)

    def __str__(self):
        return self.keyword
    

class LocationKeyword(models.Model):
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, related_name='keywords')
    keyword = models.CharField(max_length=255)
    
    def __str__(self):
        return self.keyword

