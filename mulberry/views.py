

# Function to get the next url
def get_next_url(request):
    next_url = request.META.get('HTTP_REFERER')
    return next_url