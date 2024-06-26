from django import forms # type: ignore
from .models import *
import datetime


class InventoryForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), empty_label=None, label='Тауарды таңдаңыз')
    quantity = forms.IntegerField(label='Есептен шығару данасы', min_value=1)
    reason = forms.CharField(label='Себебі', widget=forms.Textarea)

class ShipmentForm(forms.Form):
    date_sent = forms.DateField(label='Жіберу күні', initial=datetime.date.today, widget=forms.DateInput(attrs={'type': 'date'}))
    contract_number = forms.CharField(label='Келісімшарт нөмірі', max_length=100)
    recipient = forms.ModelChoiceField(queryset=Recipient.objects.all(), empty_label=None, label='Алушы')
    products = forms.CharField(widget=forms.HiddenInput(), required=False)  # Скрытое поле для передачи выбранных товаров

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['products'].widget.attrs['class'] = 'products-input'  # Добавляем класс для идентификации скрытого поля

        products = Product.objects.all()
        for index, product in enumerate(products):
            self.fields[f'quantity_{index}'] = forms.IntegerField(label=f'{product.name} тауарының данасы', required=False)
            self.fields[f'price_{index}'] = forms.IntegerField(label=f'{product.name} тауарының бағасы', required=False)

class ComingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ComingForm, self).__init__(*args, **kwargs)
        self.fields['sec_id'] = forms.IntegerField(widget=forms.HiddenInput())
        self.fields['date'] = forms.DateField(widget=forms.HiddenInput())

    class Meta:
        model = Coming
        fields = ['prov_id', 'contract_number', 'date']
        labels = {
            'prov_id': 'Жеткізуші',
            'contract_number': 'Келісімшарт нөмері',
            'date': 'Қоймаған келген күні'
        }


class ComingAddForm(forms.ModelForm):
    class Meta:
        model = Coming_add
        fields = ['product_id', 'quantity', 'price']
        labels = {
            'product_id': 'Тауар',
            'quantity': 'Дана',
            'price': '1 дана үшін бағасы'
        }

class ExpenditureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExpenditureForm, self).__init__(*args, **kwargs)
        self.fields['sec_id'] = forms.IntegerField(widget=forms.HiddenInput())
        self.fields['date'] = forms.DateField(widget=forms.HiddenInput())

    class Meta:
        model = Expenditure
        fields = ['rec_id', 'contract_number', 'date']
        labels = {
            'rec_id': 'Алушы',
            'contract_number': 'Келісімшарт нөмері',
            'date': 'Қоймадан жөнелтілген күні'
        }

class ExpenditureAddForm(forms.ModelForm):
    class Meta:
        model = Expenditure_add
        fields = ['product_id', 'quantity', 'price']
        labels = {
            'product_id': 'Тауар',
            'quantity': 'Дана',
            'price': '1 дана үшін бағасы'
        }