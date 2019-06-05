from django import forms
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import  authenticate, get_user_model
from django.forms.widgets import PasswordInput, CheckboxSelectMultiple,\
    CheckboxInput, CheckboxChoiceInput
from django.utils.translation import ugettext_lazy as _
from localflavor.us.forms import USPhoneNumberField, USZipCodeField,\
    USStateSelect, USStateField
from django.forms.models import ModelChoiceField
from django.contrib.auth.models import Group
from datamodel.models import WBCSUser, ParticipantProfile, Clinic, RAProfile,\
    CallTime
from utils.models import Timezone

class AccountCreationForm ( forms.ModelForm ) :        
    def __init__( self, *args, **kwargs ) :
        self.request = kwargs.pop('request', None)
        super(AccountCreationForm, self).__init__(*args, **kwargs)
            
        for field in self.fields :
           self.fields[field].widget.attrs['class'] = 'form-control'
    
    email = forms.EmailField(label="Your Email:",
                                   widget=forms.EmailInput(attrs={'class': "form-control",
                                                                 'placeholder': ""}),
                                   required=True)
    
    password1 = forms.CharField( label = 'Password',
                                 widget = forms.PasswordInput(attrs={'class': "form-control form-group {%if field.errors %}error{%endif%}",
                                                                       'placeholder': "New password"}),
                                required=True)
    password2 = forms.CharField( label = 'Password confirmation', 
                                 widget = forms.PasswordInput(attrs={'class': "form-control form-group {%if field.errors %}error{%endif%}",
                                                                       'placeholder': "New password again"}),
                                required=True)         
    class Meta:
        model = WBCSUser
        fields = ('email',)
        
    def clean_email (self) :
        email = self.cleaned_data.get('email')
        if email is not None and email != '':
            try:
                user = WBCSUser.objects.get(email=email)
            except WBCSUser().DoesNotExist:
                return email
            raise forms.ValidationError(
                _("The email address provided is already registered."))
        return email     
    
    def clean ( self ) :
        cleaned_data = super(AccountCreationForm, self).clean()
        # Check that the two password entries match
        password1 = cleaned_data.get( "password1", None )
        password2 = cleaned_data.get( "password2", None )
        if password1 != password2:
            raise forms.ValidationError( "Passwords don't match" )
        
        return cleaned_data
                
    def save(self, commit = True):
        # Save the provided password in hashed format
        user = super( AccountCreationForm, self ).save( commit = False)
        
        user.set_password( self.cleaned_data[ "password1" ] )
        if commit:
            user.accountsetup_completed_date = timezone.now()
            user.save()
        return user

class ParticipantAccountCreationForm(AccountCreationForm):

    def __init__( self, *args, **kwargs ) :
        super(ParticipantAccountCreationForm, self).__init__(*args, **kwargs)
    
        self.fields['sms_phone'].required = True
        self.fields['sms_phone'].widget.attrs['placeholder'] = 'xxx-xxx-xxxx'
        
                         
    sms_phone = USPhoneNumberField(label="Your phone number:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': "xxx-xxx-xxxx"}),
                                     required=True)
    alternative_phone = USPhoneNumberField(label="Alternative phone number:",
                                 widget=forms.TextInput(attrs={'class': "form-control",
                                                                 'placeholder': "xxx-xxx-xxxx"}),
                                 required=True)
    first_name = forms.CharField(max_length=30, label="Your first name:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': ""}),
                                     required=True)
    last_name = forms.CharField(max_length=30, label="Your last name:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': ""}),
                                     required=True)

    def clean ( self ) :
        cleaned_data = super(ParticipantAccountCreationForm, self).clean()
        # Check that the two password entries match
        password1 = cleaned_data.get( "password1", None )
        password2 = cleaned_data.get( "password2", None )
        if password1 != password2:
            raise forms.ValidationError( "Passwords don't match" )
                
        return cleaned_data

    def save(self, commit = True):
        user = super( ParticipantAccountCreationForm, self ).save( commit = True)
        alternative_phone = self.cleaned_data.get('alternative_phone')
        sms_phone = self.cleaned_data.get('sms_phone')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')

        paarticipantprofile_dict = {
                    "alternative_phone" : alternative_phone,
                      "sms_phone" : sms_phone,
                      }
                 
        from account.views import create_participant_profile
        participantprofile = create_participant_profile(user, first_name, last_name, **paarticipantprofile_dict)
        return user

