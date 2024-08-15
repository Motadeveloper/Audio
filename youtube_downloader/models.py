from django.db import models



class VideoInfo(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=255)
    thumbnail_url = models.URLField()
    request_count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title

    @staticmethod
    def total_conversions():
        return VideoInfo.objects.aggregate(total=models.Sum('request_count'))['total'] or 0