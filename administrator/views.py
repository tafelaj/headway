from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, UpdateView, CreateView, DetailView, DeleteView, ListView, FormView
from django.db import transaction

from headway.models import Program, News, Course, Exam, Lecturer, Student, ExamRegister, Institution, User, GradingList
from administrator.models import Invoice, Charges, Payments
from django.db.models import Q
from django.utils.decorators import method_decorator
from .import forms
# from headway.mixins import RequestFormKwargsMixin
from Sentinel.decorators import user_is_admin
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
import datetime


@method_decorator(user_is_admin, name='get')
class InstitutionDetail(DetailView):
    template_name = 'administrator/institute_details.html'
    model = Institution


@method_decorator(user_is_admin, name='get')
class DashBoard(TemplateView):  # add pagination
    template_name = 'administrator/dashboard.html'

    def get(self, request, *args, **kwargs):
        programs = Program.objects.filter(institution=self.request.user.institution).order_by('id')
        paginator = Paginator(programs, 10)
        page = request.GET.get('page')
        programs = paginator.get_page(page)

        context = {'programs': programs, }
        return render(request, self.template_name, context)


# #####################Lecturers#############
@method_decorator(user_is_admin, name='get')
class Lecturers(TemplateView):
        template_name = 'administrator/lecturers.html'

        def get(self, request, *args, **kwargs):
            # get a Lecturers/ access user
            lecturers = Lecturer.objects.filter(user__institution=self.request.user.institution)

            context = {
                'lecturers': lecturers,
                       }
            return render(request, self.template_name, context)


@method_decorator(user_is_admin, name='get')
@method_decorator(user_is_admin, name='post')
class LecturerUpdate(FormView):
    template_name = 'administrator/lecturer_details.html'

    def get(self, request, *args, **kwargs):
        lecturer = Lecturer.objects.get(pk=self.kwargs['pk'])
        user_form = forms.UserForm(instance=lecturer.user)
        lecturer_form = forms.LecturerForm(instance=lecturer)

        context = {'user_form': user_form,
                   'lecturer_form': lecturer_form, }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        lecturer = Lecturer.objects.get(pk=self.kwargs['pk'])
        user_form = forms.UserForm(request.POST, instance=lecturer.user)
        lecturer_form = forms.LecturerForm(request.POST, instance=lecturer)

        if user_form.is_valid() and lecturer_form.is_valid():
            user_form.save()
            lecturer_form.save()
            messages.success(request, "Lecturer Information updated")
            return redirect('administrator:lecturers')


# #####################Students#############
@method_decorator(user_is_admin, name='get')
@method_decorator(user_is_admin, name='post')
class Students(FormView):
    template_name = 'administrator/students.html'

    def get(self, request, *args, **kwargs):
        filter_form = forms.StudentFilterForm()
        program_list = Program.objects.filter(institution=self.request.user.institution)

        context = {
                'program_list': program_list,
                'filter_form': filter_form,
            }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        filter_form = forms.StudentFilterForm(request.POST)
        students = None
        program = None
        year = None
        semester = None
        if filter_form.is_valid():
            program_pk = self.request.POST.get('program_pk')
            year = filter_form.cleaned_data['year']
            semester = filter_form.cleaned_data['semester']

            program = Program.objects.get(pk=program_pk)

            students = Student.objects.filter(Q(program=program) &
                                              Q(year=year) &
                                              Q(semester=semester) &
                                              Q(is_active=True))
        context = {
            'students': students,
            'program': program,
            'first_student': students.first(),
            'year': year,
            'semester': semester,
        }
        return render(request, self.template_name, context)


@method_decorator(user_is_admin, name='get')
class StudentDetails(DetailView):
    template_name = 'administrator/student_detail.html'
    model = Student
    context_object_name = 'student'


