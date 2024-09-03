from django.urls import path
from . import views
from .views import PinsView, CreatePinView, ManagePinView, AntitiesView, CreateAntityView, ManageAntityView, PlacesView, ManagePlaceView, CreatePlaceView


urlpatterns = [
    path('outputs_state/<int:board_id>/', views.etat_outputs, name='outputs_state'),
    path('output_create/', views.handle_output_create, name='output_create'),
    path('messages/', views.messages, name='messages'),
    path('update_messages/<int:message_id>/', views.update_messages, name='update_messages'),


    path('antity/<int:board_id>', PinsView.as_view(), name='objects'),
    path('create/object', CreatePinView.as_view(), name='create_pin'),
    path('manage/pin/<int:pin_id>', ManagePinView.as_view(), name='manage_pin'),

    path('my-antities/', AntitiesView.as_view(), name='my_antities'),
    path('create/antity', CreateAntityView.as_view(), name='create_antity'),
    path("manage/antity/<int:board_id>/", ManageAntityView.as_view(), name="manage_antity"),

    path('my-places/', PlacesView.as_view(), name='my_places'),
    path('create/place', CreatePlaceView.as_view(), name='create_antity'),
    path('manage/place/<int:place_id>', ManagePlaceView.as_view(), name='manage_page'),




    path('pin/switch_on/', views.switch_on, name='switch_on'),
    path('pin/switch_off/', views.switch_off, name='switch_off'),
]


##