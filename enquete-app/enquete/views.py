from django.shortcuts import render
from django.views.generic import View
from django.core.paginator import Paginator

import uuid

from enquete.lib.views_utils import assemble_data_for_totalize_graphs
from enquete.lib.views_utils import make_color
from enquete.lib.views_utils import assemble_questions
from enquete.lib.views_utils import assemble_questions_with_answer
from enquete.lib.views_utils import answer_enquete
from enquete.lib.views_utils import update_enquete
from . import models
from . import forms


class EnqueteListView(View):
    """
    アンケート一覧画面
    """

    def __init__(self):
        self.PAGENATE = 10

    def get(self, request, *args, **kwargs):
        """
        機能
        ・IDリンク付き一覧表示
        ・ページング　10件ごと
        """
        page_num = kwargs.get('page_num', 1)

        enq_list = models.Enquete.objects.all()
        pagenater = Paginator(enq_list, self.PAGENATE)

        page_data = pagenater.get_page(page_num)

        context_data = {
            'data': page_data,
            'page_obj': page_data,
            'page_title': 'アンケート一覧画面',
            'headers': ['アンケートID', 'アンケート名'],
        }
        return render(request, 'enquete/enquete_list.html', context_data)


class EnqueteCreateView(View):
    """
    アンケート作成画面
    """

    def __init__(self):
        self.PAGE_TITLE = 'アンケート作成画面'
        self.QUESTION_TEXT = 'question_text'
        self.QUESTION_TYPE = 'question_type'
        self.CHOICE_NAME = 'choice_name'
        self.IS_SUCCESS = False

    def get(self, request, *args, **kwargs):
        """
        機能
        ・アンケート名の入力
        ・任意の質問項目の追加
        """
        context_data = {
            'page_title': self.PAGE_TITLE,
            'forms': forms.CreateEnqueteForm(),
            'is_success': self.IS_SUCCESS,
        }
        return render(request, 'enquete/enquete_create.html', context_data)

    def post(self, request, *args, **kwargs):
        """
        機能
        ・入力された内容の登録
            -アンケート
            -質問項目
        """
        # アンケートの作成を行う
        self.IS_SUCCESS = self._create_enquete(request)

        context_data = {
            'page_title': self.PAGE_TITLE,
            'forms': forms.CreateEnqueteForm(request.POST or None),
            'is_success': self.IS_SUCCESS,
        }
        print(request.POST)
        return render(request, 'enquete/enquete_create.html', context_data)

    def _create_enquete(self, request):
        """
        アンケートの作成を行う
        """
        is_success = False
        # Enqueteレコード作成
        enquete_id = uuid.uuid4()
        enquete_name = request.POST.get('enquete_name', None)
        enquete_obj = models.Enquete(
            enquete_id=enquete_id,
            enquete_name=enquete_name,
        )
        enquete_obj.save()

        total_q_num = request.POST.get('total_question_num', 1)
        for q_num in range(1, int(total_q_num) + 1):
            # 取得するキーの組み立て
            question_text_str = self.QUESTION_TEXT + str(q_num)
            question_type_str = self.QUESTION_TYPE + str(q_num)
            choice_name_str = self.CHOICE_NAME + str(q_num)

            # 質問項目ごとの情報を取得
            question_text = request.POST.get(question_text_str)
            question_type = request.POST.get(question_type_str)
            choice_names = request.POST.getlist(choice_name_str)

            # Questionレコードの作成
            question_obj = models.Question(
                question_text=question_text,
                question_type=question_type,
            )
            question_obj.save()

            # EQレコードの作成
            EQ_obj = models.EQ(
                E_obj=enquete_obj,
                Q_obj=question_obj,
            )
            EQ_obj.save()

            # Choiceレコードの作成
            for choice_name in choice_names:
                choice_obj = models.Choice(
                    choice_name=choice_name
                )
                choice_obj.save()

                # QCレコードの作成
                QC_obj = models.QC(
                    Q_obj=question_obj,
                    C_obj=choice_obj,
                )
                QC_obj.save()

        is_success = True
        return is_success


class EnqueteDetailView(View):
    """
    アンケート詳細画面
    """

    def __init__(self):
        self.PAGE_TITLE = 'アンケート詳細画面'

    def get(self, request, *args, **kwargs):
        """
        機能
        ・アンケートの詳細情報を表示する
        ・アンケートの回答更新画面へのリンクを提供する
        """
        # アンケートの詳細情報を保持する
        # enquete_details = [{
        #   'member_name': '石井',
        #   'answer': []
        #   },
        #   ....
        # ]

        # アンケートidを取得
        enquete_id = kwargs.get('uuid', None)

        # 対象のアンケートを取得
        enquete_obj = models.Enquete.objects.get(enquete_id=enquete_id)
        eqs = enquete_obj.eq_set.all()

        # テーブルのヘッダーを作成する
        headers = ['回答者', ]
        for eq in eqs:
            headers.append(eq.Q_obj.question_text)

        # アンケートの回答者を取得
        members_obj = []
        for eq in eqs:
            qms = eq.Q_obj.qm_set.all()
            for qm in qms:
                if qm.M_obj in members_obj:
                    continue
                members_obj.append(qm.M_obj)

        # アンケートの質問を取得
        questions_obj = []
        for eq in eqs:
            questions_obj.append(eq.Q_obj)

        # 各回答者の回答を取得し、enquete_detailに詰める
        enquete_details = []
        for member_obj in members_obj:
            enquete_detail = {}
            answers = []
            for question_obj in questions_obj:
                qm = models.QM.objects.get(
                    Q_obj=question_obj, M_obj=member_obj)
                answers.append(qm.answer)

            enquete_detail['member_obj'] = member_obj
            enquete_detail['answers'] = answers

            enquete_details.append(enquete_detail)

        context_data = {
            'page_title': self.PAGE_TITLE,
            'enquete_id': enquete_id,
            'headers': headers,
            'enquete_details': enquete_details,
        }
        return render(request, 'enquete/enquete_detail.html', context_data)


