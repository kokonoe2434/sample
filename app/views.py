from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import dumps
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import get_template
from django.views import generic
from .forms import CustomUserCreateForm

from django.core.signing import BadSignature, SignatureExpired, loads
from django.http import HttpResponseBadRequest
from . import utils

from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm

User = get_user_model()


class UserCreate(generic.CreateView):
    """ユーザ登録"""
    template_name = 'user_create.html'
    form_class = CustomUserCreateForm

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super().get(request, **kwargs)

    def form_valid(self, form):
        # 仮登録
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # メール送信
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'user': user
        }
        subject_template = get_template('mail/subject.txt')
        message_template = get_template('mail/message.txt')
        subject = subject_template.render(context)
        message = message_template.render(context)
        user.email_user(subject, message)
        # return redirect('user_create_done')
        return redirect('http://127.0.0.1:8000/login/user_create/done/')


class UserCreateDone(generic.TemplateView):
    """仮登録完了"""
    template_name = 'user_create_done.html'

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super().get(request, **kwargs)


class UserCreateComplete(generic.TemplateView):
    """本登録完了"""
    template_name = 'user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60 * 60 * 24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')

        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoenNotExist:
            return HttpResponseBadRequest()

        if not user.is_active:
            # 問題なければ本登録とする
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.save()

            # QRコード生成
            request.session["img"] = utils.get_image_b64(utils.get_auth_url(user.email, utils.get_secret(user)))

            return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class CustomLoginView(LoginView):
    """ログイン"""
    form_class = CustomLoginForm
    template_name = 'login.html'

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super().get(request, **kwargs)