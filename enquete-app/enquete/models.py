from django.db import models


class Enquete(models.Model):
    """
    アンケートテーブル
    項目:
        アンケートID: uuid4で払い出される
        アンケート名: アンケートの名前
    """
    enquete_id = models.CharField(max_length=512)
    enquete_name = models.CharField(max_length=512)

    def __str__(self):
        return self.enquete_name


class Question(models.Model):
    """
    質問テーブル
    項目:
        質問文: 質問の文章
        質問タイプ: テキスト・セレクトボックス・ラジオボタンのいずれか
    """
    question_text = models.CharField(max_length=512)
    question_type = models.CharField(max_length=512)

    def __str__(self):
        return '{} {}'.format(self.question_text, self.question_type)


class Choice(models.Model):
    """
    選択肢テーブル
    項目:
        選択肢名: セレクトボックス・ラジオボタンの質問の選択肢名
    """
    choice_name = models.CharField(max_length=512)

    def __str__(self):
        return self.choice_name


class Member(models.Model):
    """
    部員テーブル
    項目:
        部員名: アンケート回答をする部員名
    """
    member_name = models.CharField(max_length=512)

    def __str__(self):
        return self.member_name


class EQ(models.Model):
    """
    アンケートテーブルと質問テーブルの中間テーブル
    項目:
        アンケートオブジェクト: 外部キーとしてアンケートオブジェクトを保持
        質問オブジェクト: 外部キーとして質問オブジェクトを保持
    """
    E_obj = models.ForeignKey(Enquete, on_delete=models.CASCADE)
    Q_obj = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.E_obj.enquete_name, self.Q_obj.question_text)


class QC(models.Model):
    """
    質問テーブルと選択肢テーブルの中間テーブル
    項目:
        質問オブジェクト: 外部キーとして質問オブジェクトを保持
        選択肢オブジェクト: 外部キーとして選択肢オブジェクトを保持
    """
    Q_obj = models.ForeignKey(Question, on_delete=models.CASCADE)
    C_obj = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.Q_obj.question_text, self.C_obj.choice_name)


class QM(models.Model):
    """
    質問テーブルと部員テーブルの中間テーブル
    項目:
        質問オブジェクト: 外部キーとして質問オブジェクトを保持
        部員オブジェクト: 外部キーとして部員オブジェクトを保持
        回答内容: 質問項目に対する部員の回答内容を保持
    """
    Q_obj = models.ForeignKey(Question, on_delete=models.CASCADE)
    M_obj = models.ForeignKey(Member, on_delete=models.CASCADE)
    answer = models.CharField(max_length=512)

    def __str__(self):
        return '{} {}'.format(self.Q_obj.question_text, self.M_obj.member_name)
