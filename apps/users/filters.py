import django_filters
from .models import User

class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    is_active = django_filters.BooleanFilter()
    role = django_filters.CharFilter(lookup_expr='iexact')
    level = django_filters.CharFilter(lookup_expr='iexact')
    ordering = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('username', 'username'),
            ('coins', 'coins'),
        )
    )

    class Meta:
        model = User
        fields = ['is_active', 'role', 'level', 'ordering']  

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            django_filters.models.Q(username__icontains=value)
            | django_filters.models.Q(first_name__icontains=value)
            | django_filters.models.Q(last_name__icontains=value)
            | django_filters.models.Q(email__icontains=value)
            | django_filters.models.Q(phone_number__icontains=value)
            | django_filters.models.Q(tg_username__icontains=value)
        )
