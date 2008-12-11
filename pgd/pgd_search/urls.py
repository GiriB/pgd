from django.conf.urls.defaults import *

urlpatterns = patterns('pgd_search.views',
    (r'^$', 'search'),
    (r'^results/$', 'renderToSVG'),
    (r'^plot/svg/$', 'renderToSVG'),
    (r'^plot/png/$', 'renderToPNG'),
    (r'^statistics/$', 'searchStatistics'),
    (r'^dump/$', 'dataDump'),
)
