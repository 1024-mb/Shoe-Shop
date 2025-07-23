from django.forms import ModelForm
from base.models import Review, User

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = '__all__'

