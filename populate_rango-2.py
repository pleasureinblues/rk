import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'twd.settings')

import django
django.setup()

from rango.models import Category, Page


def populate():
    edit_cat('Python')

    edit_cat('Django')

    edit_cat('Other Frameworks')


def edit_cat(name):
    if name == 'Python':
        c = Category.objects.get_or_create(name=name, views=128, likes=64)
    elif name == 'Django':
        c = Category.objects.get_or_create(name=name, views=64, likes=32)
    elif name == 'Other Frameworks':
        c = Category.objects.get_or_create(name=name, views=32, likes=16)

# Start execution here!
if __name__ == '__main__':
    print ("Starting Rango population script...")
    populate()
