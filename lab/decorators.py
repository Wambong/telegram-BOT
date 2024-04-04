from django.http import HttpResponseForbidden
from functools import wraps
from django.shortcuts import redirect

def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()  # Return a 403 Forbidden response
    return _wrapped_view

def add_product_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated and allowed to add products
        if request.user.is_authenticated and request.user.has_perm('app.add_product'):
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to a different page or display an error message
            return redirect('product_list')  # Adjust this to your desired redirect URL

    return _wrapped_view