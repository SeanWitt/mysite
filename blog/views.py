from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from blog.forms import EmailPostForm, CommentForm
from blog.models import Post, Comment
from mysite.settings import EMAIL_HOST_USER


class PostListView(ListView):
    """
    Get All published Posts View
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    """
    Get Detail on a Post View
    :param request: Request Object
    :param year: Integer from url
    :param month: Integer from url
    :param day: Integer from url
    :param post: Integer from url
    """
    post = get_object_or_404(Post,
                             slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                            )
    comments = post.comments.filter(active=True)
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request,
           'blog/post/detail.html',
           {'post':post,
            'comments': comments, 
            'comment_form': comment_form})
    
def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            cleaned_name = cd.get('name') 
            cleaned_email = cd.get('email')
            cleaned_comments = cd.get('comments')
            cleaned_to_field = cd.get('to')
            
            subject = '{} ({}) Recommends you read "{}"'.format(
                cleaned_name,
                cleaned_email,
                cleaned_comments
            )
            message = "Read '{}'' at {}\n\n{}\'s comments: {}".format(
                post.title,
                post_url,
                cleaned_name,
                cleaned_comments
            )
            send_mail(
                subject,
                message,
                EMAIL_HOST_USER,
                [cleaned_to_field],
            )
            sent = True
            
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent
                  })


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    
    if tag_slug:
        tag = get_object_or_404(tag, slug=tag_slug)
        object_list.filter(tags__in=[tag])
    
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {
                      'posts': posts,
                      'page': page,
                      'tag': tag
                  }
    )
