from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.conf import settings
from .mixins import RequestKwargModelFormMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from headway.models import Student, Grade,Lecturer, Course, User, Uploads


# class RequestKwargModelFormMix(object):
#    """
#    Generic model form mixin for popping request out of the Kwargs and attaching it to the instance
#    """
#    def __init__(self, *args, **kwargs):
#        self.request = kwargs.pop("request", None)  # pop the request to be passed in kwargs
#        super(RequestKwargModelFormMix, self).__init__()


class StudentSignUpForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'middle_name', 'last_name', 'username',)

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.save()
        return user


class LecturerSignUpForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        if commit:
            user.save()
        Lecturer.objects.create(user=user)
        return user


class CourseRegistrationForm(RequestKwargModelFormMixin, forms.ModelForm):

    class Meta:
        model = Student
        fields = ('courses',)

    def __init__(self, *args, **kwargs):
        super(CourseRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['courses'].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields['courses'].help_text = "Mark All The Courses You Will Be Taking"
        self.fields['courses'].queryset = Course.objects.filter(institution=self.request.user.institution,
                                                                program=self.request.user.student.program,
                                                                year=self.request.user.student.year,
                                                                semester=self.request.user.student.semester,)
        self.helper = FormHelper()
        self.helper.form_id = 'id_course_form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = '#'

        self.helper.add_input(Submit('submit', 'Register'))


class LecturerCourseRegistrationForm(RequestKwargModelFormMixin, forms.ModelForm):

    class Meta:
        model = Student
        fields = ('courses',)

    def __init__(self, *args, **kwargs):
        super(LecturerCourseRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['courses'].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields['courses'].help_text = "Mark All The Courses You Will Be Teaching"
        self.fields['courses'].queryset = Course.objects.filter(institution=self.request.user.institution)
        self.helper = FormHelper()
        self.helper.form_id = 'id_course_form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = '#'

        self.helper.add_input(Submit('submit', 'Register'))


class FileUploadForm(forms.ModelForm):

    class Meta:
        model = Uploads
        fields = ('name', 'file',)

    def __init__(self, *args, **kwargs):
        super(FileUploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id_file_upload'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = '#'

        self.helper.add_input(Submit('submit', 'Upload'))


class StudentGradeForm(forms.ModelForm):

    class Meta:
        model = Grade
        fields = ('student', 'marks',)

    def __init__(self, *args, **kwargs):
        super(StudentGradeForm, self).__init__(*args, **kwargs)

GradeStudentsFormset = forms.modelformset_factory(Grade, form=StudentGradeForm, extra=0)


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ('nrc_number','province', 'district', 'town', 'home_address', 'phone', 'birthday', 'marital_status',)


