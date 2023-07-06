from django.db import models
from home_automation.user.models import MyUser
from django.utils.text import slugify
from django.forms import ValidationError  
from .utils import get_expiry_date, date_has_expired
from import_export import resources

class CommonModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True

class Plan(CommonModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(blank=True)
    description = models.TextField()
    VALIDITIES = (
        # Months Giving in Integer for Calculating the Expiry date.
        (1, '1 Month'),
        (6, '6 Months'),
        (12, '12 Months'),
    )
    validity = models.IntegerField(choices=VALIDITIES)
    DEVICES = (
        (1, '1 Devices'),
        (3, '3 Devices'),
        (5, '5 Devices'),
        (6, '6 Devices'),
        (7, '7 Devices'),
        (10, '10 Devices'),
    )
    device =  models.IntegerField(choices=DEVICES)
    price = models.DecimalField(max_digits=6 , decimal_places=2)
    discount = models.DecimalField(default=0, max_digits=5 , decimal_places=2, null=True, blank=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('price',)

    @property
    def final_price(self):
        discount = self.discount or 0
        return self.price - discount

    # Generate Auto Slug
    def slug_generate(self):
        return slugify(self.name, allow_unicode=True)

    def clean(self):
        slug_manual = self.slug
        if not slug_manual and Plan.objects.filter( slug=self.slug_generate() ).exists():
            raise ValidationError("Slug already exists")
        self.is_cleaned = True

    def save(self, *args, **kwargs):
        if not self.is_cleaned:
            self.clean()
        slug_manual = self.slug
        self.slug = self.slug = slug_manual or self.slug_generate()
        super().save(*args, **kwargs)
        
class Coupon(CommonModel):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    expiry_date = models.DateField()
    TYPES = (
        ('amount', 'Amount'),
        ('percent', 'Percent'),
    )
    discount_type = models.CharField(choices=TYPES, max_length=20)
    discount = models.DecimalField(max_digits=5 , decimal_places=2, verbose_name="Amount / Percent")

    use_limit = models.IntegerField(null=True, blank=True)
    coupon_used = models.IntegerField(default=0) 
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    @property
    def coupon_limit(self):
        if self.use_limit:
            return f"{self.coupon_used}/{self.use_limit}"
        return f"{self.coupon_used} times used"

class BillingDetail(CommonModel):
    # TODO: Add More Billing Data 
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    # billing_name = models.CharField(max_length=150, null=True) 
    # billing_email = models.EmailField(max_length=100, null=True) 
    # billing_mobile = models.CharField(max_length=15, null=True) 
    # billing_address = models.TextField()
    status = models.BooleanField(default=True, verbose_name='Is Active')

    def __str__(self):
        return f"{self.user.username}"

CURRENCY_OPTIONS = (
    ('INR', 'INR'),
    ('USD', 'USD'),
)
class Transaction(CommonModel):
    # TODO: Add More Payment Data from API Response
    bill = models.ForeignKey(BillingDetail, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=5 , decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_OPTIONS, default='INR')
    order_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.order_id)


# User Current Plan
class UserPackage(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True)
    expiry_date = models.DateField()
    status = models.BooleanField(default=True) # Disable the status if user wants to buy advance renewal
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.email)

    @property
    def is_expired(self):
        return date_has_expired(self.expiry_date)