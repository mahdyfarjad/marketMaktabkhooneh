from django.forms import ValidationError
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
    """
        Represent a customer
    """

    class Meta:
        verbose_name = 'مشتری'
        verbose_name_plural = 'مشتری'
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='کاربر')
    phone = models.CharField('شماره تماس', max_length=20)
    address = models.TextField('آدرس')
    balance = models.PositiveIntegerField('موجودی کیف پول', default=20000)

    def deposit(self, amount):
        try:
            assert amount >= 0
            self.balance += amount
            self.save()
        except:
            raise ValidationError('Error because amount < 0')

    def spend(self, amount):
        try:
            assert amount <= self.balance
            self.balance -= amount
            self.save()
        except:
            raise ValidationError('Error because amount < 0')

    def __str__(self) -> str:
        return self.user.username

class Product(models.Model):
    """
        Represent a product
    """

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصول'

    code = models.CharField('کد', unique=True, max_length=10)
    name = models.CharField('نام', max_length=100)
    price = models.PositiveIntegerField('قیمت')
    inventory = models.PositiveIntegerField('موجودی کالا', default=0)

    def increase_inventory(self, amount):
        try:
            assert amount >= 0
            self.inventory += amount
            self.save()
        except:
           raise ValidationError('Error because amount < 0')

    def decrease_inventory(self, amount):
        try:
            assert amount >= 0
            assert self.inventory >= amount

            self.inventory -= amount
            self.save()
        except:
            raise ValidationError('Error because amount < 0 or inventory < amount')

    def __str__(self) -> str:
        return self.name

class OrderRow(models.Model):
    """
        Represent an orderrow
    """

    class Meta:
        verbose_name = 'لیست سفارش'
        verbose_name_plural = 'لیست سفارش'

    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='محصول')
    order = models.ForeignKey('Order', on_delete=models.PROTECT, verbose_name='سفارش', related_name='rows')
    amount = models.PositiveIntegerField('تعداد')



class Order(models.Model):
    """
        Represent an order
    """

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش'

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, verbose_name='مشتری', related_name='orders')
    order_time = models.DateTimeField('زمان ثبت سفارش', auto_now_add=True, blank=True)
    total_price = models.PositiveIntegerField('مجموع پرداختی', default=0, null=True, blank=True)

    STATUS_SHOPPING = 1
    STATUS_SUBMITTED = 2
    STATUS_CANCELED = 3
    STATUS_SENT = 4

    status_choices = (
        (STATUS_SHOPPING, 'در حال خرید'),
        (STATUS_SUBMITTED, 'ثبت شده'),
        (STATUS_CANCELED, 'لغو شده'),
        (STATUS_SENT, 'ارسال شده'),
    )

    status = models.IntegerField(choices=status_choices)

    @staticmethod
    def initiate(customer):
        try:
            assert Order.objects.filter(customer=customer, status=1).count() == 0, 'You have an order in progress.'
            order = Order.objects.create(customer=customer, status=1)
            order.save()
            return order
        except AssertionError as msg:
            raise AssertionError(msg)

    def add_product(self, product, amount):
        try:
            assert amount > 0, 'Amount msut be a positive integer'
            assert product.inventory >= amount, 'Not enough inventory.'
            assert self.status == 1, 'Your shopping cart is empty.'

            if self.rows.filter(product=product).count() == 0:
                OrderRow.objects.create(product=product, amount=amount, order_id=self.id).save()
                self.total_price += amount * product.price
            else:
                row = self.rows.get(product=product)
                assert row.amount + amount <= product.inventory, 'Not enough of this product available.'
                row.amount += amount
                row.save()
                self.total_price += amount * product.price

            self.save()

        except AssertionError as msg:
            raise AssertionError(msg)
           

    def remove_product(self, product, amount=None):
        try:
            row = self.rows.get(product=product)

            if amount is not None:
                assert amount > 0, 'Amount must be positive integer.' 
                assert row.amount >= amount, 'This number of products does not exist in your shopping cart.'
                row.amount -= amount
                self.total_price -= amount * product.price
                row.save()
            else:
                self.total_price -= row.amount * product.price
                row.delete()

            self.save()
        except AssertionError as msg:
            raise AssertionError(msg)

    def submit(self):
        try:
            
            assert self.status == 1, 'You cannot submit this order because of status.'
            rows = self.rows.all()
        
            for row in rows:
                assert row.product.inventory >= row.amount, 'This number of products does not exist in your shopping cart.'
            assert self.customer.balance >= self.total_price, 'Your account balance is not enough.'
            for row in rows:
                row.product.decrease_inventory(row.amount)
                row.save()
            self.customer.spend(self.total_price)
            self.customer.save()

            self.status = 2
            self.save()
        except AssertionError as msg:
            raise AssertionError(msg)

    def cancel(self):
        try:
            assert self.status == 2, 'The order must be submitted.'
            self.customer.deposit(self.total_price)
            self.customer.save()

            for row in self.rows:
                row.product.increase_inventory(row.amount)
                row.save()
            
            self.total_price = 0
            self.status = 3
            self.save()
        except AssertionError as msg:
            raise AssertionError(msg)

    def send(self):
        try:
            assert self.status == 2, 'The order must be submitted.'

            self.status = 4
            self.save()
        except AssertionError as msg:
            raise AssertionError(msg)