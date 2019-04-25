from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import pusher_get_jwt_token_response, pusher_create_user

from main_app.models import User


# Create your views here.
# login required to access this page. will redirect to admin login page.
@login_required()
def messenger(request):
    return render(request, "pusher_chat_app/messenger.html")


@login_required(login_url='/login/')
def chatbox(request):
    return render(request, "pusher_chat_app/chatbox.html")


@csrf_exempt
def ajax_jwtkey(request, userid):
    response = {}
    if not request.user.is_authenticated:
        response['error'] = "Error 400  user not  authenticated."
    else:
        response = pusher_get_jwt_token_response(userid)

    return JsonResponse(response, safe=False)


@login_required()
def ajax_get_user_infos(request,userid):

    user = get_object_or_404(User,id=userid)

    response = {}

    response['name'] = user.get_full_name()
    if user.profil.photo_profil.image:
        response['image'] = user.profil.photo_profil.image.url
    else:
        response['image'] = None

    return JsonResponse(response, safe=False)