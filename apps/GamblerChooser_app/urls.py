from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^add_players$', views.add_players),
    url(r'^remove_player/(?P<player_id>\d+)$', views.remove_player),
    url(r'^play_game$', views.play_game),
    url(r'^new_game$', views.new_game)
]