# adding multiple students
@method_decorator(user_is_admin, name='get')
@method_decorator(user_is_admin, name='post')
class StudentsAdd(FormView):
    template_name = 'administrator/students_add.html'

    def get(self, request, *args, **kwargs):
        program_pk = self.request.GET.get('program_pk')
        year = self.request.GET.get('student_year')
        semester = self.request.GET.get('student_semester')
        # queries
        program = Program.objects.get(pk=program_pk)
        queryset = User.objects.filter(Q(institution=self.request.user.institution) &
                                       Q(student__program=program) &
                                       Q(student__year=year) &
                                       Q(student__semester=semester))
        formset = forms.StudentSignUpFormSet(queryset=queryset)
        context = {'formset': formset,
                   'program': program,
                   'year': year,
                   'semester': semester, }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        program_pk = self.request.POST.get('program_pk')
        year = self.request.POST.get('student_year')
        semester = self.request.POST.get('student_semester')
        # queries
        program = Program.objects.get(pk=program_pk)
        queryset = User.objects.filter(Q(institution=self.request.user.institution) &
                                       Q(student__program=program) &
                                       Q(student__year=year) &
                                       Q(student__semester=semester))

        formset = forms.StudentSignUpFormSet(request.POST, queryset=queryset)

        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                with transaction.atomic():
                    # get info from non-committed instance
                    print(instance.username)
                    username = instance.username
                    institution = self.request.user.institution
                    email = str(username) + '@' + str(institution.short_name) + '.com'
                    password = 'password1234'

                    # use data to create user
                    user = User.objects.create_user(username, email, password)
                    # update Extra User fields
                    user.first_name, user.middle_name, user.last_name = \
                        instance.first_name, instance.middle_name, instance.last_name
                    user.institution = institution
                    user.save()
                    Student.objects.create(user=user, year=year, semester=semester, program=program)
                    messages.success(request, 'The Students Were Added Successfully.')

            if not instances:
                messages.info(request, 'No Changes Made.')

        else:
            messages.warning(request, 'Something Went Wrong, We Could Not Validate The User Data.')
            messages.error(request, formset.errors)

        # students for display on redirect to students list.
        students = Student.objects.filter(Q(program=program) &
                                          Q(year=year) &
                                          Q(semester=semester))

        context = {
            'students': students,
            'program': program,
            'first_student': students.first(),
            'year': year,
            'semester': semester,
        }

        return render(request, 'administrator/students.html', context)


# #####################ExamsViews#############
@method_decorator(user_is_admin, name='get')
class ExamsView(ListView):
    template_name = 'administrator/exams.html'
    model = Exam
    ordering = 'start_date'
    context_object_name = 'exams'
    paginate_by = '10'


@method_decorator(user_is_admin, name='post')
@method_decorator(user_is_admin, name='get')
class ExamsAdd(SuccessMessageMixin, CreateView):
    model = Exam
    form_class = forms.ExamForm
    template_name = 'administrator/exams_form.html'
    success_message = "%(name)s Exam was Created Successfully"
    success_url = reverse_lazy('administrator:exams')

    def form_valid(self, form):
        exam = form.save(commit=False)
        exam.institution = self.request.user.institution
        exam.created_by = self.request.user
        super(ExamsAdd, self).form_valid(form)


@method_decorator(user_is_admin, name='get')
@method_decorator(user_is_admin, name='post')
class ExamsUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'administrator/exams_update_form.html'
    model = Exam
    form_class = forms.ExamForm
    success_url = reverse_lazy('administrator:exams')
    success_message = "%(name)s Was Updated Successfully"


@method_decorator(user_is_admin, name='get')
class ExamsDetail(TemplateView):
    template_name = 'administrator/exam_details.html'

    def get(self, request, *args, **kwargs):  # get number of students and number of courses
        exam = Exam.objects.get(pk=self.kwargs['pk'])
        register = ExamRegister.objects.filter(exam=exam)
        student_num = register.count()
        context = {'student_num': student_num,
                   'exam': exam, }
        return render(request, self.template_name, context)


