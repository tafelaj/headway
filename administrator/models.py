from django.db import models
from headway.models import Student, Institution, User
from django.urls import reverse


# ----------------- Accounts Models ---------
class Charges(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
    description = models.CharField(max_length=250)
    amount = models.FloatField()


class Invoice(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    description = models.CharField(max_length=250, null=True)
    total_amount = models.FloatField(null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    prepared_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return str(self.student.program) + 'Year: ' + str(self.student.year)\
               + ' Semester: ' + str(self.student.semester) + ' : ' + str(self.date.date())


class Payments(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    paid_to = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    description = models.CharField(max_length=200)
    receipt_no = models.CharField(max_length=120)
    date = models.DateTimeField(auto_created=True, auto_now=True)

    def get_absolute_url(self):
        return reverse('administrator:payment_details', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.student) + ' ' + str(self.description)
