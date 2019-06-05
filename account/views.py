import uuid
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.models import Group

def reset_password_confirm(request, uidb64=None, token=None):
    return password_reset_confirm(request, template_name='account/password_reset_confirm.html',
        uidb64=uidb64, token=token, post_reset_redirect=settings.LOGIN_URL)

def reset_password(request):
    current_site = get_current_site(request)
    current_domain = current_site.domain
    
    return password_reset(request, 
        from_email='WBCS Support <support@%s>' % (current_domain,),
        subject_template_name='account/password_reset_subject.txt',
        template_name='account/password_reset_form.html',
        email_template_name='account/password_reset_email.html',
        post_reset_redirect=reverse('account:reset_password_done'),
        extra_context = {'settings': settings})

def reset_password_done(request):
    return render_to_response(template_name='account/password_reset_done.html')

def password_reset_complete(request):
        return render_to_response(template_name='account/password_reset_complete.html')

@staff_login_required
def create_participant_profile(request, user, **kwargs):
    ''' given a user object, create a participant profile, add user to 
        appropriate groups'''
    me = user
    participant_group = Group.objects.get(name='Participant')
    me.groups.add(participant_group)

    participantprofile = ParticipantProfile.objects.create(me=me, 
                           **kwargs
                           )
    participantprofile.save()
    survey_info=SurveyInfo(participant=participantprofile)
    survey_info.save()
    return participantprofile
        
@staff_login_required
def create_participant_login(request, clinic):
    ''' create data; create WBCSUser,  create ParentProfile, create List '''

    code = WBCSAccessCode.new_code().accesscode   
  
    user_dict = {
             "email": code,}
    
    participant = get_user_model().objects.create_user(**user_dict)
    
    participant_group = Group.objects.get(name="Participant")
    participant.groups.add(participant_group)
    accesscode_dict = {
        "user": participant,
        "code": code,
        "clinic": clinic}
    ac = AccessCode.objects.create(**accesscode_dict)    


    wbcs_participant_dict = {"user": participant,
                        "clinic": clinic}
    participantprofile = create_participant_profile(request, **wbcs_participant_dict)
    return participantprofile


