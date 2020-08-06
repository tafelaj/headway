from django.contrib import admin
from .models import User, Institution, Student, Lecturer, Program, Course, News, RecentNews, CourseRegister, \
    Uploads, Grade, Exam, VideoSeries, ExamRegister, GradingList

# Register your models here.
admin.site.register(User)
admin.site.register(Institution)
admin.site.register(Student)
admin.site.register(Lecturer)
admin.site.register(Program)
admin.site.register(Course)
admin.site.register(News)
admin.site.register(RecentNews)
admin.site.register(CourseRegister)
admin.site.register(Uploads)
admin.site.register(Grade)
admin.site.register(Exam)
admin.site.register(VideoSeries)
admin.site.register(ExamRegister)
admin.site.register(GradingList)