class RAAccountCreationForm(AccountCreationForm):
    
    first_name = forms.CharField(max_length=30, label="Your first name:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': ""}),
                                     required=True)
    last_name = forms.CharField(max_length=30, label="Your last name:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': ""}),
                                     required=True)

    def save(self, commit = True):
        user = super( RAAccountCreationForm, self ).save( commit = True)
        RA_group = Group.objects.get(name='RA')
        user.groups.add(RA_group)
        user.is_staff = True
        user.save()
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        RA = RAProfile(me=user, first_name=first_name, last_name=last_name)
        RA.save()

        return user
    
class AccountUpdateForm ( forms.ModelForm ) :        
    class Meta:
        model = WBCSUser
        fields = ('email',)
    
    def clean_confirm_email(self):
        email = self.cleaned_data.get('email', None)
        confirm_email = self.cleaned_data.get('confirm_email', None)
        if email and confirm_email:
            if email != confirm_email:
                raise forms.ValidationError(_("The two email fields didn't match."))
            else:
                try:
                    WBCSUser.objects.get(email=email)
                except:
                    return email
                raise forms.ValidationError(_("This email already exists"))
            
        if email and not confirm_email:  
            if email != self.instance.email:
                raise forms.ValidationError(_("The two email fields didn't match."))
            
        return confirm_email

    
    def save(self, commit = True):
        user = super( AccountUpdateForm, self ).save( commit = True)
        email = self.cleaned_data["email"]
        if email:
            user.email = email
            user.save()
        return user
    
