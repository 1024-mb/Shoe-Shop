from django.forms import ModelForm
from base.models import Review, User
from django.contrib.auth.forms import UserCreationForm

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['description_review', 'stars']


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

class UpdateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make 'email' optional
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = False
        self.fields['password1'].required = False
        self.fields['password2'].required = False
