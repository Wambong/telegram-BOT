from django import forms
from .models import Product , Comment , Category


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=100, required=True)
    email = forms.EmailField(label='Электронная почта', required=True)
    full_name = forms.CharField(label='ФИO' , max_length=100 , required=True)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=True)


    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Пароль должен содержать минимум 8 символов.')
        return password


class ProductForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple)
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'color', 'price', 'categories' , 'image' ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_categories(self):
        categories = self.cleaned_data['categories']
        if len(categories) == 0:
            raise forms.ValidationError("Select at least one category.")
        return categories


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'text']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class SearchForm(forms.Form):
    query = forms.CharField(label='Search')



from django import forms
from .models import Newsletter

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['content', 'image']
