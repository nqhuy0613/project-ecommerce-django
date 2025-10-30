from django.db import models


from django.urls import reverse


class Category(models.Model):

    name = models.CharField(max_length=250, db_index=True)

    slug = models.SlugField(max_length=250, unique=True)


    class Meta:

        verbose_name_plural = 'categories'


    def __str__(self):

        return self.name


    def get_absolute_url(self):

        return reverse('list-category', args=[self.slug])



class Product(models.Model):

    #FK 

    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE, null=True)


    title = models.CharField(max_length=250)

    color = models.CharField(max_length=250, default='Unknown')

    description = models.TextField(blank=True)

    slug = models.SlugField(max_length=255)

    price = models.BigIntegerField()

    screen_size = models.CharField(max_length=250, default='Unknown')

    ram = models.CharField(max_length=250, default='Unknown')

    pin = models.CharField(max_length=250, default='Unknown')

    image = models.ImageField(upload_to='images/')


    class Meta:

        verbose_name_plural = 'products'


    def __str__(self):

        return self.title



    def get_absolute_url(self):

        return reverse('product-info', args=[self.slug])