@method_decorator(user_is_admin, name='post')
class PublishExam(FormView):
    def post(self, request, *args, **kwargs):
        exam = None
        try:
            exam = Exam.objects.get(pk=request.POST.get('exam_id'))
            exam.active = False
            exam.save()
            messages.success(request, 'The Results Were Successfully Published')
        except Exam.DoesNotExist:
            messages.error(request, 'It Seems The Exam Was Just Deleted')
        return redirect('administrator:exam_details', pk=exam.pk)


# #####################Notifications#############
class Notifications(ListView):
    # implement better filtering
    template_name = 'administrator/notifications.html'
    model = News
    context_object_name = 'news'
    paginate_by = 15

    def get_queryset(self):
        institution_id = self.request.user.institution.id
        query = News.objects.filter(institution=institution_id).order_by('-create_date')
        return query


class NotificationAdd(SuccessMessageMixin, CreateView):
    model = News
    fields = ['title', 'content', 'staff_only', ]
    template_name = 'administrator/add_notification.html'
    success_url = reverse_lazy('administrator:notifications')
    success_message = "%(title)s Was Successfully Posted"

    def form_valid(self, form):
        news = form.save(commit=False)
        news.institution = self.request.user.institution
        news.created_by = self.request.user
        if self.request.POST.get('staff_only'):
            form.instance.staff_only = True
        return super(NotificationAdd, self).form_valid(form)


class NotificationDeleteView(DeleteView):
    model = News
    success_url = reverse_lazy('administrator:notifications')
    template_name = 'administrator/news_confirm_delete.html'

    def get(self, request, *args, **kwargs):
        messages.error(request, 'Notification Deleted Successfully')
        return super(NotificationDeleteView, self).get(self, request, *args, **kwargs)


# #####################Courses#############
@method_decorator(user_is_admin, name='get')
@method_decorator(user_is_admin, name='post')
class CourseUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'administrator/update_course.html'
    model = Course
    fields = ('name', 'code', 'summary', 'credits', 'mandatory', 'semester', 'year', )
    success_url = reverse_lazy('administrator:dash')
    pk_url_kwarg = 'pk'
    success_message = "%(name)s Was Successfully Updated"


@method_decorator(user_is_admin, name='get')
@method_decorator(user_is_admin, name='post')
class CourseCreate(SuccessMessageMixin, CreateView):
    template_name = 'administrator/create_course.html'
    form_class = forms.CourseAddForm
    success_url = reverse_lazy('administrator:dash')
    success_message = "%(name)s Was Created Successfully"

    def form_valid(self, form):
        form.save(commit=False)
        form.instance.institution = self.request.user.institution
        form.instance.program = Program.objects.get(pk=self.kwargs['program_pk'])
        return super(CourseCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CourseCreate, self).get_context_data(**kwargs)
        context['program'] = Program.objects.get(pk=self.kwargs['program_pk'])
        return context


@method_decorator(user_is_admin, name='get')
@method_decorator(user_is_admin, name='post')
class CoursesCreateView(FormView):
    template_name = 'administrator/add_courses.html'

    def get(self, request, *args, **kwargs):
        program = Program.objects.get(pk=self.kwargs['program_pk'])
        formset = forms.AddCourseFormSet(queryset=Course.objects.filter(program=program))
        context = {'program': program,
                   'formset': formset, }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        program = Program.objects.get(pk=self.kwargs['program_pk'])
        formset = forms.AddCourseFormSet(request.POST, queryset=Course.objects.filter(program=program))

        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.institution = self.request.user.institution
                instance.program = Program.objects.get(pk=self.kwargs['program_pk'])
                instance.save()
                messages.success(request, "Courses Were Successfully Added/Updated")
            if not instances:
                messages.info(request, 'No Changes Made')
        else:
            messages.warning(request, "Sorry Something Went Wrong And We Could Not Add The Course")
            messages.error(request, formset.errors)
        return redirect('administrator:dash')


