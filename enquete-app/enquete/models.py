from django.db import models


class Enquete(models.Model):
    """
    アンケートテーブル
    項目:
        アンケートID
        アンケート名
    """
    enquete_id = models.CharField(max_length=100)
    enquete_name = models.CharField(max_length=100)

    def __str__(self):
        return self.enquete_name
