from rest_framework.pagination import PageNumberPagination


class CustomPagePaginator(PageNumberPagination):
    page_size_query_param = "limit"
