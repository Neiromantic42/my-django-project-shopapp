from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    """
    форма для создания аватара
    """
    class Meta:
        model= Profile
        fields = ['avatar', 'bio']