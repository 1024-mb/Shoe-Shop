from django.forms import ModelForm
from base.models import Review

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = '__all__'


