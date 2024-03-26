from django.db import models
from django.contrib.auth.models import User


class Secretary(models.Model):
    name = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    middlename = models.CharField('Отчество', max_length=50)
    number = models.CharField('Номер телефона', max_length=12, default='')
    email = models.CharField('Почта', max_length=50, default='')
    dateofbirth = models.DateField('Дата рождения', default='1900-01-01', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Secretarie'

class Manager(models.Model):
    name = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    middlename = models.CharField('Отчество', max_length=50)
    number = models.CharField('Номер телефона', max_length=12, default='')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Manager'

class Recipient(models.Model):
    city = models.CharField('Город', max_length=50)
    address = models.CharField('Адрес точки', max_length=150)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)

    def __str__(self):
        return self.city + ', ' + self.address 

class Provider(models.Model):
    name = models.CharField('Название', max_length=150)
    address = models.CharField('Адрес поставщика', max_length=150)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField('Название группы', max_length=100)
    info = models.CharField('Информация', max_length=250)

class Product(models.Model):
    name = models.CharField('Название', max_length=150)
    size = models.CharField('Размер', max_length=10)
    color = models.CharField('Цвет', max_length=50, default='')
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    manufacturer = models.CharField('Производитель', max_length=100)
    country_from = models.CharField('Страна производство', max_length=100)
    quantity = models.IntegerField('Количество', default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product'

class Expenditure(models.Model):
    rec_id = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    contract_number = models.IntegerField('Номер договора')
    sec_id = models.ForeignKey(Secretary, on_delete=models.CASCADE)
    date = models.DateField('Дата отправки из склада', default='2024-01-01')

class Expenditure_add(models.Model):
    exp_id = models.ForeignKey(Expenditure, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField('Количество', default=0)
    price = models.IntegerField('Цена за 1 штук', default=0)

class Coming(models.Model):
    prov_id = models.ForeignKey(Provider, on_delete=models.CASCADE)
    contract_number = models.IntegerField('Номер договора')
    sec_id = models.ForeignKey(Secretary, on_delete=models.CASCADE)
    date = models.DateField('Дата прихода на склада', default='2024-01-01')

class Coming_add(models.Model):
    com_id = models.ForeignKey(Coming, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField('Количество', default=0)
    price = models.IntegerField('Цена за 1 штук', default=0)

class Offs(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField('Количество', default=0)
    reason = models.CharField('Причина списание', max_length=250)
    created_at = models.DateField('Дата списания', default='2024-01-01')