from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy
from allauth.account.views import SignupView
from .forms import ProfileForm
from .models import Profile


class CustomSignupView(SignupView):
    def form_valid(self, form):
        # Call the parent form_valid which creates the user
        response = super().form_valid(form)
        # Add success message
        messages.success(
            self.request,
            f'Account created successfully for {form.cleaned_data.get("username")}! Please log in to continue.'
        )
        return response
    
    def form_invalid(self, form):
        # Add error message when form is invalid
        messages.error(
            self.request,
            'There were errors in your signup form. Please check the details below.'
        )
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('account_login')  # Redirect to login after signup


@login_required
def complete_profile_view(request):
    # Get or create the user's profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')  # Redirect to dashboard/home after saving
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)  # Initialize form with profile data
    
    return render(request, 'accounts/complete_profile.html', {'form': form})


@login_required
def profile_view(request):
    """Main profile page with profile info and password change"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Initialize forms
    profile_form = ProfileForm(instance=profile)
    password_form = PasswordChangeForm(request.user)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            # Handle profile update
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                # Update user's email if changed
                email = profile_form.cleaned_data.get('email')
                if email and email != request.user.email:
                    request.user.email = email
                    request.user.save()
                messages.success(request, '✅ Profile updated successfully!')
                return redirect('profile')
            else:
                messages.error(request, '❌ Please correct the errors in the profile form.')
        
        elif form_type == 'password':
            # Handle password change
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, '✅ Password changed successfully!')
                return redirect('profile')
            else:
                messages.error(request, '❌ Please correct the errors in the password form.')
    
    context = {
        'profile': profile,
        'profile_form': profile_form,
        'password_form': password_form,
    }
    
    return render(request, 'accounts/profile.html', context)