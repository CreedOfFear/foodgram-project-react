from rest_framework.pagination import PageNumberPagination

#class six_pagination(PageNumberPagination):
#    page_size = 6
#    page_size_query_param = 'page_size'
#    max_page_size = 6


class CustomPagination(PageNumberPagination):
    page_size_query_param = "limit"