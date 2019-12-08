from django.shortcuts import render
from django.views.generic import View

from . import models


class EnqueteListView(View):
    """
    アンケート一覧画面
    """

    def get(self, request, *args, **kwargs):
        """
        機能
        ・IDリンク付き一覧表示
        ・ページング　10件ごと
        """
        enquete_list = models.Enquete.objects.all()
        print(enquete_list)
        context_data = {
            'enquete_data': enquete_list,
        }
        return render(request, 'enquete/enquete_list.html', context_data)
