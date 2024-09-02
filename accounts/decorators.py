from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.contrib.auth import logout

def unauthenticated_user(view_func):             #pour y acceder que si on est pas connecte
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated :
            logout(request)
        return view_func(request, *args, **kwargs)
    
    return wrapper_func

#############################################################################

''' WHY 2 ALLOWED USERS??

    The first one is for students, people knows url of pages, they know that those urls exist, so it is normal to try
    accees them directly, that's why if they are not logged_in we redirect them on 'connexion' with the 
    login_required decorator before checking their group, and we continue BUT

    For admins, the urls are note known by the whole pupblic, so if someone just try to access them while he is not
    euthenticated, he go directly on 404, and possybly, he can be connected with a student 
    account, so he go 404 also, that's the purpose of second decorator. so we don't need login_required in administrations apps

'''


def allowed_users(allowed_roles=[]):          #pour gerer les groupes autorises dans django admin 
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            groups = request.user.groups.all()
            group_names = [group.name for group in groups]

            if not any(role in group_names for role in allowed_roles):
                return custom_404(request)

            return view_func(request, *args, **kwargs)

        return wrapper_func
    return decorator



def allowed_users_admin(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # Si l'utilisateur n'est pas connecté, rediriger vers la page d'erreur 404
                return custom_404(request)

            groups = request.user.groups.all()
            group_names = [group.name for group in groups]

            if not any(role in group_names for role in allowed_roles):
                return custom_404(request)

            return view_func(request, *args, **kwargs)

        return wrapper_func
    return decorator

#########################################################################################################


#This one is only for studentuserwithoutetudinat vue in students.views check there
def redirect_if_etudiant(view_func):        #verifier si l'utilisateur n'est pas relier a un etudiant
    def wrapper_func(request, *args, **kwargs):
        try:
            etudiant = request.user.etudiants
            return redirect('tableau_de_bord')  # Redirige vers le tableau de bord si l'objet Etudiants existe
        except Etudiants.DoesNotExist:
            return view_func(request, *args, **kwargs)  # Laisse l'exécution continuer vers la vue originale
    
    return wrapper_func




def custom_404(request):
    return render(request, 'students/404.html', status=404)