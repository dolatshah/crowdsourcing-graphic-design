from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout 
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


freeDesignerPatterns = patterns('freeDesigner.views',
    # Examples:
    # url(r'^$', 'projefa.views.home', name='home'),
    # url(r'^projefa/', include('projefa.foo.urls')),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    ('^$', 'main'),
    (r'^signup/(.*)$', 'signup'),
    (r'^login/$', 'login_view'),
    (r'^loginAjax/$', 'loginAjax'),
    (r'^login/(.*)/$', 'login_view'),
    (r'^logout/$', 'logout_view'), 
    (r'^profile/$', 'profile'),
    (r'^profile/(.*)/$', 'profile'),
    (r'^editProfile/$', 'editProfile'),
    (r'^message/(\d+)/$','message'),
    (r'^setting/$', 'setting'),
    (r'^account/$','account'),
    (r'^account/(.*)/$','account'),
    (r'^deposit/$','deposit'),
    (r'^deposit/(.*)/$','deposit'),
    (r'^withdraw/$','withdraw'),
    (r'^messagesList/$','messagesList'),
    (r'^notifications/$','notifications'),
    (r'^conversation/(\d+)/$','conversation'),
    (r'^controlPanel/$','controlPanel'),
    (r'^controlPanel/(.*)/$','controlPanel'),
    (r'^myProjects/$','myProjects'),
    (r'^chat/(\d+)/(\d+)/$', 'chat'),
    (r'^chats/(\d+)/(\d+)/(.*)/$', 'chats'),
    (r'^resume/$', 'resume'),
    (r'^resume/(.*)/$', 'resume2'),
    (r'^uploadResume/$', 'uploadResume'),
    (r'^deleteResume/$', 'deleteResume'),
    (r'^edit-description/$', 'editDescription'),
    (r'^edit-picture/$', 'editPicture'),
    (r'^remove-resume/(\d+)/$','removeResume'),
    (r'^file/$', 'file'),
    	

    
    

    
    

    

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

projectpatterns = patterns('project.views',
                        
    (r'^new-project/$', 'newProject'),
    (r'^project/(\d+)/$','project'),
    (r'^project/(\d+)/(.*)/$','project'),
    (r'^upload/(\d+)/$','upload'),
    (r'^remove-upload/(\d+)/$','removeUpload'),
    (r'^done/(\d+)/$','done'),
    (r'^cancel/(\d+)/$','cancel'),
    (r'^timeincrease/(\d+)/(\d+)/$','timeincrease'),
    (r'^mortgageincrease/(\d+)/(\d+)/$','mortgageincrease'),
    (r'^changeOffer/(\d+)/(\d+)/$','changeOffer'),
    (r'^deleteOffer/(\d+)/$','deleteOffer'),
    (r'^acceptOffer/(\d+)/$','acceptOffer'),
    (r'^cancelOffer/(\d+)/$','cancelOffer'),
    (r'^editProject/(\d+)/$','editProject'),
    (r'^advanced-search/$', 'advancedSearch'),
    (r'^completeByEmployee/(\d+)/$','completeByEmployee'),
    (r'^sue/(\d+)/$','sue'),
     (r'^addfile/(\d+)/(.*)/$','addfile')
     

)



chatpatterns = patterns('freeDesigner.views',

    (r'^chat/(\d+)/$', 'chat'),
    (r'^chats/(\d+)/(\d+)/(\d+)/$', 'chats'),
                   
    
     
)

urlpatterns =freeDesignerPatterns
urlpatterns +=projectpatterns
urlpatterns += chatpatterns
handler500 = 'freeDesigner.views.handler500'
