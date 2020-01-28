from django.conf.urls import url
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = "bodymap"

urlpatterns = [
    url(
        r'^$',
        views.index,
        name='home'
    ),
    url(
        r'^help$',
        views.help,
        name='help'
    ),
    url(
        r'^chemMapping/$',
        views.mappingChemicalToBody,
        name='chemMapping'
    ),
    url(
        r'^chemMappingCASNResult/$',
        views.mappingChemicalToBody,
        {"typeChem":"CASN"},
        name='chemMappingCAS'
    ),
    url(
        r'^chemMappingNameResult/$',
        views.mappingChemicalToBody,
        {"typeChem":"name"},
        name='chemMappingTable'

    ),
    ]+ static(settings.STATIC_URL, document_root="{}/bodymap/".format(settings.STATIC_ROOT))
