from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.conf import settings
from . import forms
from administrator.forms import UserForm, LecturerForm
from .models import Lecturer, Student, Course, Grade, Exam, News, RecentNews, User, CourseRegister, Uploads, \
    TestGrade, Papers, VideoSeries, GradingList
from django.views.generic import TemplateView, CreateView, FormView, ListView, DetailView, DeleteView
from django.db.models import Q
from django.db import transaction
from .mixins import RequestFormKwargsMixin
from django.utils.decorators import method_decorator
import datetime
from Sentinel.decorators import user_is_lecturer
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from administrator.models import Invoice, Payments


class Landing(TemplateView):
    template_name = 'headway/landing.html'


class StudentHome(TemplateView):
    template_name = 'headway/student_home.html'

    def get(self, request, *args, **kwargs):
        student = Student.objects.get(id=self.request.user.student.id)
        courses = student.courses.all()
        recent_news = []

        # GETTING THE LATEST NEWS TO SHOW ON DASHBOARD
        # recent notifications popup
        institution_id = self.request.user.institution.id
        # get last 5 updates from institution
        news = RecentNews.objects.filter(Q(news__institution=institution_id) & Q(news__staff_only=False))[:5]
        for notification in news:
            if notification.news.is_recent():
                recent_news.append(notification)

        context = {
            'courses': courses,
            'recent_news': recent_news,
        }
        return render(request, self.template_name, context)


@method_decorator(user_is_lecturer, name='get')
class LecturerHome(TemplateView):
    template_name = 'headway/lecturer_home.html'

    def get(self, request, *args, **kwargs):
        recent_news = []
        courses = Course.objects.filter(Q(institution=request.user.institution) &
                                        Q(course_lecturer=request.user.lecturer))

        # GETTING THE LATEST NEWS TO SHOW ON DASHBOARD
        # recent notifications popup
        institution_id = self.request.user.institution.id
        # get last 5 updates from institution
        news = RecentNews.objects.filter(Q(news__institution=institution_id) &
                                         Q(news__staff_only=False))[:5]
        for notification in news:
            if notification.news.is_recent():
                recent_news.append(notification)

        context = {
            'courses': courses,
            'recent_news': recent_news,
        }
        return render(request, self.template_name, context)


class ResultList(TemplateView):
    """This class contains tons of misleading variable names"""
    template_name = 'headway/result_list.html'

    def get(self, request, *args, **kwargs):
        context = {}
        if request.user.is_student:
            exams = Exam.objects.filter(Q(institution=request.user.institution) &
                                        Q(students=request.user.student) &
                                        Q(active=False)).order_by('-end_date')

            context = {
                'exams': exams,
            }

        else:
            if request.user.is_lecturer:
                exams = Exam.objects.filter(Q(institution=request.user.institution) & Q(
                    grade__graded_by=request.user.lecturer))

                context = {
                    'exams': exams,
                }
        return render(request, self.template_name, context)


class Icons(TemplateView):
    pass


class Notifications(ListView):
    # implement better filtering
    template_name = 'headway/notifications.html'
    model = News
    context_object_name = 'news'
    paginate_by = 15
    ordering = ['-create_date']

    def get_queryset(self):
        institution_id = self.request.user.institution.id
        if self.request.user.is_lecturer:
            query = News.objects.filter(institution=institution_id)

        else:
            query = News.objects.filter(Q(institution=institution_id) &
                                        Q(staff_only=False))
        return query


class NotificationAdd(SuccessMessageMixin, CreateView):
    model = News
    fields = ['title', 'content', 'staff_only', ]
    template_name = 'headway/add_notification.html'
    success_url = reverse_lazy('headway:notifications')
    success_message = '%(title)s Was Added Successfully'

    def form_valid(self, form):
        form.instance.institution = self.request.user.institution
        form.instance.title = self.request.POST.get('title')
        form.instance.content = self.request.POST.get('content')
        form.instance.created_by = self.request.user
        if self.request.POST.get('staff_only'):
            form.instance.staff_only = True
        return super(NotificationAdd, self).form_valid(form)


