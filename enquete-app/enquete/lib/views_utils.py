# viewsで使用する関数郡
import uuid
import colorsys

from enquete import forms
from enquete import models


def assemble_data_for_totalize_graphs(eqs):
    """
    グラフ描画に必要なデータの組み立てを行う
    Args:
        eqs (:obj:`EQ`): アンケートに紐づく質問レコードのリスト
    Returns:
        graphs_data (list): グラフ描画用に整形したデータのリスト
    """
    totalizes_data = _totalize_question(eqs)
    graphs_data = _create_praphs_data(totalizes_data)
    return graphs_data


def _totalize_question(eqs):
    """
    質問に対する回答を集計　以下の形で集計する
    totalizes_data = [{
      "質問文": {
          "回答内容": 件数(int),
          "回答内容": 件数(int),
          }
      },
      ...
    ]
    Args:
        eqs (:obj:`EQ`): アンケートに紐づく質問レコードのリスト
    Returns:
        totalizes_data (list): 質問に対する回答を集計したリスト
    """
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

    return totalizes_data


def _create_praphs_data(totalizes_data):
    """
    グラフ描画用に以下形のデータを作る
    graphs_data = [{
      "question_text": str
      "labels": [],
      "data": [],
      "backgroundColor": [],
      },
      ...
    ]
    Args:
        totalizes_data (list): 質問に対する回答を集計したリスト
    Returns:
        graphs_data (list): グラフ描画用に整形したデータのリスト
    """
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
    return graphs_data


def make_color(color_num):
    """
    指定された数の色を作成する。
    虹の色と同じ配色になるようによしなに作成される
    Args:
        color_num (int): 作成する色の数を指定する
    Returns:
        RGBs (list): 色を表す16進数コードを要素に持つリスト
    """
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
