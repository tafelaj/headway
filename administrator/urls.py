from django.urls import path
from . import views

app_name = 'administrator'

urlpatterns = [
    path('', views.DashBoard.as_view(), name='dash'),

    path('institution/<int:pk>/details/', views.InstitutionDetail.as_view(), name='institution_details'),
    path('institution/add_grading_list/', views.AddGradingValues.as_view(), name='add_grading_list'),

    path('course/<int:pk>/update/', views.CourseUpdate.as_view(), name='course_update'),
    path('course/<int:program_pk>/add/', views.CourseCreate.as_view(), name='add_course'),  # single course
    path('courses/<int:program_pk>/add/', views.CoursesCreateView.as_view(), name='add_courses'),  # Multiple courses


    path('program/add/', views.AddProgram.as_view(), name='create_program'),
    path('program/<int:pk>/delete/', views.DeleteProgram.as_view(), name='delete_program'),
    path('program/<int:pk>/update/', views.ProgramUpdate.as_view(), name='update_program'),

    path('lecturers/', views.Lecturers.as_view(), name='lecturers'),
    path('lecturers/<int:pk>/update/', views.LecturerUpdate.as_view(), name="lecturer_details"),
    path('lecturers/add/', views.Lecturers.as_view(), name='lecturers'),

    path('students/', views.Students.as_view(), name='students'),
    path('students/<int:pk>/details', views.StudentDetails.as_view(), name='student_details'),
    path('students/add/', views.StudentsAdd.as_view(), name='add_students'),

    path('exams/', views.ExamsView.as_view(), name='exams'),
    path('exams/<int:pk>/details', views.ExamsDetail.as_view(), name='exam_details'),  # filter ExamRegister
    path('exams/<int:pk>/update/', views.ExamsUpdate.as_view(), name='update_exam'),  # You Know The drill
    path('exams/add/', views.ExamsAdd.as_view(), name='add_exam'),
    path('exams/publish/', views.PublishExam.as_view(), name='publish_exam'),

    path('notifications/', views.Notifications.as_view(), name='notifications'),
    path('notifications/add/', views.NotificationAdd.as_view(), name='add_notification'),
    path('notification/<int:pk>/delete/', views.NotificationDeleteView.as_view(), name='news_delete'),

    path('accounts/', views.Accounts.as_view(), name='accounts'),
    path('accounts/invoices/', views.InvoiceList.as_view(), name='invoice_list'),
    path('accounts/invoices/<int:pk>/delete', views.InvoiceDelete.as_view(), name='invoice_delete'),
    path('accounts/invoice/<int:pk>/update', views.InvoiceUpdate.as_view(), name='invoice_update'),
    path('accounts/invoice/filter/add/', views.InvoiceStudentsFilter.as_view(), name='invoice_students_filter'),
    path('accounts/invoice/add/<int:program_pk>/<int:year>/<int:semester>/<int:extra>/',
         views.CreateInvoices.as_view(), name='add_invoice'),

    path('accounts/payments/', views.PaymentList.as_view(), name='payment_list'),
    path('accounts/payments/add/', views.RecordPayments.as_view(), name='add_payment'),
    path('accounts/payments/<int:pk>/', views.PaymentDetails.as_view(), name='payment_details'),


]
