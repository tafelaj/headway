class RequestFormKwargsMixin(object):

    def get_form_kwargs(self):
        kwargs = super(RequestFormKwargsMixin, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs


class RequestKwargModelFormMixin(object):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(RequestKwargModelFormMixin, self).__init__(*args, **kwargs)