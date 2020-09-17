from django.views.generic.edit import FormView

from . import forms


class Index(FormView):
    form_class = forms.TextForm
    template_name = "index.html"
    
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