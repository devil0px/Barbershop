from django import forms
from .models import Review

class ReviewReplyForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['reply_text']
        widgets = {
            'reply_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'اكتب ردك على التقييم هنا...'
            })
        }
        labels = {
            'reply_text': 'الرد على التقييم'
        }
