from django.urls import path
from . import views

app_name = 'headway'

urlpatterns = [
    path('', views.Login.as_view(), name='login'),
    path('student/', views.StudentHome.as_view(), name='student_home'),
    path('lecturer/', views.LecturerHome.as_view(), name='lecturer_home'),
    path('result/list/', views.ResultList.as_view(), name='result_list'),
    path('icons/', views.Icons.as_view(), name='icons'),
    path('notifications/', views.Notifications.as_view(), name='notifications'),
    path('user/', views.UserView.as_view(), name='user'),

    path('course/register/', views.CourseRegistration.as_view(), name='course_registration'),
    path('course/register/lecturer/', views.LecturerCourseRegistration.as_view(), name='lecturer_course_registration'),

    path('courses/', views.Courses.as_view(), name='courses'),
    path('course/<int:pk>/details/', views.CourseDetails.as_view(), name='course_detail'),
    path('course/cleared/', views.CompletedCourses.as_view(), name='completed_courses'),
    path('course/<int:pk>/grade/', views.GradeCourseView.as_view(), name='grade_course'),

    path('file/upload/<int:course_id>/', views.UploadFiles.as_view(), name='upload_file'),
    path('file/<int:pk>/delete/<int:course_id>/', views.FileDeleteView.as_view(), name='delete_file'),
    path('published/papers/upload', views.PaperAdd.as_view(), name='paper_upload'),
    path('published/papers/', views.PapersView.as_view(), name='papers'),
    path('published/paper/<int:pk>/delete/', views.PaperDeleteView.as_view(), name='paper_delete'),

    path('videos/<int:playlist_pk>/playlist/', views.VideoSeriesView.as_view(), name='video_play_list'),
    path('videos/upload/<int:course_id>/', views.VideoUpload.as_view(), name='upload_video'),
    path('videos/<int:pk>/delete/<int:course_id>/', views.VideoDelete.as_view(), name='video_delete'),

    path('notifications/add/', views.NotificationAdd.as_view(), name='add_notification'),
    path('notification/<int:pk>/delete/', views.NotificationDeleteView.as_view(), name='news_delete'),
    path('notification/<int:pk>/details/', views.NotificationDetail.as_view(), name='notification_details'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('accounts/', views.Accounts.as_view(), name='student_accounts'),
]
