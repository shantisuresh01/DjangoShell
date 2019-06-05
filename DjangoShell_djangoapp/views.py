'''
Created on May 26, 2019

@author: shanti
'''
from django.views.generic.base import TemplateView

class LandingView(TemplateView):
    template_name = 'DjangoShell_djangoapp/welcome.html'
    page_name = "WelcomePage"
    
class AboutTheProgramView(TemplateView):
    template_name = 'DjangoShell_djangoapp/about.html'
    page_name = 'AboutOurProgram'
    
def whereto(request):
    user = request.user
    if user.is_active == True:
        return redirect('landing_page')