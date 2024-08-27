from django.shortcuts import render, redirect
from django.views.generic import FormView
from .form import UserRegisterForm, UserUpdateForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View

class UserRegisterForm(FormView):
    template_name = 'account/registration.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        print(form.cleaned_data)
        user = form.save()
        login(self.request, user)
        print(user)
        return super().form_valid(form)
    
class UserLoginView(LoginView):
    template_name = 'account/login.html'
    def get_success_url(self):
        return reverse_lazy('profile')

# class UserLogoutView(LogoutView):
#     print("up")
#     def get_success_url(self):
#         print("mup")
#         if self.request.user.is_authenticated:
#             logout(self.request)
#             print("robiul")
#         return reverse_lazy('home')
class logoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")

class UserBankAccountUpdateView(View):
    template_name = 'account/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})
    
    
    
