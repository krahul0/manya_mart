
from .models import Category


def menu_links(request):
    #fetch all categories from DB
    links = Category.objects.all()
    return dict(links=links)