class NotificationDeleteView(DeleteView):
    model = News
    success_url = reverse_lazy('headway:notifications')


class NotificationDetail(DetailView):
    model = News
    template_name = 'headway/notification_detail.html'
    context_object_name = 'notification'


# this view is ridiculous (it used to be)
class UserView(FormView):
    template_name = 'headway/user.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        profile_form = None
        user_form = UserForm(instance=user)
        if request.user.is_student:
            student = request.user.student
            profile_form = forms.StudentForm(instance=student)

        if request.user.is_lecturer:
            lecturer = request.user.lecturer
            profile_form = LecturerForm(instance=lecturer)
        context = {'user_form': user_form,
                   'profile_form': profile_form, }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = request.user
        user_form = UserForm(request.POST, instance=user)
        user_form.save()
        if request.user.is_student:
            student = request.user.student
            profile_form = forms.StudentForm(request.POST, instance=student)
            profile_form.save()
            messages.success(request, 'User Profile Updated')

        if request.user.is_lecturer:
            lecturer = request.user.lecturer
            profile_form = LecturerForm(request.POST, instance=lecturer)
            profile_form.save()

            messages.success(request, 'User Profile Updated')

        return redirect('headway:user')


class PapersView(ListView):
    template_name = 'headway/papers.html'
    model = Papers
    paginate_by = 10
    ordering = ['-date']


class PaperAdd(SuccessMessageMixin, CreateView):
    template_name = 'headway/paper_add.html'
    model = Papers
    fields = ('name', 'file')
    success_message = '%(name)s Was Successfully Added.'

    def form_valid(self, form):
        form.save(commit=False)
        form.instance.user = self.request.user
        return super(PaperAdd, self).form_valid(form)


class CourseRegistration(RequestFormKwargsMixin, FormView):
    template_name = 'headway/course_reg.html'
    form_class = forms.CourseRegistrationForm

    def post(self, request, *args, **kwargs):
        already_registered = []
        student = self.request.user.student
        for course_pk in request.POST.getlist('courses'):
            course = Course.objects.get(pk=course_pk)
            if request.user.is_student:
                try:
                    if CourseRegister.objects.get(student=student, course=course):
                        already_registered.append(course)
                except CourseRegister.DoesNotExist:
                    CourseRegister.objects.create(student=student, course=course)
        messages.success(request, 'Course Registration Successful.')

        if already_registered:
            context = {
                'already_registered': already_registered,
            }
            return render(request, self.template_name, context)
        return redirect('headway:courses')


class LecturerCourseRegistration(RequestFormKwargsMixin, FormView):
    template_name = 'headway/course_reg.html'
    form_class = forms.LecturerCourseRegistrationForm

    def post(self, request, *args, **kwargs):
        lecturer = self.request.user.lecturer
        for course_pk in request.POST.getlist('courses'):
            course = Course.objects.get(pk=course_pk)

            if request.user.is_lecturer:
                if lecturer not in course.course_lecturer.all():
                    course.course_lecturer.add(request.user.lecturer)
        messages.success(request, 'Course Registration Successful.')
        return redirect('headway:courses')


class Courses(TemplateView):
    template_name = 'headway/courses.html'

    def get(self, request, *args, **kwargs):
        courses = []
        if request.user.is_student:
            student = request.user.student
            register = CourseRegister.objects.filter(student=student, cleared=False)
            for entry in register:
                course = Course.objects.get(pk=entry.course.id)
                courses.append(course)

        if request.user.is_lecturer:
            lecturer = request.user.lecturer
            courses = Course.objects.filter(Q(institution=self.request.user.institution) &
                                            Q(course_lecturer=lecturer))

        context = {'courses': courses, }

        return render(request, self.template_name, context)


