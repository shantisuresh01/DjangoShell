"""BMi2_djangoapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.contrib.auth import views as auth_views

from account.views import WBCSUserDetailsView, WBCSUserListView,\
    WBCSUserDeactivateView, WBCSUserPersonalUpdateView, password_reset_complete
from account.views import reset_password, \
    reset_password_confirm, reset_password_done, reset_password, WBCSUserCreateView, \
    WBCSUserUpdateView
from django.conf.urls import patterns, url
from django.conf import settings
from django.views.decorators.cache import never_cache
from account.forms import ParticipantAccountCreationForm, \
ParticipantAccountUpdateForm, ParticipantPersonalAccountUpdateForm,\
    RAAccountUpdateForm, RAAccountCreationForm,\
    InitialParticipantPersonalAccountUpdateForm
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('account.views',
     
    url(r'^participantsetup/$', never_cache(WBCSUserCreateView.as_view(form_class=ParticipantAccountCreationForm)), name="participantsetup"),

    url(r'^update/$', never_cache(WBCSUserUpdateView.as_view()), name="update"),
    url(r'^participantupdate/$', never_cache(WBCSUserUpdateView.as_view(form_class=ParticipantAccountUpdateForm)), name="participantupdate"),
    url(r'^participantupdate/(?P<pk>\d+)$', never_cache(WBCSUserUpdateView.as_view(form_class=ParticipantAccountUpdateForm)), name="participantupdate"),
    url(r'^raupdate/(?P<pk>\d+)$', never_cache(WBCSUserUpdateView.as_view(form_class=RAAccountUpdateForm)), name="raupdate"),
    url(r'^rasetup/$', never_cache(WBCSUserCreateView.as_view(form_class=RAAccountCreationForm)), name="rasetup"),
    url(r'^profile/(?P<pk>\d+)$', never_cache(WBCSUserPersonalUpdateView.as_view(form_class=ParticipantPersonalAccountUpdateForm)), name="participantpersonalupdate"),
    url(r'^profile/initial/(?P<pk>\d+)$', never_cache(WBCSUserPersonalUpdateView.as_view(form_class=InitialParticipantPersonalAccountUpdateForm)), name="initialparticipantpersonalupdate"),
    url(r'^profile_updated/$', never_cache(TemplateView.as_view(template_name="account/profile_updated.html")), name="profileupdated"),
    url(r'^list/(?P<usertype>.*)$', never_cache(WBCSUserListView.as_view()), name="list"),
    url(r'^delete/(?P<pk>\d+)$', never_cache(WBCSUserDeactivateView.as_view()), name='deactivate'),
    
    url(r'^password-reset/$', auth_views.password_reset, {
        'template_name': 'account/password_reset_form.html',
        'email_template_name': 'account/password_reset_email.html',
        'post_reset_redirect': reverse_lazy('account:reset_password_done'),
    }, name="reset_password"),
    url(r'^password-reset-sent/$', auth_views.password_reset_done, {
        'template_name': 'account/password_reset_done.html',
    }, name="reset_password_done"),
    url(r'^password-reset-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)$',
        'password_reset_confirm', {
            'template_name': 'account/password_reset_confirm.html',
            'post_reset_redirect':
                reverse_lazy('account:password-reset-complete'),
        }, name="password_reset_confirm"),
    url(r'^password-reset-complete/$', auth_views.password_reset_complete, {
        'template_name': 'account/password_reset_complete.html',
    }, name="password-reset-complete"),
)
