from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Review
from barbershops.models import Barbershop

class MerchantReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'reviews/merchant_review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        """
        Return the list of reviews for all barbershops owned by the current user.
        """
        return Review.objects.filter(barbershop__owner=self.request.user).order_by('-created_at')


class ReviewListView(ListView):
    model = Review
    template_name = 'reviews/list.html'
    context_object_name = 'reviews'
    
    def get_queryset(self):
        return Review.objects.filter(is_approved=True).order_by('-created_at')

class ReviewDetailView(DetailView):
    model = Review
    template_name = 'reviews/detail.html'
    context_object_name = 'review'

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    template_name = 'reviews/create.html'
    fields = ['rating', 'comment']
    
    def dispatch(self, request, *args, **kwargs):
        self.barbershop = get_object_or_404(Barbershop, pk=kwargs['barbershop_id'])

        # Check if the user has already reviewed this barbershop
        existing_review = Review.objects.filter(barbershop=self.barbershop, customer=request.user).first()
        if existing_review:
            messages.info(request, 'لقد قمت بتقييم هذا المحل من قبل. يمكنك تعديل تقييمك هنا.')
            return redirect('reviews:edit', pk=existing_review.pk)

        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.customer = self.request.user
        form.instance.barbershop = self.barbershop
        messages.success(self.request, 'تم إضافة تقييمك بنجاح!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('barbershops:detail', kwargs={'pk': self.barbershop.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barbershop'] = self.barbershop
        return context


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    template_name = 'reviews/edit.html' # New template
    fields = ['rating', 'comment']

    def get_queryset(self):
        # Ensure user can only edit their own reviews
        return Review.objects.filter(customer=self.request.user)

    def get_success_url(self):
        # Redirect back to the barbershop detail page
        return reverse_lazy('barbershops:detail', kwargs={'pk': self.object.barbershop.pk})

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل تقييمك بنجاح!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barbershop'] = self.object.barbershop
        return context


class BarbershopReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'reviews/barbershop_review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        """
        Verify that the logged-in user is the owner of the barbershop.
        """
        self.barbershop = get_object_or_404(Barbershop, pk=self.kwargs['barbershop_id'])
        if self.barbershop.owner != self.request.user:
            raise PermissionDenied("You do not have permission to view these reviews.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return the list of reviews for the specific barbershop.
        """
        return Review.objects.filter(barbershop=self.barbershop).order_by('-created_at')

    def get_context_data(self, **kwargs):
        """
        Add the barbershop object to the context.
        """
        context = super().get_context_data(**kwargs)
        context['barbershop'] = self.barbershop
        return context

