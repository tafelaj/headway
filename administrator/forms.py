from django import forms
from headway.models import Course, Lecturer, User, Exam, GradingList
from headway.mixins import RequestKwargModelFormMixin
from administrator.models import Payments, Invoice, Charges

YEAR = (
    ('1', 'First Year'),
    ('2', 'Second Year'),
    ('3', 'Third Year'),
    ('4', 'Fourth Year'),
    ('5', 'Firth Year'),
    ('6', 'Sixth Year'),
    ('7', 'Seventh Year'),
)
SEMESTER = (
    ('1', 'Semester 1'),
    ('2', 'Semester 2'),
)

class CourseAddForm(forms.ModelForm):

    class Meta:
        model = Course
        exclude = ('institution', 'program',)


class CourseForm(RequestKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = Course
        exclude = ('institution', 'program', 'course_lecturer')

AddCourseFormSet = forms.modelformset_factory(Course, form=CourseForm, extra=6)
GradeStudentsFormset = forms.modelformset_factory(Course, form=CourseForm, extra=0)


class LecturerForm(RequestKwargModelFormMixin, forms.ModelForm):

    class Meta:
        model = Lecturer
        exclude = ('user', 'date_of_join')


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'middle_name', 'last_name', 'email',)


LecturerFormSet = forms.modelformset_factory(Lecturer, form=LecturerForm, extra=0)
UserFormSet = forms.modelformset_factory(User, form=UserForm, extra=0)


class StudentFilterForm(forms.Form):
    year = forms.ChoiceField(choices=YEAR)
    semester = forms.ChoiceField(choices=SEMESTER)


class InvoiceStudentFilterForm(forms.Form):
    year = forms.ChoiceField(choices=YEAR)
    semester = forms.ChoiceField(choices=SEMESTER)
    number_of_charges = forms.IntegerField(help_text='Number Of Charges The Invoice Will Have. '
                                                     'If Left Blank It Defaults To 5.', required=False)


class ExamForm(forms.ModelForm):

    class Meta:
        model = Exam
        fields = ('name', 'start_date', 'end_date')


class StudentCreateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'middle_name', 'last_name', 'username',)

    def __init__(self, *args, **kwargs):
        super(StudentCreateForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Computer Number'
        self.fields['username'].help_text = 'Enter a Student ID(Computer Number)'


StudentSignUpFormSet = forms.modelformset_factory(User, form=StudentCreateForm, extra=5)


class PaymentForm(forms.ModelForm):
    student_id = forms.CharField(max_length=50, help_text='Enter Student Computer Number')

    class Meta:
        model = Payments
        fields = ('amount', 'description', 'receipt_no',)


class InvoiceForm(forms.ModelForm):

    class Meta:
        model = Invoice
        fields = ()


class ChargesForm(forms.ModelForm):

    class Meta:
        model = Charges
        fields = ('description', 'amount')


class GradeListForm(forms.ModelForm):

    class Meta:
        model = GradingList
        fields = ('grade', 'lower', 'upper')

GradeListFormSet = forms.modelformset_factory(GradingList, form=GradeListForm, extra=5)