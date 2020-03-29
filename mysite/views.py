from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from users.forms import CustomUserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


def passwordchange(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        p_form = PasswordChangeForm(request.POST, instance=user)
        if p_form.is_valid():
            Password_form = p_form.save(commit=False)
            update_session_auth_hash(request, user)  # Important!
            return render(request, 'user_list.html',
                          {'user': user})
    else:
        # edit
        p_form = PasswordChangeForm(instance= user)
    return render(request, 'registration/change_password.html', {'p_form': p_form})
