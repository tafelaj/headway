def __init__(self, *args, **kwargs):
    super(LecturerForm, self).__init__(*args, **kwargs)
    self.fields['courses'].queryset = Course.objects.filter(institution=self.request.user.institution)