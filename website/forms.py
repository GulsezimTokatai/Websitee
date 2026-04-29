from django import forms
from .models import Profile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio' ,'phone', 'address']
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Өзіңіз туралы қысқаша жазыңыз...', 'class': 'form-input'}),
            'avatar': forms.FileInput(attrs={'class': 'form-input-file'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (777) 000-00-00'}),
            'address': forms.TextInput(attrs={'placeholder': 'Қала, көше, үй'}),
        }