class CourseDetails(TemplateView):
    model = Course
    template_name = 'headway/course_details.html'
    context_object_name = 'course'

    def get(self, request, *args, **kwargs):
        course = Course.objects.get(pk=kwargs['pk'])
        files = Uploads.objects.filter(course=course)
        tests = None
        videos = VideoSeries.objects.filter(course=course)
        test_grades = None
        if request.user.is_lecturer:
            tests = TestGrade.objects.filter(course=course, lecturer=request.user.lecturer)
        else:
            test_grades = TestGrade.objects.filter(course=course, student=request.user.student)

        context = {'course': course,
                   'files': files,
                   'tests': tests,
                   'test_grades': test_grades,
                   'videos': videos, }

        return render(request, self.template_name, context)


class CompletedCourses(TemplateView):
    template_name = 'headway/completed_courses.html'

    def get(self, request, *args, **kwargs):
        grades = []
        student = request.user.student
        register = CourseRegister.objects.filter(student=student, cleared=True)

        for entry in register:
            course = Course.objects.get(pk=entry.course.id)
            grade = Grade.objects.get(student=student, course=course)
            grades.append(grade)

        context = {'courses': grades}

        return render(request, self.template_name, context)


class GradeCourseView(FormView):
    template_name = 'headway/grade_course.html'

    def get(self, request, *args, **kwargs):
        course = Course.objects.get(pk=self.kwargs['pk'])
        queryset = Grade.objects.filter(course=course)
        formset = forms.GradeStudentsFormset(queryset=queryset)

        context = {'course': course,
                   'formset': formset}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        course = Course.objects.get(pk=self.kwargs['pk'])
        queryset = Grade.objects.filter(course=course)
        formset = forms.GradeStudentsFormset(request.POST, queryset=queryset)
        grade_lists = GradingList.objects.filter(institution=self.request.user.institution)

        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                with transaction.atomic():
                    instance.graded_by = self.request.user.lecturer
                    # figure out grades
                    for grade in grade_lists:
                        if grade.lower < instance.marks < grade.upper:
                            instance.grade = grade.grade
                            print('i set it')
                    instance.save()
                    messages.success(request, 'Students Graded Successfully')
            return redirect('headway:result_list')


class UploadFiles(FormView):
    template_name = 'headway/file_upload.html'

    def get(self, request, *args, **kwargs):
        form = forms.FileUploadForm()

        context = {
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = forms.FileUploadForm(request.POST, request.FILES)

        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = self.request.user
            print(kwargs['course_id'])
            upload.course = Course.objects.get(id=kwargs['course_id'])
            upload.save()
            messages.success(request, 'File Uploaded Successfully.')

        return redirect('headway:course_detail', pk=kwargs['course_id'])


class FileDeleteView(DeleteView):
    model = Uploads

    def get_success_url(self):
        pk = self.kwargs['course_id']
        return reverse_lazy('headway:course_detail', kwargs={'pk': pk})

    def get(self, request, *args, **kwargs):
        messages.error(request, 'The File Was Deleted.')
        return super(FileDeleteView, self).get(self, request, *args, **kwargs)


class PaperDeleteView(DeleteView):
    model = Papers
    success_url = reverse_lazy('headway:papers')


class SearchView(TemplateView):
    template_name = 'headway/search.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')

        # course Query List
        course_query_list = Course.objects.filter(Q(institution=request.user.institution) &
                                                  Q(name__icontains=query))

        # News Query List
        news_query_list = News.objects.filter(Q(institution=request.user.institution) &
                                              Q(title__icontains=query) |
                                              Q(content__icontains=query))

        #  Papers Query List
        papers_query_list = Papers.objects.filter(name__icontains=query)

        # Upload Query List
        upload_query_list = Uploads.objects.filter(Q(name__icontains=query) &
                                                   Q(user__institution=request.user.institution))

        context = {
            'course_query_list': course_query_list,
            'news_query_list': news_query_list,
            'papers_query_list': papers_query_list,
            'upload_query_list': upload_query_list,
        }

        return render(request, self.template_name, context)


