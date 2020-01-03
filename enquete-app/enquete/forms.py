from django import forms

from . import models

select_data = [
    ('none', '選択してください'),
    ('text', 'テキストボックス'),
    ('select', 'セレクトボックス'),
    ('radio', 'ラジオボタン'),
]


class CreateFormTemplate(object):
    """
    動的にフォームを作成する際に使用する、設定をまとめたクラス
    """
    DEFAULT_CHOICE = ('none', '選択してください')

    def create_text_form(self, max_length=512):
        """
        テキスト形式のフォーム属性を用意する
        Args:
            max_length (int): 最大文字長
        """
        text_form = forms.CharField(
            max_length=max_length
        )
        return text_form

    def create_select_form(self, choices=None):
        """
        セレクトボタン形式のフォーム属性を用意する
        Args:
            choices (list): 選択肢のタプルのリスト
        """
        select_form = forms.ChoiceField(
            choices=choices,
        )
        return select_form

    def create_radio_form(self, choices=None):
        """
        ラジオボタン形式のフォーム属性を用意する
        Args:
            choices (list): 選択肢のタプルのリスト
        """
        radio_form = forms.ChoiceField(
            choices=choices,
            widget=forms.RadioSelect(),
        )
        return radio_form


class CreateEnqueteForm(forms.Form):
    """
    アンケート作成画面の入力フォーム

    Attributes:
        enquete_name (:obj:`form`): アンケート名を入力するフォーム
        question_text (:obj:`form`): 質問文を入力するフォーム
    """

    def __init__(self, *args, **kwargs):
        """
        bootstrap用にform-controlクラスを追加
        """
        super(CreateEnqueteForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    enquete_name = forms.CharField(
        label='アンケートタイトル',
        max_length=512,
        required=False,
    )
    question_text = forms.CharField(
        label='質問文',
        max_length=512,
        required=False
    )
    question_type = forms.ChoiceField(
        label='回答タイプ',
        choices=select_data,
        required=False,
    )
    choice_name = forms.CharField(
        label='選択肢',
        required=False,
        max_length=512,
    )


class MemberForm(forms.Form):
    """
    アンケート回答画面にて、回答者を選択するフォーム
    Attributes:
        member_name (:`obj`:form): アンケートの回答者を選択するフォーム
    """

    def __init__(self, *args, **kwargs):
        """
        bootstrap用にform-controlクラスを追加
        """
        super(MemberForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    member_name = forms.ModelChoiceField(
        label='回答者',
        queryset=models.Member.objects.all(),
        empty_label='回答者を選択してください',
    )


class TextForm(forms.Form):
    """
    アンケート回答画面にて使用する、text形式のフォーム
    answer属性は動的に生成する。

    Attributes:
        answer (:`obj`:form): テキスト形式の回答フォーム
    """

    def __init__(self, *args, **kwargs):
        """
        bootstrap用にform-controlクラスを追加
        """
        super(TextForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class SelectForm(forms.Form):
    """
    アンケート回答画面にて使用する、select形式のフォーム
    answer属性は動的に生成する。

    Attributes:
        answer (:`obj`:form): テキスト形式の回答フォーム
    """

    def __init__(self, *args, **kwargs):
        """
        bootstrap用にform-controlクラスを追加
        """
        super(SelectForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class RadioForm(forms.Form):
    """
    アンケート回答画面にて使用する、radio形式のフォーム
    answer属性は動的に生成する。

    Attributes:
        answer (:`obj`:form): テキスト形式の回答フォーム
    """

    def __init__(self, *args, **kwargs):
        """
        bootstrap用にform-controlクラスを追加
        """
        super(RadioForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-check-input"
