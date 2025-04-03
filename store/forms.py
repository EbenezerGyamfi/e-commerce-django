from django import forms
from store.models import ReviewRating


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ["subject", "review", "rating"]
        # widgets = {
        #     'rating': forms.RadioSelect(),
        #     'comment': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        # }
        # labels = {
        #     'rating': 'Rating',
        #     'comment': 'Comment',
        # }
        # help_texts = {
        #     'rating': 'Please select a rating from 1 to 5.',
        #     'comment': 'Please provide your feedback.',
        # }
