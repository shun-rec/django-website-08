# Djangoチュートリアル #8

## 実用的なテキスト置換サービスを作ってみよう

## 完成版プロジェクト

<https://github.com/shun-rec/django-website-08>

## 事前準備

### 新規プロジェクト

```py
django-admin startproject pj_form
```

### 新規アプリの作成

```py
cd pj_form
python manage.py startapp text_edit
```

### ドメインの許可

全体設定`pj_form/settings.py`の28行目を以下のように修正。

※これを追加しないとブラウザで開いた時に、「このドメインではアクセス出来ません。」というエラーが出ます。

```py
ALLOWED_HOSTS = ["*"]
```

### アプリを追加

同じく全体設定33行目の`INSTALLED_APPS`の配列の最後に`text_edit`アプリを追加。

※これを追加しないとdjangoがアプリのことを知らないので、「テンプレートが見つかりません。」というエラーが出ます。

```py
    'text_edit',
```

### ベースのテンプレートの作成

前回と同じく[Bootstrap 4](https://getbootstrap.com/docs/4.0/getting-started/introduction/)を使っています。

`text_edit/templates/base.html`

```html
<!doctype HTML>
<html>
    <head>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <a class="navbar-brand" href="/">テキスト置換</a>
        </nav>
        <div class="container mt-4">
        {% block main %}
        <p>※コンテンツがありません。</p>
        {% endblock %}
        </div>
    </body>
</html>
```

## FormViewを使って簡単にフォームを表示してみよう

### フォームを追加

`text_edit/forms.py` （新規作成）

```py
from django import forms


class TextForm(forms.Form):
    text = forms.CharField()
    search = forms.CharField()
    replace = forms.CharField()
```

モデルの作り方と似ていますが、これはあくまでフォームの表示用途だけです。  
DBに保存はされません。  
`CharField`でテキストを受け取るフォームが作れます。  
他にもモデルと同様に`IntegerField`、`DateTimeField`など多くのフィールドがデフォルトで用意されています。

### ビューを追加

```py
from django.views.generic.edit import FormView

from . import forms


class Index(FormView):
    form_class = forms.TextForm
    template_name = "index.html"
```

前回出てきた`CreateForm`と似ています。  
`CreateForm`はフォームを送信すると自動でDBにデータを保存してくれました。  
一方で`FormView`は勝手にDBに保存はしません。  
ユーザーから入力は受け取れますが、それをどう処理するかは自由にカスタマイズ出来ます。

### テンプレートを追加

`text_edit/templates/index.html`

```html
{% extends "base.html" %}
{% block main %}
<form method="post">
    {% csrf_token %}
    
    {{ form.as_p }}
    
    <input type="submit" value="変換" class="btn btn-info" />
</form>
{% endblock %}
```

* `{% csrf_token %}` - djangoでフォームを使うときのおまじないです。
* `{{ form.as_p }}` - フォームが表示されます。

### URLを設定

`pj_form/urls.py`を以下のように修正。

```
from django.urls import path

from text_edit import views

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
]
```

実はアプリのURL設定ではなく、全体のURL設定に直接追加することも出来ます。  
今回のような小さなプロジェクトではこちらの方が簡単です。

### 表示してみよう

サーバーを起動して、トップページにアクセスしてフォームが表示されていたらOKです。

サーバーの起動

```py
python manage.py runserver
```

## フォームのデータを処理しよう

実際にテキストを置換してユーザーに表示してみましょう。

### ビューにフォームの処理を追加

`text_edit/views.py`の`Index`クラスに以下を追記。

```py
    # フォームの入力にエラーが無かった場合に呼ばれます
    def form_valid(self, form):
        # form.cleaned_dataにフォームの入力内容が入っています
        data = form.cleaned_data
        text = data["text"]
        search = data["search"]
        replace = data["replace"]
        
        # ここで変換
        new_text = text.replace(search, replace)
        
        # テンプレートに渡す
        ctxt = self.get_context_data(new_text=new_text, form=form)
        return self.render_to_response(ctxt)
```

### テンプレートに変換後のテキストを表示

`text_edit/templates/index.html`を以下に変更。

```html
{% extends "base.html" %}
{% block main %}
<div class="row">
    <div class="col-sm">
        <h2>変換前</h2>
        <form method="post">
            {% csrf_token %}
            {{ form.as_p }}
            <input type="submit" value="変換" class="btn btn-info" />
        </form>  
    </div>
    <div class="col-sm">
        <h2>変換後</h2>
        <p>{{ new_text }}</p>
    </div>
</div>
{% endblock %}
```

* `row`や`col-sm`というのはBootstrapで簡単に2カラムのページを作れるクラスです
* `{{ new_text }}`に変換後のテキストが渡されます

### 変換を試してみよう

フォームに入力して、変換されたらOKです。

## バリデーション（入力エラーチェック）を追加しよう

テキストが5文字以下の場合はエラーとしましょう。

### フォームにバリデーションを追加

`text_edit/forms.py`に`ValidationError`のインポートを追加。

```py
from django.core.exceptions import ValidationError
```

このエラーはフォームで自動的に扱うことが出来て便利です。

`TextForm`クラスに以下を追加。

```py
    # 自動的に呼ばれます。エラーを発生させると簡単に表示できます
    def clean(self):
        # djangoもともとのバリデーションを実行してデータを取得
        data = super().clean()
        text = data["text"]
        if len(text) <= 5:
            raise ValidationError("テキストが短すぎます。")
            
        # 最後は必ずデータ全体を返します
        return data
```

### テンプレート

`text_edit/templates/index.html`の本文の一番上に以下を追加。

```html
{% for error in form.non_field_errors %}
<div class="alert alert-danger" role="alert">
  {{ error }}
</div>
{% endfor %}
```

### エラーを確認してみよう

フォームのテキストに5文字以下の文字を入力して送信するとピンクのエラーメッセージが表示されたらOKです。

※エラーが２つ表示されますが、後で修正しましょう。

## フォームの見た目を整えよう

### ラベルを変更しよう

`text_edit/forms.py`の`TextForm`クラスのフィールドを以下のように変更。

```py
    text = forms.CharField(label="")
    search = forms.CharField(label="検索")
    replace = forms.CharField(label="置換")
```

`label`でフォームが表示されるときのラベルを変更できます。

### 長文テキストを入力できるようにしよう

同じく`TextForm`の`text`フィールドを以下のように変更。

```py
    text = forms.CharField(widget=forms.Textarea, label="")
```

入力するデータの種類は同じでフォームの見た目だけを変えるときには`widget`を使用します。

### Bootstrapのクラスを追加して見た目をおしゃれにしよう

Bootstrapのクラスを設定してみましょう。  
djangoで作ったフォームに独自のHTMLを設定するのには、独自の`widget`を作成します。

#### ウィジェットの作成

`text_edit/forms.py`の`TextForm`の上に以下を追加。

```py
widget_textarea = forms.Textarea(
    attrs={
        "class": "form-control"
    }
)

widget_textinput = forms.TextInput(
    attrs={
        "class": "form-control"
    }
)
```

それぞれ独自のクラス`form-control`を追加したテキストエリアとテキストインプットです。  
この方法を知っておけば、`readonly`をつけて編集不可にしたりと色々なことが出来ます。

#### フォームに適用

`TextForm`の各フィールドに先程作ったウィジェットを使うように設定しましょう。

```py
    text = forms.CharField(label="", widget=widget_textarea)
    search = forms.CharField(label="検索", widget=widget_textinput)
    replace = forms.CharField(label="置換", widget=widget_textinput)
```

### 余分に出ているエラーを非表示にしよう

`text_edit/templates/index.html`の`{{ form.as_p }}`を以下のように変更します。

```html
            {% for field in form %}
            <p>
                <label>{{ field.label }}</label>
                {{ field }}
            </p>
            {% endfor %}
```

forループを使うことでフォームのフィールドを１つずつ表示することが出来ます。  

* `field.label` - ラベル
* `field` - 本体
* `field.errors` - エラー

今回は`field.errors`を書かないことでエラーを非表示にしています。

### 表示を確認しよう

変更したところの見た目が変わっていたらOKです。

## おまけ：ModelFormでモデルからフォームを自動生成しよう

モデルからフォームを自動で作成することが出来ます。  
前回使った`CreateView`でフォームをカスタマイズしたい時に便利な方法です。

### ベースとなるモデルを作成

`text_edit/models.py`に`Post`モデルを追加

```py
class Post(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
```

### `Post`モデルを使って`Post`用のフォームを自動生成

`text_edit/forms.py`の最後に以下を追加。

```
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body"]
```

`ModelForm`を使うことで、モデルと編集可能なフィールドを指定するだけでフォームが作成出来ます。

### ビューに適用

ここでは表示確認のために先程作成した`Index`のフォームを変えてみましょう。

`text_edit/views.py`の`form_class`を`forms.PostForm`に変更します。

```py
    form_class = forms.PostForm
```

### 表示を確認しよう

トップページにアクセスして、`Post`モデルがそのままフォームになっていればOKです。
