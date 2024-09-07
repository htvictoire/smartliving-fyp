

from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import  Group
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect



from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy , reverse
from django.views import View
from .models import User, Favorites, Messages
from gpio.models import Places, Pins, Board
from gpio.chekers import check_antity_manager, check_place_manager

from .forms import *
from .decorators import *

Users = get_user_model # dont touch this dude



from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode







def get_nav_bar(user, board):

    places = []

    userplaces = user.places.all()

    userantities = user.boards.all()

    userpins = user.pins.all()


    ######

    places.extend(userplaces)

    places_from_boards = []
    for brd in userantities:
        if brd.place not in userplaces:
            places.append(brd.place) if brd.place not in places else None
            places_from_boards.append(brd.place)
        
    places_from_pins = []
    for pin in userpins:
        if pin.board.place not in userplaces:
            places_from_pins.append(pin.board.place)
            if pin.board.place not in places_from_boards :
                places.append(pin.board.place) if pin.board.place not in places else None
                                  

    active_place = None

    if board is not None:
        active_place = board.place
        

    for pl in places:
        pl.antities = []
        pl.is_active = False
        
        if pl == active_place:
            pl.is_active = True

        if pl in userplaces:
            pl.antities = Board.objects.filter(place=pl)
        if pl in places_from_boards:
            pl.antities.extend(user.boards.filter(place=pl))
        if pl in places_from_pins:
            for p in user.pins.filter(board__place=pl):
                pl.antities.append(p.board) if p.board not in pl.antities else None
     

    ##### 
    
    all_boards = []
    all_boards.extend(Board.objects.filter(place__in = userplaces))
    all_boards.extend([b for b in userantities if b not in all_boards])

    all_pins = []
    all_pins.extend(Pins.objects.filter(board__place__in = userplaces))
    all_pins.extend([p for p in Pins.objects.filter(board__in = userantities) if p not in all_pins])
    all_pins.extend([p for p in userpins if p not in all_pins])

    
    context = {
        "board": board,
        "places" : places,
        "userplaces": userplaces,
        "all_boards" : all_boards,
        "all_pins" : all_pins,
        "pl_num" : len(userplaces),
        "brd_number": len(all_boards),
        "pn_number": len(all_pins),
        
    }  

    return context,


def get_fav_bar(user): 
    fav_pins = [f.pin for f in Favorites.objects.filter(user=user).order_by('-update_time')[0:5]]
    for pin in fav_pins:
        checker, checkerr = check_antity_manager(user=user, antity=pin.board) , check_place_manager(user=user, place=pin.board.place)
        if checker == True or checkerr == True:
            pin.manager = True

    return fav_pins



def get_messages(user):
    messages = [m for m in Messages.objects.filter(recipient=user).order_by('created_at')]
    return messages




def dashboard(request):
    user = request.user
    nav_context = get_nav_bar(user=user, board=None)
    fav_pins = get_fav_bar(user)
    title = 'Dashboard'
    description = ''
    messages = get_messages(user)
    
    for m in messages:
        print(m.message)

    if isinstance(nav_context, tuple):
        nav_context = nav_context[0]
        
    context = {
        "dashboard": True,
        "fav_pins": fav_pins,
        'title' : title,
        'description' : description,
        'messages' : messages,
    }

    context.update(nav_context)

    return render(request, 'accounts/main.html', context)

    



def depannage(request):
    form = SignUpForm()
    mail_envoye = False

    if request.method == 'POST':
        form = SignUpForm(request.POST)


        if form.is_valid() : 
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            # Ajoute l'utilisateur au groupe approprié , here Etudiants
            student_group = Group.objects.get(name='Etudiants')
            user.groups.add(student_group)
            
            messages.success(request, 'Compte enregistré avec Succès')
            return redirect('depannage')

    else:
        form = SignUpForm()    

    context = {
        'form': form,
        'mail_envoye': mail_envoye
    }
    return render(request, 'accounts/signup.html', context)















UserModel = get_user_model()
from .tokens import account_activation_token



##############################################################################################################

@unauthenticated_user
def register(request):
    form = SignUpForm()
    mail_envoye = False


    if request.method == 'POST':
        form = SignUpForm(request.POST)

        st_email = request.POST.get('email')

        nos_mails = User.objects.all().values('email')

        if st_email in nos_mails:
            messages.error(request, 'This email address is already registered')
            return redirect('register')

        if form.is_valid(): 
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('accounts/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            mail_envoye = True
      
    else:
        form = SignUpForm()
        

    context = {
        'form': form,
        'mail_envoye': mail_envoye
    }
    return render(request, 'accounts/signup.html', context)





def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token): 
        if user.is_active :
            messages.info(request, "This account is already activated")
            return redirect('login')
        else:
            user.is_active = True  
            user.save()       
        messages.success(request, "Your account have been succefully activated")
        return redirect('login')
    
    else:
        messages.error(request, "This activation link is not eligible anymore, please request for another")
        return redirect('login')





############################################################################################################



