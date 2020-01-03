from django.shortcuts import render
from django.views.generic import View
from django.core.paginator import Paginator

import uuid

from . import models
from . import forms


def make_color(color_num):
    """
    指定された数の色を作成する。
    虹の色と同じ配色になるようによしなに作成される
    Args:
        color_num (int): 作成する色の数を指定する
    Returns:
        RGBs (list): 色を表す16進数コードを要素に持つリスト
    """
    import colorsys
    HSV_tuples = [(x*1.0/color_num, 1.0, 1.0) for x in range(color_num)]
    RGBs = ['#%02x%02x%02x' % (int(x[0]*255), int(x[1]*255), int(x[2]*255))
            for x in list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))]
    return RGBs


def assemble_questions(enquete_obj):
    """
    対象のアンケートに紐づく質問項目を取得
    以下のようなdictを要素に持つリストを作成する
    questions = [
        {
            "question_text": 質問文,
            "question_form": 質問フォーム,
        },
        ...
    ]
    """
    ANSWER = 'answer'
    # フォームの組み立てに使用するテンプレートクラス
    FORM_TEMPLATE_OBJ = forms.CreateFormTemplate()

    eqs = enquete_obj.eq_set.all()
    questions = []
    for question_num, eq in enumerate(eqs, 1):

        question = {}

        # 質問文を取得
        question['question_text'] = eq.Q_obj.question_text

        # 質問項目のタイプによって作成するフォームを変更する
        # フォームの属性名を定義
        attr_name_str = ANSWER + str(question_num)
        if eq.Q_obj.question_type == 'text':

            # formを属性として追加し、動的にクラスを作成する
            # こうしないと動的にフォームを作成できない
            _form_attr = {
                attr_name_str: FORM_TEMPLATE_OBJ.create_text_form()
            }
            _AnswerForm_cls = type(
                'AnswerFrom', (forms.TextForm, ), _form_attr)

            question['question_form'] = _AnswerForm_cls()
            questions.append(question)

        elif eq.Q_obj.question_type == 'select':

            choices = []
            choices.append(forms.CreateFormTemplate.DEFAULT_CHOICE)

            # 質問項目に紐づく、選択肢のリストを作成する
            qcs = eq.Q_obj.qc_set.all()
            for qc in qcs:
                choice = (qc.C_obj.choice_name, qc.C_obj.choice_name)
                choices.append(choice)

            # formを属性として追加し、動的にクラスを作成する
            _form_attr = {
                attr_name_str: FORM_TEMPLATE_OBJ.create_select_form(
                    choices=choices)
            }
            _AnswerForm_cls = type(
                'AnswerForm', (forms.SelectForm, ), _form_attr)

            question['question_form'] = _AnswerForm_cls()
            questions.append(question)

        elif eq.Q_obj.question_type == 'radio':

            choices = []
            # choices.append(forms.CreateFormTemplate.DEFAULT_CHOICE)

            # 質問項目に紐づく、選択肢のリストを作成する
            qcs = eq.Q_obj.qc_set.all()
            for qc in qcs:
                choice = (qc.C_obj.choice_name, qc.C_obj.choice_name)
                choices.append(choice)

            # formを属性として追加し、動的にクラスを生成する
            _form_attr = {
                attr_name_str: FORM_TEMPLATE_OBJ.create_radio_form(
                    choices=choices)
            }
            _AnswerForm_cls = type(
                'AnswerForm', (forms.RadioForm, ), _form_attr)

            question['question_form'] = _AnswerForm_cls()
            questions.append(question)

        else:
            # TODO:エラー処理
            pass

    return questions


