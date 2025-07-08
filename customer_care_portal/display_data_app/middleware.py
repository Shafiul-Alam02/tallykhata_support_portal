from django.shortcuts import redirect

class MyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            # Check if 'next' parameter exists and it's not the OTP authentication page
            if 'next' in request.GET and request.GET['next'] != '/otp_authentication/':
                # Redirect to the OTP authentication page with the 'next' parameter preserved
                return redirect(f'/otp_authentication/')

        # Continue processing the request
        response = self.get_response(request)
        return response