class EnqueteAnswerView(View):
    """
    アンケート回答画面
    """

    def __init__(self):
        self.PAGE_TITLE = 'アンケート回答画面'
        self.IS_SUCCESS = False

    def get(self, request, *args, **kwargs):
        """
        機能
        ・アンケートへの回答を行う
        """
        # アンケートidを取得
        enquete_id = kwargs.get('uuid', None)

        # 対象のアンケートを取得
        enquete_obj = models.Enquete.objects.get(enquete_id=enquete_id)

        # アンケートに紐づく質問を組み立て
        questions = assemble_questions(enquete_obj)

        context_data = {
            'page_title': self.PAGE_TITLE,
            'enquete_obj': enquete_obj,
            'questions': questions,
            'member_form': forms.MemberForm(),
            'is_success': self.IS_SUCCESS,
        }

        return render(request, 'enquete/enquete_answer.html', context_data)

    def post(self, request, *args, **kwargs):
        """
        機能
        ・アンケートへの回答を登録する
        """
        # TODO: 失敗した場合の例外処理を入れる
        self.IS_SUCCESS = True

        # アンケートidを取得
        enquete_id = kwargs.get('uuid', None)
        member_id = request.POST.get('member_name')

        # 対象のアンケートを取得
        enquete_obj = models.Enquete.objects.get(enquete_id=enquete_id)
        # 回答者を取得
        member_obj = models.Member.objects.get(id=member_id)

        # アンケートの回答内容を保存
        self.IS_SUCCESS = answer_enquete(enquete_obj, member_obj, request)

        # アンケートに紐づく質問を組み立て
        questions = assemble_questions(enquete_obj)

        member_form = forms.MemberForm()

        context_data = {
            'page_title': self.PAGE_TITLE,
            'enquete_obj': enquete_obj,
            'questions': questions,
            'member_form': member_form,
            'is_success': self.IS_SUCCESS,
        }

        return render(request, 'enquete/enquete_answer.html', context_data)


class EnqueteAnswerUpdateView(View):
    """
    アンケートの回答更新画面
    """

    def __init__(self):
        self.PAGE_TITLE = 'アンケート回答更新画面'
        self.IS_SUCCESS = False

    def get(self, request, *args, **kwargs):
        """
        機能
        ・一度回答したアンケートへの回答を更新する
        """
        # アンケートidと回答者idを取得
        enquete_id = kwargs.get('uuid', None)
        member_id = kwargs.get('member_id', None)

        # 対象のアンケートと回答者レコードを取得
        enquete_obj = models.Enquete.objects.get(enquete_id=enquete_id)
        member_obj = models.Member.objects.get(id=member_id)

        # アンケートに紐づく質問を組み立て
        questions = assemble_questions_with_answer(enquete_obj, member_obj)

        # MemberFormの初期化を行う
        # 初期値を設定するにはインスタンス化するタイミングで、
        # formの属性名をキーに、初期値をバリューとして定義して渡す必要がある
        initial = {
            'member_name': member_id,
        }
        member_form = forms.MemberForm(initial=initial)

        context_data = {
            'page_title': self.PAGE_TITLE,
            'enquete_obj': enquete_obj,
            'member_obj': member_obj,
            'questions': questions,
            'member_form': member_form,
            'is_success': self.IS_SUCCESS,
        }

        return render(request, 'enquete/enquete_answer_update.html', context_data)

    def post(self, request, *args, **kwargs):
        """
        機能
        ・入力された内容で回答を更新する
        """
        # アンケートidと回答者idを取得
        enquete_id = kwargs.get('uuid', None)
        member_id = kwargs.get('member_id', None)

        # 対象のアンケートと回答者レコードを取得
        enquete_obj = models.Enquete.objects.get(enquete_id=enquete_id)
        member_obj = models.Member.objects.get(id=member_id)

        # アンケートの回答内容を保存
        self.IS_SUCCESS = update_enquete(enquete_obj, member_obj, request)

        # アンケートに紐づく質問を組み立て
        questions = assemble_questions(enquete_obj)

        member_form = forms.MemberForm()

        context_data = {
            'page_title': self.PAGE_TITLE,
            'enquete_obj': enquete_obj,
            'member_obj': member_obj,
            'questions': questions,
            'member_form': member_form,
            'is_success': self.IS_SUCCESS,
        }

        return render(request, 'enquete/enquete_answer_update.html', context_data)


class EnqueteTotalizeView(View):
    """
    アンケートの集計結果をグラフで表示する画面
    """

    def __init__(self):
        self.PAGE_TITLE = 'アンケート集計画面'

    def get(self, request, *args, **kwargs):
        """
        機能
        ・アンケートの回答ごとの集計結果をグラフで表示する
        """
        # 回答結果を集計する

        # アンケートidを取得
        enquete_id = kwargs.get('uuid', None)

        # 対象のアンケートを取得する
        enquete_obj = models.Enquete.objects.get(enquete_id=enquete_id)

        # アンケートに紐づく質問を取得
        eqs = enquete_obj.eq_set.all()

        # グラフ描画に必要なデータの組み立て
        graphs_data = assemble_data_for_totalize_graphs(eqs)

        print(graphs_data)
        context_data = {
            'page_title': self.PAGE_TITLE,
            'graphs_data': graphs_data,
            'enquete_obj': enquete_obj,
        }

        return render(request, 'enquete/enquete_totalize.html', context_data)