from django.contrib.auth.views import PasswordResetView
from django.utils.translation import gettext as _

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/passwordreset.html'
    

    @method_decorator(csrf_protect)
    @method_decorator(unauthenticated_user)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):

        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": 'accounts/password_reset_email.html',
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }

        form.save(**opts)  # Appel de la méthode form.save() de la classe mère

        return render(self.request, self.template_name, {'show_popup' : True})




class CustomPasswordResetConfirmView(PasswordResetConfirmView):  # utilise aussi if valid link dans le template
    template_name = 'accounts/passwordresetform.html'
    success_url = reverse_lazy('password_reset_complete')  # sans impact cer we show_popup only
    form_class = CustomSetPasswordForm


    def form_valid(self, form):
        
        # Vérification du numéro etudiant
        user = form.user

        form.save()

        return render(self.request, self.template_name, {'show_popup' : True})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = messages.get_messages(self.request)
        return context
    
   


#################################################################################################



def sign_in(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember")

        next_url = request.GET.get("next", None)
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                if not remember_me:
                    request.session.set_expiry(0)

                login(request, user)
                return redirect(next_url or'dashboard')  
            else:
                resend_activation_link = reverse('resend_activation_email', kwargs={'user_id': user.id})  
                messages.error(request, "Your account is not active. <a href='{}'>Resend activation url</a>.".format(resend_activation_link))
                         
        else:
            messages.error(request,"Incorrect Login Informations")
        
    return render(request , "accounts/login.html")




Users = get_user_model
UserModel = get_user_model()

from accounts.models import User

def resend_activation_email(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        if not user.is_active and user.groups.filter(name='Etudiants').exists():
            if user.verification_requests < 3:
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('accounts/acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                email = EmailMessage(
                    mail_subject, message, to=[user.email]
                )
                email.send()

                user.verification_requests += 1  # Incremente le nombre de demandes
                user.save()
                messages.info(request, "Un nouvel email de confirmation a été envoyé.")
                return redirect('connexion')

            else: 
                messages.error(request, "Vous avez atteint le nombre maximum de demandes d'email de vérification, Si vous avez besoin d'aide, contacter les servises informatiques.")
                return redirect('connexion')
        else:
            messages.error(request, "Impossible d'envoyer un nouvel email de confirmation.")
            return redirect('connexion')
    except User.DoesNotExist:
        messages.error(request, "Vous n'avez pas encore créer un compte.")
    
    return redirect('connexion') 





@login_required(login_url='connexion')
@allowed_users(allowed_roles=['Etudiants'])
def logout_etudiants(request):
    logout(request)
    return redirect('connexion')


######################################### NOW STAFF , NO SIMILAR TO STUDENTS DUE TO SECUriTITY MANAGEMENT


@unauthenticated_user
def create_user_staff(request):      # only user will be created , staff profile, will be done administrationally
    form = SignUpForm()
    mail_envoye = False

    if request.method == 'POST':
        form = SignUpForm(request.POST)


        if form.is_valid() : 
            user = form.save(commit=False)
            user.is_active = True
            user.admin = True
            user.save()
            # Ajoute l'utilisateur au groupe approprié , here Personnel
            staff_group = Group.objects.get(name='Personnel')
            user.groups.add(staff_group)

            '''
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('accounts/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            mail_envoye = True
            '''
            messages.success(request, 'Compte enregistré avec Succès')
            return redirect('staff_signup')
    else:
        form = SignUpForm()    

    context = {
        'form': form,
        'mail_envoye': mail_envoye
    }
    return render(request, 'accounts/signup.html', context)
     





@unauthenticated_user
def login_staff(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember")

        next_url = request.GET.get("next", None)
        user = authenticate(username=username, password=password)
        
        if user is not None and user.groups.filter(name='Personnel').exists():
            if user.is_active:
                if not remember_me:
                    request.session.set_expiry(0)

                login(request, user)
                return redirect(next_url or'dashboard')  
            else:
                resend_activation_link = reverse('resend_activation_email', kwargs={'user_id': user.id})  
                messages.error(request, "Votre compte n'est pas actif. <a href='{}'>Redemander le lien d'activation</a>.".format(resend_activation_link))
                         
        else:
            messages.error(request,"Informations d'identification incorrectes")
        
    return render(request , "accounts/login.html")


@allowed_users_admin(allowed_roles=['Personnel'])
def logout_staff(request):
    return redirect('login')





def contacts(request):
    
    personnel = 'vicky'
    
    try:
        if request.method == 'POST':
            subject = request.POST['subject']
            message_sent = request.POST['message']

            message = f'{message_sent} \n\n  Ce mail a été envoyé par {personnel} '
            send_mail(
            subject,
            message, 
            settings.EMAIL_HOST_USER,
            [settings.SUPPORT_EMAIL], 
            fail_silently=False)
        return render(request, 'accounts/contacts.html')
    except:
            messages.error(request, 'Une erreur s\'est produite. Veuillez reessayer.')
            return render(request, 'accounts/contacts.html')
    