# ################################# SignUP and LogIN Views ############################################
class StudentSignUpView(CreateView):
    model = settings.AUTH_USER_MODEL
    form_class = forms.StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('headway:student_home')


class LecturerSignUpView(CreateView):
    model = settings.AUTH_USER_MODEL
    form_class = forms.LecturerSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Lecturer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        print(Lecturer.objects.get(user=user))  # test purpose
        login(self.request, user)
        return redirect('headway:lecturer_home')


# logIN
class Login(FormView):
    template_name = 'registration/login.html'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_active:
                if user.institution.active_subscription:
                    login(request, user)
                    if user.is_student:
                        return HttpResponseRedirect(reverse_lazy('headway:student_home'))
                    if user.is_lecturer:
                        return HttpResponseRedirect(reverse_lazy('headway:lecturer_home'))
                    if user.is_admin:
                        return HttpResponseRedirect(reverse_lazy('administrator:dash'))

                else:
                    return render(request, self.template_name, {'error': 'Your Institution Has Been Deactivated. '
                                                                         'Go To The Support Page For Assistance.'})
            else:
                return render(request, self.template_name, {'error': 'Your Account Has Been Deactivated. '
                                                                     'Go To The Support Page For Assistance.'})
        else:
            error = 'Your Account Was Not Found. Check Your Student ID or Email and Password. ' \
                    'Contact Your Admin If The Problem Persists.'
            context = {
                'error': error
            }
            return render(request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return render(request, self.template_name)
        if request.user.is_authenticated:
            if request.user.is_lecturer:
                return HttpResponseRedirect(reverse_lazy('headway:lecturer_home'))
            if request.user.is_student:
                return HttpResponseRedirect(reverse_lazy('headway:student_home'))
            if request.user.is_admin:
                return HttpResponseRedirect(reverse_lazy('administrator:dash'))


# ################################# Video Views ############################################
class VideoSeriesView(TemplateView):
    template_name = 'headway/video_playlist.html'

    def get(self, request, *args, **kwargs):
        video = VideoSeries.objects.get(pk=self.kwargs['playlist_pk'])
        context = {'video': video, }
        return render(request, self.template_name, context)


class VideoUpload(SuccessMessageMixin, CreateView):
    template_name = 'headway/video_form.html'
    model = VideoSeries
    fields = ('name', 'link',)
    success_message = '%(name)s Was Successfully Added.'

    def form_valid(self, form):
        video = form.save(commit=False)
        video.course = Course.objects.get(pk=self.kwargs['course_id'])
        return super(VideoUpload, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('headway:course_detail', kwargs= {'pk': self.kwargs['course_id'], })


class VideoDelete(DeleteView):
    model = VideoSeries
    template_name = 'headway/video_series_confirm_delete.html'

    def get_success_url(self):
        pk = self.kwargs['course_id']
        return reverse_lazy('headway:course_detail', kwargs={'pk': pk, })

    def get(self, request, *args, **kwargs):
        messages.error(request, 'The Video Series Was Deleted.')
        return super(VideoDelete, self).get(self, request, *args, **kwargs)


class Accounts(TemplateView):
    template_name = 'headway/accounting.html'

    def get(self, request, *args, **kwargs):
        invoices = Invoice.objects.filter(Q(institution=self.request.user.institution) &
                                          Q(student=self.request.user.student)).order_by('-date')
        payments = Payments.objects.filter(Q(institution=self.request.user.institution) &
                                           Q(student=self.request.user.student)).order_by('-date')
        invoices_total = 0
        payments_total = 0

        for invoice in invoices:
            invoices_total += invoice.total_amount
            print(invoices_total)

        for payment in payments:
            payments_total +=payment.amount
            print(payments_total)

        outstanding = invoices_total - payments_total

        context = {
            'invoices': invoices,
            'outstanding': outstanding,
            'payments': payments,}
        return render(request, self.template_name, context)