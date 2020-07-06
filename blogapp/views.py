from django.shortcuts import render , HttpResponse ,get_object_or_404 , redirect
from .models import author ,  category , article , comment
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import createForm , registerUser , createauthor , commentForm , createCategory
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
# Create your views here.

def index(request):
    post = article.objects.all()  # pylint: disable=maybe-no-member
    search = request.GET.get('q')
    if search:
        post = post.filter(
            Q(title__icontains=search) | Q(body__icontains=search)
        )
    paginator = Paginator(post, 8) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    total_article = paginator.get_page(page_number)
    context = {
        "post" : total_article
    }
    return render(request , "index.html" , context)

def getauthor(request , name):
    post_author = get_object_or_404(User , username=name) # pylint: disable=maybe-no-member
    auth = get_object_or_404(author , name=post_author.id)
    post = article.objects.filter(article_author=auth.id)  # pylint: disable=maybe-no-member
    context={
        "auth" : auth,
        "post" : post
    }
    return render(request , "profile.html" ,context)

def getsingle(request , id):
    post = get_object_or_404(article , pk=  id)
    first = article.objects.first()  # pylint: disable=maybe-no-member
    last = article.objects.last()   # pylint: disable=maybe-no-member
    getcomment = comment.objects.filter(post=id) # pylint: disable=maybe-no-member
    related_post = article.objects.filter(category=post.category).exclude(id=id)[:4]  # pylint: disable=maybe-no-member
    form = commentForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.post = post
        instance.save()
    context = {
        "post" : post,
        "first" : first,
        "last" : last,
        "related_post" : related_post,
        "form" : form,
        "comment" : getcomment
    }
    return render(request , "single.html" , context)    

def gettopic(request , name):
    cat = get_object_or_404(category , name=name)
    post = article.objects.filter(category=cat.id) # pylint: disable=maybe-no-member
    context={
        "post" : post,
        "cat" : cat
    }
    return render(request , "category.html" , context) 

def getlogin(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == "POST":
            user = request.POST.get('user')
            password = request.POST.get('pass')
            auth = authenticate(request, username=user , password=password)
            if auth is not None:
                login(request , auth)
                return redirect('index')    
            else:
                messages.add_message(request, messages.ERROR, 'Username or Password mismatched .')    
    return render(request, "login.html")    


def getlogout(request):
    logout(request)
    return redirect('index')


def getcreate(request):
    if request.user.is_authenticated:
        u = get_object_or_404(author , name=request.user.id)
        form = createForm(request.POST or None , request.FILES or None )
        if form.is_valid():
            instance = form.save(commit = False)
            instance.article_author = u
            instance.save()
            return redirect('index')
        context={
        "form": form 
        }
        return render(request , "create.html" , context)     
    else:
        return redirect('login')


def getprofile(request):
    if request.user.is_authenticated:
        user = get_object_or_404(User , id=request.user.id)
        author_profile = author.objects.filter(name=user.id) # pylint: disable=maybe-no-member
        if author_profile:
            authorUser = get_object_or_404(author , name=request.user.id)
            post=article.objects.filter(article_author=authorUser.id) # pylint: disable=maybe-no-member
            context={
                "post" : post,
                "user" : authorUser
            }
            return render(request , "logged_in_profile.html" , context)     
        else:
            form = createauthor(request.POST or None ,  request.FILES or None)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.name = user
                instance.save()
                return redirect('profile')
            context = {
                "form" : form
            }
            return render(request , "createauthor.html" , context)

    else:
        return redirect('login')  



def getupdate(request , id):
    if request.user.is_authenticated:
        u = get_object_or_404(author , name=request.user.id)
        post = get_object_or_404(article , id=id)
        form = createForm(request.POST or None , request.FILES or None , instance=post )
        if form.is_valid():
            instance = form.save(commit = False)
            instance.article_author = u
            instance.save()
            messages.success(request , 'Article has been updated successfully')
            return redirect('profile')

        context={
        "form": form 
        }
        return render(request , "create.html" , context)     
    else:
        return redirect('login')



def getdelete(request , id):
    if request.user.is_authenticated:
        post = get_object_or_404(article , id=id)
        post.delete()
        messages.error(request , 'Article has been deleted')
        return redirect('profile')
    else:
        return redirect('login')


def getregister(request):
    form = registerUser(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request , "Registration successfully completed")
        return redirect('login') 

    context={
        "form" : form
    }
    return render(request , "register.html" , context)


def categoryList(request):
    catagorys = category.objects.all()  # pylint: disable=maybe-no-member
    context = {
        "catagorys" : catagorys
    }
    return render(request , "categorylist.html" , context)    

def categoryCreat(request):
    form = createCategory(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        return redirect('categoryList')  
    context = {
        "form" : form
    }    
    return render(request , "categoryCreat.html" , context)
    