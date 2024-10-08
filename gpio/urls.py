from django.urls import path
from . import views
from .views import (PinsView,
                   CreatePinView,
                   ManagePinView,
                   AntitiesView,
                   CreateAntityView,
                   ManageAntityView, SendMessageView,
                   PlacesView, MyMessagesView,
                   ManagePlaceView, CreatePlaceView)


urlpatterns = [
    path('outputs_state/<str:board_code>/', views.etat_outputs, name='outputs_state'),
    path('output_create/', views.handle_output_create, name='output_create'),
    path('messages/', MyMessagesView.as_view(), name='messages'),
    path('send_message/', SendMessageView.as_view(), name='sendmessage'),
    path('update_messages/<int:message_id>/', views.update_messages, name='update_messages'),

    path('receive/messages/', views.receive_messages, name='receive_messages'),
    path('send_sms/', views.send_message, name='send_message'),

    path('antity/<int:board_id>', PinsView.as_view(), name='objects'),
    path('get-available-gpios/', views.get_available_gpios, name='get_available_gpios'),
    path('create/object', CreatePinView.as_view(), name='create_pin'),
    path('manage/pin/<int:pin_id>', ManagePinView.as_view(), name='manage_pin'),
    path('delete/p/<int:pin_id>', views.delete_object, name='delete_object'),

    path('my-antities/', AntitiesView.as_view(), name='my_antities'),
    path('create/antity', CreateAntityView.as_view(), name='create_antity'),
    path("manage/antity/<int:board_id>/", ManageAntityView.as_view(), name="manage_antity"),
    path('delete/a/<int:board_id>', views.delete_antity, name='delete_antity'),

    path('my-places/', PlacesView.as_view(), name='my_places'),
    path('create/place', CreatePlaceView.as_view(), name='create_place'),
    path('manage/place/<int:place_id>', ManagePlaceView.as_view(), name='manage_place'),
    path('delete/p/<int:place_id>', views.delete_place, name='delete_place'),




    path('pin/switch_on/', views.switch_on, name='switch_on'),
    path('pin/switch_off/', views.switch_off, name='switch_off'),


    path('check-pin-state', views.check_pin_state, name='check_pin_state'),
]


##