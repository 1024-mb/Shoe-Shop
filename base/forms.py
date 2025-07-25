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

