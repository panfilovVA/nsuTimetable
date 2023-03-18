from django.urls import path

from .views import *

urlpatterns = [
    path('', index),
    path('read_json/', load_from_json),
    path('create_shedule/', create_sched),

    path('schedule/', schedule, name='schedule'),
    path('schedule/<int:group_number>/<int:identif>/', show_schedule),

    path("subjects/", SubjectList.as_view(), name='subjects'),
    path('subject/create/', SubjectCreate.as_view(), name='create_subject'),
    path("subject/<int:pk>/", SubjectDetail.as_view(), name='subject'),
    path("subject/edit/<int:pk>/", SubjectEdit.as_view(), name='edit_subject'),

    path('teacher/create/', TeacherCreate.as_view(), name='create_teacher'),
    path('teachers/', TeacherList.as_view(), name='teachers'),
    path('teacher/<int:pk>/', TeacherDetail.as_view(), name='teacher'),
    path('teacher/edit/<int:pk>/', TeacherEdit.as_view(), name='edit_teacher'),

    path('rooms/', RoomList.as_view(), name='rooms'),
    path('room/create/', RoomCreate.as_view(), name='create_room'),
    path('room/<int:pk>/', RoomDetail.as_view(), name='room'),
    path('room/edit/<int:pk>/', RoomEdit.as_view(), name='edit_room'),

    path('subjappgroups/', SubjAppGroupList.as_view(), name='subjappgroups'),
    path('subjappgroup/<int:pk>/', SubjAppGroupEdit.as_view(), name='subjappgroup'),
    path('subjappgroup/create/', SubjAppGroupCreate.as_view(), name='create_subjappgroup'),

    path('groups/', GroupList.as_view(), name='groups'),
    path('group/create/', GroupCreate.as_view(), name='create_group'),
    path('group/<int:pk>/', GroupDetail.as_view(), name='group'),
    path('group/edit/<int:pk>/', GroupEdit.as_view(), name='edit_group')

]
