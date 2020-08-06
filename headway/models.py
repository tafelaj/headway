from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from datetime import timedelta
# signal imports
from django.dispatch import receiver
import os

# CONSTANTS
STATUS = (
    (0, 'In progress'),
    (1, 'Approved'),
    (2, 'Rejected'),
)

DAYS = (
    [(i, i) for i in range(1, 31)]
)

MONTHS = (
    (1, 'January'),
    (2, 'February'),
    (3, 'March'),
    (4, 'April'),
    (5, 'May'),
    (6, 'June'),
    (7, 'July'),
    (8, 'August'),
    (9, 'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December'),
)


YEARS = (
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
    )

SEMESTER = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8'),
)

LEVELS = (
    ('Certificate', 'Certificate'),
    ('Diploma', 'Diploma'),
    ('Bachelor', 'Bachelor'),
    ('Masters', 'Masters'),
)

TYPES = (
    ('M', 'Mandatory'),
    ('E', 'Elective'),
)

MARRIED = (
        ('M', 'Married'),
        ('U', 'Unmarried'),
    )

RELATION = (
    ('gma', 'Grand Mother'),
    ('gda', 'Grand Father'),
    ('dad', 'Father'),
    ('mom', 'Mother'),
    ('sis', 'Sister'),
    ('bro', 'Brother'),
    ('unc', 'Uncle'),
    ('aun', 'Auntie'),
    ('cuz', 'Cousin'),
    ('son', 'Son'),
    ('dot', 'Daughter'),)

GRADES = (
    ('A+', 'A+'),
    ('A', 'A'),
    ('B+', 'B+'),
    ('B', 'B'),
    ('C+', 'C+'),
    ('C', 'C'),
    ('D', 'D'),
    )

# THEME_COLORS = (
#    ('White', 'White'),
#    ('Blue', 'Blue'),
#    ('Green', 'Green'),
#    ('Orange', 'Orange'),
#   ('Yellow', 'Yellow'),
#    ('Red', 'Red'),
# )


# CLASSES
# ----------Institution Classes----------
class Institution(models.Model):
    name = models.CharField(max_length=100, help_text='Enter Institution Name')
    active_subscription = models.BooleanField(default=True)
    subscription_type = models.CharField(max_length=1)  # add choices
    subscription_start = models.DateField(auto_created=True, auto_now_add=True)
    subscription_end = models.DateField()
    short_name = models.CharField(max_length=10, default='INSTITUTE', help_text='Enter A Short Abbreviation Of'
                                                                                'Your Institutes Name '
                                                                                '(10 Characters Max.)')
    # theme_color = models.CharField(max_length=6, choices=THEME_COLORS, default=THEME_COLORS[0])

    def __str__(self):
        return self.name + ' ' + str(self.subscription_type)


class GradingList(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2, choices=GRADES)
    upper = models.FloatField()
    lower = models.FloatField()

    def __str__(self):
        return  str(self.grade) + ': ' +str(self.upper) + ' TO ' + str(self.lower)


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Enter a Student ID for student Accounts or Email for lecturer Accounts.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), blank=True, unique=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    is_student = models.BooleanField(default=True)
    is_lecturer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        if self.middle_name:
            full_name = '%s %s %s' % (self.first_name, self.middle_name, self.last_name)
        else:
            full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name

    def __str__(self):
        return self.get_full_name()


class PersonalDetails(models.Model):
    province = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    home_address = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    birthday = models.DateField(verbose_name='Date of Birth', blank=True, null=True)
    marital_status = models.CharField(max_length=1, choices=MARRIED, blank=True, null=True)
    nrc_number = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        abstract = True


class Guardian(PersonalDetails):
    relation = models.CharField(max_length=3, choices=RELATION)


class Program(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=150)
    summary = models.TextField(null=True, blank=True)
    level = models.CharField(max_length=11, choices=LEVELS, help_text='Qualification Level For The Program.')

    def __str__(self):
        return str(self.name) + ' (' + str(self.level) + ')'

    def get_absolute_url(self):
        return reverse('headway:program_details', kwargs={'pk': self.pk})