def assemble_questions_with_answer(enquete_obj, member_obj):
    """
    対象のアンケートに紐づく質問項目を取得
    以下のようなdictを要素に持つリストを作成する
    また初期値として、前回の回答内容を埋めてインスタンス化するï

    questions = [
        {
            "question_text": 質問文,
            "question_form": 質問フォーム,
        },
        ...
    ]
    """
    ANSWER = 'answer'
    # フォームの組み立てに使用するテンプレートクラス
    FORM_TEMPLATE_OBJ = forms.CreateFormTemplate()

    eqs = enquete_obj.eq_set.all()
    questions = []
    for question_num, eq in enumerate(eqs, 1):

        question = {}

        # 質問文を取得
        question['question_text'] = eq.Q_obj.question_text

        # 質問項目のタイプによって作成するフォームを変更する
        # フォームの属性名を定義
        attr_name_str = ANSWER + str(question_num)
        if eq.Q_obj.question_type == 'text':

            # formを属性として追加し、動的にクラスを作成する
            # こうしないと動的にフォームを作成できない
            _form_attr = {
                attr_name_str: FORM_TEMPLATE_OBJ.create_text_form()
            }
            _AnswerForm_cls = type(
                'AnswerFrom', (forms.TextForm, ), _form_attr)

            # 回答内容を取得
            qm_obj = models.QM.objects.get(Q_obj=eq.Q_obj, M_obj=member_obj)

            # 回答内容を初期値として設定
            initial = {
                attr_name_str: qm_obj.answer,
            }
            question['question_form'] = _AnswerForm_cls(initial=initial)
            questions.append(question)

        elif eq.Q_obj.question_type == 'select':

            choices = []
            choices.append(forms.CreateFormTemplate.DEFAULT_CHOICE)

            # 質問項目に紐づく、選択肢のリストを作成する
            qcs = eq.Q_obj.qc_set.all()
            for qc in qcs:
                choice = (qc.C_obj.choice_name, qc.C_obj.choice_name)
                choices.append(choice)

            # formを属性として追加し、動的にクラスを作成する
            _form_attr = {
                attr_name_str: FORM_TEMPLATE_OBJ.create_select_form(
                    choices=choices)
            }
            _AnswerForm_cls = type(
                'AnswerForm', (forms.SelectForm, ), _form_attr)

            # 回答内容を取得
            qm_obj = models.QM.objects.get(Q_obj=eq.Q_obj, M_obj=member_obj)

            # 回答内容を初期値として設定
            initial = {
                attr_name_str: qm_obj.answer,
            }
            question['question_form'] = _AnswerForm_cls(initial=initial)
            questions.append(question)

        elif eq.Q_obj.question_type == 'radio':

            choices = []
            # choices.append(forms.CreateFormTemplate.DEFAULT_CHOICE)

            # 質問項目に紐づく、選択肢のリストを作成する
            qcs = eq.Q_obj.qc_set.all()
            for qc in qcs:
                choice = (qc.C_obj.choice_name, qc.C_obj.choice_name)
                choices.append(choice)

            # formを属性として追加し、動的にクラスを生成する
            _form_attr = {
                attr_name_str: FORM_TEMPLATE_OBJ.create_radio_form(
                    choices=choices)
            }
            _AnswerForm_cls = type(
                'AnswerForm', (forms.RadioForm, ), _form_attr)

            # 回答内容を取得
            qm_obj = models.QM.objects.get(Q_obj=eq.Q_obj, M_obj=member_obj)

            # 回答内容を初期値として設定
            initial = {
                attr_name_str: qm_obj.answer,
            }
            question['question_form'] = _AnswerForm_cls(initial=initial)
            questions.append(question)

        else:
            # TODO:エラー処理
            pass

    return questions


def answer_enquete(enquete_obj, member_obj, request):
    """
    アンケートへの回答内容を保存する
    Args:
        enquete_obj (:obj:`model`): 対象アンケートのレコード
        member_obj (:obj:`model`): 回答者のレコード
        request (:obj:`HttpRequest`): Djangoのリクエストオブジェクト
    Returns:
        is_success (bool): 成功(True) or 失敗(False)
    """
    is_success = False

    # 回答を取得し、回答のリストを作成
    answers = []
    for k, v in request.POST.items():
        if 'answer' in k:
            answers.append(v)

    # アンケートに紐づく質問項目を取得
    eqs = enquete_obj.eq_set.all()
    for eq, answer in zip(eqs, answers):
        mq_obj = models.QM(
            Q_obj=eq.Q_obj,
            M_obj=member_obj,
            answer=answer,
        )
        mq_obj.save()

    is_success = True
    return is_success


def update_enquete(enquete_obj, member_obj, request):
    """
    アンケートへの回答内容を保存する
    Args:
        enquete_obj (:obj:`model`): 対象アンケートのレコード
        member_obj (:obj:`model`): 回答者のレコード
        request (:obj:`HttpRequest`): Djangoのリクエストオブジェクト
    Returns:
        is_success (bool): 成功(True) or 失敗(False)
    """
    is_success = False

    # 回答を取得し、回答のリストを作成
    answers = []
    for k, v in request.POST.items():
        if 'answer' in k:
            answers.append(v)

    # アンケートに紐づく質問項目を取得
    eqs = enquete_obj.eq_set.all()

    # アンケートの回答内容を更新する
    for eq, answer in zip(eqs, answers):
        qm_obj = models.QM.objects.get(Q_obj=eq.Q_obj, M_obj=member_obj)
        qm_obj.answer = answer
        qm_obj.save()

    is_success = True
    return is_success


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

        # 質問に対する回答を集計　以下の形で集計する
        # totalizes_data = [{
        #   "質問文": {
        #       "回答内容": 件数(int),
        #       "回答内容": 件数(int),
        #       }
        #   },
        #   ...
        # ]
        totalizes_data = []
        for eq in eqs:
            totalize_data = {}
            question_data = {}
            qms = eq.Q_obj.qm_set.all()
            for qm in qms:
                answer = qm.answer
                # 回答がなければ追加、あればカウントアップする
                if answer not in question_data:
                    question_data[answer] = 1
                else:
                    question_data[answer] = question_data[answer] + 1
                totalize_data[qm.Q_obj.question_text] = question_data

            totalizes_data.append(totalize_data)

        # 以下形のデータを作る
        # graphs_data = [{
        #   "question_text": str
        #   "labels": [],
        #   "data": [],
        #   "backgroundColor": [],
        #   },
        #   ...
        # ]
        graphs_data = []
        for totalize_data in totalizes_data:
            graph_data = {}
            question_text = ''
            labels = []
            data = []

            for question_text, question_data in totalize_data.items():
                question_text = question_text

                for k, v in question_data.items():
                    labels.append(k)
                    data.append(v)

            backgroundColor = make_color(len(labels))

            graph_data['question_text'] = question_text
            graph_data['labels'] = labels
            graph_data['data'] = data
            graph_data['backgroundColor'] = backgroundColor

            graphs_data.append(graph_data)

        print(graphs_data)
        context_data = {
            'page_title': self.PAGE_TITLE,
            'graphs_data': graphs_data,
            'enquete_obj': enquete_obj,
        }

        return render(request, 'enquete/enquete_totalize.html', context_data)