# #####################Programs#############
@method_decorator(user_is_admin, name='get')
@method_decorator(user_is_admin, name='post')
class AddProgram(SuccessMessageMixin, CreateView):
    template_name = 'administrator/program_add.html'
    model = Program
    fields = ('name', 'summary', 'level')
    success_message = "%(name)s Was Successfully Added"

    def form_valid(self, form):
        form.save(commit=False)
        form.instance.institution = self.request.user.institution
        return super(AddProgram, self).form_valid(form)

    def get_success_url(self):
        return reverse('administrator:add_courses', kwargs={'program_pk': self.object.pk})


@method_decorator(user_is_admin, name='get')
class DeleteProgram(DeleteView):
    template_name = 'administrator/program_confirm_delete.html'
    model = Program
    success_url = reverse_lazy('administrator:dash')

    def get(self, request, *args, **kwargs):
        messages.error(request, 'Program Deleted Successfully')
        return super(DeleteProgram, self).get(self, request, *args, **kwargs)


@method_decorator(user_is_admin, name='get')
@method_decorator(user_is_admin, name='post')
class ProgramUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'administrator/program_update.html'
    model = Program
    fields = ('name', 'summary', 'level')
    success_url = reverse_lazy('administrator:dash')
    success_message = "%(name)s Was Successfully Updated"


# ######## Accounts######
class Accounts(TemplateView):
    template_name = 'administrator/accounts.html'


@method_decorator(user_is_admin, name='get')
@method_decorator(user_is_admin, name='post')
class InvoiceStudentsFilter(FormView):
    template_name = 'administrator/invoice_student_filter.html'

    def get(self, request, *args, **kwargs):
        filter_form = forms.InvoiceStudentFilterForm()
        program_list = Program.objects.filter(institution=self.request.user.institution)

        context = {
                'program_list': program_list,
                'filter_form': filter_form,
            }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        filter_form = forms.InvoiceStudentFilterForm(request.POST)
        program_pk = None
        year = None
        semester = None
        number_of_charges = 5
        if filter_form.is_valid():
            program_pk = self.request.POST.get('program_pk')
            year = filter_form.cleaned_data['year']
            semester = filter_form.cleaned_data['semester']
            if filter_form.cleaned_data['number_of_charges']:
                number_of_charges = filter_form.cleaned_data['number_of_charges']

        return redirect('administrator:add_invoice', program_pk=program_pk, year=year, semester=semester,
                        extra=number_of_charges)


class CreateInvoices(FormView): # add a way for students who just came to get an Invoice: assign last invoice of
    template_name = 'administrator/invoice_create.html'

    def get(self, request, *args, **kwargs):
        program = Program.objects.get(pk=self.kwargs['program_pk'])
        invoice_form = forms.InvoiceForm
        extra = None
        if self.kwargs['extra']:
            extra = int(self.kwargs['extra'])
        ChargesFormset = forms.forms.modelformset_factory(Charges, form=forms.ChargesForm, extra=extra)
        charges_formset = ChargesFormset(queryset=None)

        context = {'program': program,
                   'year': self.kwargs['year'],
                   'semester': self.kwargs['semester'],
                   'invoice_form': invoice_form,
                   'charges_formset': charges_formset,
                   'extra': extra, }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        extra = self.kwargs['extra']
        ChargesFormset = forms.forms.modelformset_factory(Charges, form=forms.ChargesForm, extra=extra)
        charges_formset = ChargesFormset(request.POST)
        invoice_form = forms.InvoiceForm(request.POST)
        program = Program.objects.get(pk=self.kwargs['program_pk'])
        students = Student.objects.filter(Q(program=program) &
                                          Q(year=self.kwargs['year']) &
                                          Q(semester=self.kwargs['semester']) &
                                          Q(is_active=True))
        invoice_list = []
        if invoice_form.is_valid() and charges_formset.is_valid():
            charges = charges_formset.save(commit=False)
            # get total amount now to avoid having to save the invoices again
            total_amount = 0
            for charge in charges:
                total_amount += charge.amount

            for student in students:
                invoice_item = Invoice(institution=self.request.user.institution, prepared_by=self.request.user,
                                       student=student, total_amount=total_amount)
                invoice_list.append(invoice_item)
            # take note of time before creating in bilk
            now = datetime.datetime.now()
            # create in bulk
            Invoice.objects.bulk_create(invoice_list)
            # add charges to each invoice, really its the reverse
            invoices = Invoice.objects.filter(institution=self.request.user.institution, prepared_by=self.request.user,
                                              date__gte=now).values_list('id', flat=True)

            for invoice in invoices:
                for charge in charges:
                    charge.invoice_id = invoice
                    charge.save()
            messages.success(request, 'Invoices Were Successfully Created')
        return redirect('administrator:invoice_list')