class Course(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, default='CODE_default', help_text='Enter Course Code')
    summary = models.TextField(max_length=600, null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    credits = models.IntegerField(null=True, default=0)
    mandatory = models.BooleanField(default=True)
    year = models.IntegerField(choices=YEARS, default=1)
    semester = models.IntegerField(choices=SEMESTER, default=1)
    course_lecturer = models.ManyToManyField('Lecturer', related_name='course_teacher', blank=True)

    def __str__(self):
        return self.name

    def get_type(self):
        if self.mandatory:
            return "Mandatory"
        else:
            return "Elective"

    def get_absolute_url(self):
        return reverse('headway:course_detail', kwargs={'pk': self.pk})


class CourseRegister(models.Model):
    student = models.ForeignKey('Student', related_name='register', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='registered_course', on_delete=models.CASCADE)
    date_registered = models.DateTimeField(auto_now_add=True, auto_created=True)
    cleared = models.BooleanField(default=False)


class Student(PersonalDetails):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(null=True, blank=True, default='no-img.png')
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    guardian = models.OneToOneField(Guardian, on_delete=models.SET_NULL, null=True, blank=True)
    courses = models.ManyToManyField(Course, related_name='courses', blank=True, through=CourseRegister)
    year = models.IntegerField(choices=YEARS, default=1)
    semester = models.IntegerField(choices=SEMESTER, default=1)
    exams = models.ManyToManyField('Exam', related_name='students', through='ExamRegister')
    is_active = models.BooleanField(default=True) # for pursose of students that left the school but can still login

    def get_contact(self):
        if self.phone:
            return self.phone
        else:
            return self.user.email  # return email if no number.

    def __str__(self):
        return str(self.user) + '  (' + str(self.user.username) + ')'

    def get_absolute_url(self):
        return reverse('headway:student_profile', kwargs={'pk': self.pk})


class Lecturer(PersonalDetails):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    qualification = models.CharField(max_length=200, help_text='Enter Highest Qualification Attained.')
    date_of_join = models.DateTimeField(auto_created=True)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse('headway:lecturer_profile', kwargs={'pk': self.pk})


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    graded_by = models.ForeignKey(Lecturer, on_delete=models.DO_NOTHING, null=True, blank=True)
    ca_grade = models.ForeignKey('TestGrade', blank=True, null=True, on_delete=models.SET_NULL)
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE)
    marks = models.FloatField(default=0, null=True)
    grade = models.CharField(max_length=2, choices=GRADES, null=True, blank=True)  # add field to show ma A+
    date_graded = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return self.student.user.get_full_name() + ' ' + str(self.grade)

    def get_absolute_url(self):
        return reverse('headway:grade_details', kwargs={'pk': self.pk})


class Exam(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)
    courses = models.ManyToManyField(Course)
    # students = models.ManyToManyField(Student)

    def get_absolute_url(self):
        return reverse('administrator:exam_details', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name + ' ' + str(self.start_date) + ' | ' + str(self.end_date)


class ExamRegister(models.Model):
    student = models.ForeignKey(Student, related_name='subscriptions', on_delete=models.SET_NULL, null=True)
    exam = models.ForeignKey(Exam, related_name='exams', on_delete=models.SET_NULL, null=True)
    courses = models.ManyToManyField(Course, related_name='examRegisterCourses')
    date_registered = models.DateTimeField(auto_created=True)

    def __str__(self):
        return str(self.student) + ' ' + str(self.exam)


# ##############TEST BUSINESS########
class TestGrade(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Continuous Assessment')
    ca_total = models.FloatField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.FloatField()
    ca_value = models.FloatField()

    def set_ca_value(self):
        ca_value = (self.marks/100) * self.ca_total
        self.ca_value = ca_value
        return self.ca_value

    def __str__(self):
        return self.ca_value


# ########### NOTIFICATION THINGS ###########
class News(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(help_text='Enter Message Content here.')
    picture = models.ImageField(null=True, blank=True)
    create_date = models.DateTimeField(auto_created=True, auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    staff_only = models.BooleanField(default=True, help_text='Who should See This Message.')

    def get_content(self):
        return self.content[:150] + '...'

    def __str__(self):
        return self.title

    def is_recent(self):
        recent = False
        now = timezone.now()
        two_days = timedelta(days=2)
        difference = now - self.create_date
        if difference < two_days:
            recent = True
        return recent

    def get_absolute_url(self):
        return reverse('headway:notification_details', kwargs={'pk': self.pk})

    class Meta:
        verbose_name_plural = 'News'


class RecentNews(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Recent News'

    def __str__(self):
        return self.news.title


def upload_dir_papers(instance, filename):
    name = str(instance.user.institution.id) + str(instance.user.institution.short_name) + '/papers/' + filename
    return name


class Papers(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_dir_papers, max_length=150)
    date = models.DateTimeField(auto_created=True, auto_now_add=True)

    def get_absolute_url(self):
        return reverse('headway:papers')


def upload_dir_files(instance, filename):
    name = str(instance.user.institution.id) + str(instance.user.institution.short_name) + '/uploads/' + filename
    return name


class Uploads(models.Model):
    name = models.CharField(max_length=100, help_text='Enter A Name For The File')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_dir_files, max_length=150, help_text='Choose File To Be Uploaded')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    upload_time = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Uploads'


class VideoSeries(models.Model):
    name = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    link = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True, auto_created=True)

    class Meta:
        verbose_name_plural = 'Video Series'

    def __str__(self):
        return self.name +' '+ str(self.course)


# delete files after corresponding Uploads Model has been deleted
@receiver(models.signals.post_delete, sender=Uploads)
def auto_delete_file_on_model_delete(sender, instance, **kwargs):
    """Deletes the file from file field of deleted Uploads model"""
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


# delete Papers after corresponding Paper Model has been deleted
@receiver(models.signals.post_delete, sender=Papers)
def auto_delete_paper_on_model_delete(sender, instance, **kwargs):
    """Deletes the file from file field of deleted Uploads model"""
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
