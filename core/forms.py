from django import forms
from .models import ElementoDespesa

class UploadPlanilhaForm(forms.Form):
    arquivo = forms.FileField(
        label='Planilha CSV/Excel',
        help_text='Arquivo com colunas: codigo, nome, descricao',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        })
    )
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data['arquivo']
        tamanho_maximo = 100 * 1024 * 1024
        
        if arquivo.size > tamanho_maximo:
            raise forms.ValidationError(f'Arquivo muito grande. Máximo: 10MB')
        
        extensao = arquivo.name.split('.')[-1].lower()
        if extensao not in ['csv', 'xlsx', 'xls']:
            raise forms.ValidationError('Formato inválido. Use .csv, .xlsx ou .xls')
        
        return arquivo


class ElementoDespesaForm(forms.ModelForm):
    class Meta:
        model = ElementoDespesa
        fields = ['codigo', 'nome', 'descricao']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 339030'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Material de Consumo'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Descrição detalhada do elemento de despesa...'
            }),
        }