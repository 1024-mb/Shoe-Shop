from django.forms import ModelForm
from base.models import Review, User

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = '__all__'

class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class SignupForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