class RecordPayments(SuccessMessageMixin, CreateView):
    template_name = 'administrator/make_payment.html'
    model = Payments
    success_message = 'Payment For %(amount)s From %(student_id)s Successfully Recorded.'
    form_class = forms.PaymentForm

    def form_valid(self, form):
        payment = form.save(commit=False)
        student = None
        try:
            student_number = form.cleaned_data['student_id']
            student = Student.objects.get(user__username=student_number)
        except Student.DoesNotExist or Student.MultipleObjectsReturned:
            messages.error(self.request, 'The Student Could Not Be Found. Check The Student ID you Entered.')
            return redirect('administrator:add_payment')
        payment.student = student
        payment.paid_to = self.request.user
        return super(RecordPayments, self).form_valid(form)


class PaymentList(ListView):
    template_name = 'administrator/payment_list.html'
    context_object_name = 'payments'
    ordering = 20

    def get_queryset(self):
        query = Payments.objects.filter(Q(paid_to__institution=self.request.user.institution)).order_by('-date')
        return query


class PaymentDetails(DetailView):
    template_name = 'administrator/payment_details.html'
    model = Payments
    context_object_name = 'payment'


class InvoiceList(ListView):
    template_name = 'administrator/invoice_list.html'
    context_object_name = 'invoices'
    ordering = 20

    def get_queryset(self):
        query = Invoice.objects.filter(Q(institution=self.request.user.institution)).order_by('-date')
        return query


class InvoiceUpdate(SuccessMessageMixin, UpdateView):
    model = Invoice
    template_name = 'administrator/invoice_update.html'
    success_url = reverse_lazy('administrator:invoice_list')
    success_message = 'Invoice Updated!'


class InvoiceDelete(DeleteView):
    model = Invoice
    template_name = 'administrator/invoice_confirm_delete.html'
    success_url = reverse_lazy('administrator:invoice_list')

    def get(self, request, *args, **kwargs):
        messages.error(request, 'Invoice Deleted Successfully')
        return super(InvoiceDelete, self).get(self, request, *args, **kwargs)


class AddGradingValues(FormView):
    model = GradingList
    template_name = 'administrator/add_gradings.html'
    success_message = 'Grading Values Have Been Updated.'

    def get(self, request, *args, **kwargs):
        queryset = GradingList.objects.filter(institution=self.request.user.institution)
        grade_list_formset = forms.GradeListFormSet(queryset=queryset)

        context = {
            'grade_list_formset': grade_list_formset,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        grade_list_formset = forms.GradeListFormSet(request.POST)
        print('pop')
        if grade_list_formset.is_valid():
            instances = grade_list_formset.save(commit=False)
            for instance in instances:
                instance.institution = self.request.user.institution
                instance.lower = instance.lower - 0.0001
                instance.upper = instance.upper + 0.0001
                instance.save()
                print('popo')
            messages.success(request, 'Grading List Updated')
        return redirect('administrator:institution_details', pk=self.request.user.institution_id)