class RAAccountUpdateForm(AccountUpdateForm):

            
    first_name = forms.CharField(max_length=30, label="RD first name:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': ""}),
                                     required=True)
    last_name = forms.CharField(max_length=30, label="RD last name:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': ""}),
                                     required=True)
    
    def __init__(self, *args, **kwargs):
        super(RAAccountUpdateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.instance.raprofile.first_name
        self.fields['last_name'].initial = self.instance.raprofile.last_name

    def save(self, commit = True):
        user = super( RAAccountUpdateForm, self ).save( commit = True)
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
 

        raprofile = user.raprofile
        ra_data_dict = {"me":user, "first_name": first_name, "last_name": last_name}
        for (key, value) in ra_data_dict.items():
                setattr(raprofile, key, value)
        raprofile.save()
        return user
    
class ParticipantAccountUpdateForm(AccountUpdateForm):

    first_name = forms.CharField(max_length=30, label="Parent first name:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': ""}),
                                     required=True)
    last_name = forms.CharField(max_length=30, label="Parent last name:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': ""}),
                                     required=True)
    alternative_phone = USPhoneNumberField(label="Alternative phone number:",
                                 widget=forms.TextInput(attrs={'class': "form-control",
                                                                 'placeholder': "xxx-xxx-xxxx"}),
                                 required=True)       
    sms_phone = USPhoneNumberField(label="Parent phone number:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': "xxx-xxx-xxxx"}),
                                   required=False)
    preferred_call_times = forms.ModelMultipleChoiceField(
                                queryset=CallTime.objects.all(),
                                label=_("Preferred times for phone call (check all that apply)"),
                                widget=forms.CheckboxSelectMultiple(), required=False)
    
    def __init__(self, *args, **kwargs):
        super(ParticipantAccountUpdateForm, self).__init__(*args, **kwargs)
        self.fields['alternative_phone'].initial = self.instance.participantprofile.alternative_phone
        self.fields['sms_phone'].initial = self.instance.participantprofile.sms_phone
        self.fields['first_name'].initial = self.instance.participantprofile.first_name
        self.fields['last_name'].initial = self.instance.participantprofile.last_name
        self.fields["preferred_call_times"].initial = \
        [t.pk for t in self.instance.participantprofile.preferred_call_times.all()]
        
    def save(self, commit = True):
        user = super( ParticipantAccountUpdateForm, self ).save( commit = True)
        alternative_phone = self.cleaned_data.get( "alternative_phone" )
        sms_phone = self.cleaned_data.get('sms_phone')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        participantprofile = user.participantprofile
        parent_data_dict = {"me":user, "alternative_phone": alternative_phone, "sms_phone": sms_phone, "first_name": first_name, "last_name": last_name}
        for (key, value) in parent_data_dict.items():
                setattr(participantprofile, key, value)
        preferred_call_times = self.cleaned_data.get('preferred_call_times')
        for pct in preferred_call_times:
            participantprofile.preferred_call_times.add(pct)
        participantprofile.save()
        return user
    
class PersonalAccountUpdateForm(AccountUpdateForm):
    
    confirm_email = forms.EmailField(max_length=200)
    
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    
    password2 = forms.CharField(label=_("Re-enter password:"), widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super(PersonalAccountUpdateForm, self).__init__(*args, **kwargs)
        self.fields['confirm_email'].required = False
        self.fields['password1'].required = False
        self.fields['password2'].required = False
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        if password1 and not password2:  
            if not self.instance.check_password(password1):
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2
    
    def clean(self):
        cleaned_data = super(PersonalAccountUpdateForm, self).clean()
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirm_email")

        if email and confirm_email:
        # Only do something if both fields are valid so far.
            if email != confirm_email:
                raise forms.ValidationError("Emails do not match.")

        return cleaned_data
    
    def save(self, commit = True):
        user = super( PersonalAccountUpdateForm, self ).save( commit = True)
        password1 = self.cleaned_data["password1"]
        if password1:
            user.set_password(password1)
            user.save()
        return user
    
class ParticipantPersonalAccountUpdateForm(PersonalAccountUpdateForm):

      
    first_name = forms.CharField(max_length=30, label="First name:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': ""}),
                                     required=True)
    last_name = forms.CharField(max_length=30, label="Last name:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': ""}),
                                     required=True)
        
    alternative_phone = USPhoneNumberField(label="Primary phone number:",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': "xxx-xxx-xxxx"}),
                                     required=True)
    sms_phone = USPhoneNumberField(label="If you would like to receive text reminders, please enter your cell phone number (this could be the same as your primary phone number)",
                                     widget=forms.TextInput(attrs={'class': "form-control",
                                                                     'placeholder': "xxx-xxx-xxxx"}),
                                     required=False)

    preferred_call_times = forms.ModelMultipleChoiceField(
                                queryset=CallTime.objects.all(),
                                label=_(" Preferred times to be contacted by phone"),
                                widget=forms.CheckboxSelectMultiple(), required=False)
    
    def __init__(self, *args, **kwargs):
        super(ParticipantPersonalAccountUpdateForm, self).__init__(*args, **kwargs)
#         self.fields['password1'].required = False
#         self.fields['password2'].required = False
        self.fields['sms_phone'].initial = self.instance.participantprofile.sms_phone
        self.fields['alternative_phone'].initial = self.instance.participantprofile.alternative_phone
        self.fields['first_name'].initial = self.instance.participantprofile.first_name
        self.fields['last_name'].initial = self.instance.participantprofile.last_name
        self.fields["preferred_call_times"].initial = \
        [t.pk for t in self.instance.participantprofile.preferred_call_times.all()]

    def save(self, commit = True):
        user = super( ParticipantPersonalAccountUpdateForm, self ).save( commit = True)
        participantprofile = user.participantprofile
        participant_data_dict = {"me":user, 
                            "sms_phone": self.cleaned_data.get('sms_phone'), 
                            "first_name": self.cleaned_data.get('first_name'), 
                            "last_name": self.cleaned_data.get('last_name'),
                            "alternative_phone": self.cleaned_data.get('alternative_phone'),
                            }
        for (key, value) in participant_data_dict.items():
                setattr(participantprofile, key, value)

        participantprofile.save()
        preferred_call_times = self.cleaned_data.get('preferred_call_times')
        for pct in preferred_call_times:
            participantprofile.preferred_call_times.add(pct)
        return user

class InitialParticipantPersonalAccountUpdateForm(ParticipantPersonalAccountUpdateForm):
    def __init__(self, *args, **kwargs):
        super(InitialParticipantPersonalAccountUpdateForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = True
        self.fields['password2'].required = True
        self.fields['confirm_email'].required = True
#         self.fields['password1'].help_text = '*'
#         self.fields['password2'].help_text = '*'
#         self.fields['confirm_email'].help_text = '*'

    def save(self, commit = True):
        user = super( InitialParticipantPersonalAccountUpdateForm, self ).save( commit = True)
        user.accountsetup_completed_date = timezone.now()
        user.save()
        return user


''' Authentication Forms: '''
class UserAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_("E-mail"), max_length=254)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'] % {
                        'username': self.username_field.verbose_name
                    })
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        return self.cleaned_data