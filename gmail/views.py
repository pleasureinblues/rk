from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Gmail says hey there world!")


def personalized_name(request, your_name):
    context_dict = {}
    context_dict['name'] = your_name
    return render(request,'gmail/namevame.html',context_dict)

def sumup(request,fv,sv):
    context_dict = {}
    context_dict['fv'] = fv
    context_dict['sv'] = sv
    total = int(fv) + int(sv)
    context_dict['total'] = total
    return render(request,'gmail/sumup.html',context_dict)