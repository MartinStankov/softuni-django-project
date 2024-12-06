from django import forms
from magic_forum.comments.models import Comment


class CommentForm(forms.ModelForm):
    is_anonymous = forms.BooleanField(required=False, label='Post Anonymously')

    class Meta:
        model = Comment
        fields = ['content', 'is_anonymous']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your comment here...',
                'class': 'comment-input'
            }),
        }
