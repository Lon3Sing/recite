import django_filters
from .models import Mark

class MarkFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label="Title contains")
    category = django_filters.ChoiceFilter(choices=Mark.CATEGORY_CHOICES)
    created_at = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Mark
        fields = ['title', 'category', 'created_at']