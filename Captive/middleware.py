class RestrictSubscriberAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Middleware logic here
        response = self.get_response(request)
        return response
