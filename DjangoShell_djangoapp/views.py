'''
Created on May 26, 2019

@author: shanti
'''
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

class LandingView(TemplateView):
    template_name = 'DjangoShell_djangoapp/welcome.html'
    page_name = "WelcomePage"
    
class AboutTheProgramView(TemplateView):
    template_name = 'DjangoShell_djangoapp/about.html'
    page_name = 'AboutOurProgram'

class BravoView(TemplateView):
    template_name = 'DjangoShell_djangoapp/bravo.html'
    page_name = "WelcomePage"

def whereto(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('welcome')

    if user.is_active == True and user.is_authenticated:
        return redirect('bravo_page')