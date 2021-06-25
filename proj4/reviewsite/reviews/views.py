import re

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Review, Doctor, Forbidden, Excepted
from django.contrib.auth.decorators import permission_required
from django.core.cache import caches
from django.views.decorators.cache import cache_page


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


@cache_page(60 * 15, cache='default')
def review_write(request, doc_id):
    doctor = get_object_or_404(Doctor.objects.prefetch_related('speciality'), pk=doc_id)
    context = {
        'doctor': doctor,
    }
    try:
        print(request.user)
        entered_review = request.POST['review_text']
    except KeyError:
        return render(request, 'reviews/writing.html', context)
    else:
        review = Review.objects.create(doctor=doctor, raw_review=entered_review, ip_address=get_client_ip(request))
        if not request.user.is_anonymous:
            review.user = request.user
        review.edit_review()
        return HttpResponseRedirect(reverse('success'))


def success(request):
    return render(request, 'reviews/sent.html')


@permission_required('reviews.can_moderate_views')
def review_list(request):
    cache = caches['default']
    forbidden_list = Forbidden.objects.all()
    excepted_list = Excepted.objects.values_list('word', flat=True)
    reviews_list = cache.get('reviews_list')
    if reviews_list is None:
        reviews_list = Review.objects.order_by('created_at').prefetch_related('doctor__speciality'). \
            select_related('user')
        cache.add('reviews_list', reviews_list, 60 * 60)
    for review in reviews_list:
        for forb in forbidden_list:
            sample = r' (\w*' + forb.word + r'\w*)([.,!?]?) ?'
            review.edited_review = re.sub(sample, r' \1\2@m@ ', review.edited_review, flags=re.IGNORECASE)
    context = {'reviews_list': reviews_list,
               'excepted_list': excepted_list
               }
    return render(request, 'reviews/listing.html', context)
