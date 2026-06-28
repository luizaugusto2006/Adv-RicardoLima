from django import forms
from .models import Advogado, Cliente, Processo, Juiz, Forum


class ProcessoForm(forms.ModelForm):
    class Meta:
        model = Processo
        fields = ['numero_processo', 'cliente', 'advogado', 'juiz', 'forum', 'status', 'resumo_sentenca']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(ativo=True)
        self.fields['advogado'].queryset = Advogado.objects.filter(ativo=True)
        self.fields['juiz'].queryset = Juiz.objects.filter(ativo=True)
        self.fields['forum'].queryset = Forum.objects.filter(ativo=True)
        for field_name, field in self.fields.items():
            if field_name not in ['status', 'resumo_sentenca']:
                field.widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
        self.fields['resumo_sentenca'].widget.attrs.update({'rows': '4', 'placeholder': 'Digite um resumo detalhado da causa...'})


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'cpf', 'telefone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class AdvogadoForm(forms.ModelForm):
    class Meta:
        model = Advogado
        fields = ['nome', 'oab', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class JuizForm(forms.ModelForm):
    class Meta:
        model = Juiz
        fields = ['nome', 'email', 'forum']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['forum'].queryset = Forum.objects.filter(ativo=True)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum
        fields = ['nome', 'cidade', 'uf']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class UsuarioForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Senha")
    confirmar_senha = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirmar Senha")

    class Meta:
        from django.contrib.auth.models import User
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmar = cleaned_data.get('confirmar_senha')
        if senha and confirmar and senha != confirmar:
            raise forms.ValidationError("As senhas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['senha'])
        if commit:
            user.save()
        return user
