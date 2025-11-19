import django_filters
from django.db.models import Q
from .models import User


class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    is_active = django_filters.BooleanFilter()
    role = django_filters.CharFilter(lookup_expr='iexact')
    level = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = User
        fields = ['is_active', 'role', 'level']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value)
        )
