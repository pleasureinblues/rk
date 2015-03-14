from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page, Contact
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.forms import CategoryForm, PageForm, ContactForm, UserForm, UserProfileForm
from datetime import datetime
from rango.bing_search import run_query

import os

def index(request):

    category_list = Category.objects.order_by('-name')[:5]
    page_list = Page.objects.order_by('-title')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).days > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits

    response = render(request,'rango/index.html', context_dict)

    return response







def about(request):
    context_dict = {}
    context_dict['abc'] = 'We are here'
    return render(request, 'rango/about.html', context_dict)


def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    if not context_dict['query']:
        context_dict['query'] = category.name

    return render(request, 'rango/category.html', context_dict)




#Add Category Veiw
@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index (request)
        else:
            print (form.errors)
    else:
        form = CategoryForm()

    return render(request, 'rango/add_category.html', {'form':form})







def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index (request)
        else:
            print (form.errors)
    else:
        form = ContactForm()

    return render(request, 'rango/contact_form.html', {'form':form})








# Add Page View
@login_required()
def add_page(request,category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
                cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here.

                #return HttpResponseRedirect(reverse('rango:category',args=[cat.slug]))
                return redirect(reverse('rango:category',args=[category_name_slug]))
            print (form.errors)
    else:
        form = PageForm()

    context_dict = {'form':form, 'category': cat}

    return render(request, 'rango/add_page.html', context_dict)






def contact_messages(request):
    message_list = Contact.objects.all()
    context_dict = {'messages': message_list}
    return render(request,'rango/contact_messages.html',context_dict,)


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        page_id = request.GET['page_id']
        try:
            page = Page.objects.get(id=page_id)
            page.views = page.views + 1
            page.save()
            url = page.url
        except:
            pass

    return redirect(url)


@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id  = request.GET['category_id']

    likes = 0

    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)


#Helper Function for Inline Category Suggestions
def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

        if max_results > 0:
            if len(cat_list) > max_results:
                cat_list = cat_list[:max_results]

        return cat_list


def suggest_category(request):

        cat_list = []
        starts_with = ''
        if request.method == 'GET':
                starts_with = request.GET['suggestion']
        if len(starts_with) > 0:
            cat_list = get_category_list(8, starts_with)
        else:
            cat_list = Category.objects.all()

        return render(request, 'rango/category_list.html', {'cat_list': cat_list })


def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}

    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category = category, title = title, url = url)

            pages = Page.objects.filter(category=category).order_by('-views')

            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages
    return render(request, 'rango/page_list.html', context_dict)



def gallery(request):

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    img_folder = 'static/gallery/'
    images_path = (
    os.path.join(BASE_DIR, img_folder)
)

    img_list =os.listdir(images_path)
    return render(request, 'rango\gallery.html', {'images': img_list})