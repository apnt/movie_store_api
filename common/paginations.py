from rest_framework.pagination import PageNumberPagination


class MovieStorePagination(PageNumberPagination):
    """Default pagination for all movie store api viewsets"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
