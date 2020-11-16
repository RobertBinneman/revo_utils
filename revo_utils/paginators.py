from rest_framework.pagination import PageNumberPagination


class CResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100000
