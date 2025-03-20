from django.urls import path
from .view.authentication import (signup, login, logout, user_detail)
from .view.slambooks import slambook_view, slambook_single_view, get_url_slambook, get_slambook_by_url
from .view.questions import question_single_view, question_option_view, question_view, question_option_single_view
from .view.responses import response_list_create, submit_slambook_response, upload_image, response_answers, get_image
from .view.export import export_slambook_responses

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('user/', user_detail, name='user-detail'),
    path('slambook/', slambook_view, name='slambooks'),
    path('slambook/<uuid:slamid>/', slambook_single_view, name='slambook'),
    path('slambook/<uuid:slamid>/question', question_view, name='question'),
    path('slambook/<uuid:slamid>/question/<uuid:questionid>', question_single_view,
         name='question update, get, delete'),
    path('slambook/<uuid:slamid>/question/<uuid:questionid>/option', question_option_view,
         name='qn option'),
    path('slambook/<uuid:slamid>/question/<uuid:questionid>/option/<uuid:optionid>',
         question_option_single_view, name='qn options'),
    path('responses/<uuid:slamid>/', response_list_create, name='response-list-create'),
    path('slambook/<uuid:slamid>/share',get_url_slambook, name='share url' ),
    path('slam/<uuid:urlid>/', get_slambook_by_url, name='get-slambook-by-url'),
    path('slam/<uuid:urlid>/submit/', submit_slambook_response, name='submit-slambook-response'),
    path('upload/', upload_image, name='upload-image'),
    path('responses/<uuid:responseid>/answers/', response_answers, name='response-answers'),
    path('image/<str:filename>/', get_image, name='get-image'),
    path('slambook/<str:slamid>/export/', export_slambook_responses, name='export_slambook_responses'),
]
