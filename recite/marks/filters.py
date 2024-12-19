import django_filters
from .models import Mark

class MarkFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label="Title contains")
    category = django_filters.ChoiceFilter(choices=Mark.CATEGORY_CHOICES)
    created_at = django_filters.DateTimeFromToRangeFilter()
    tags = django_filters.CharFilter(method='filter_by_tags', label="Tags contains")

    class Meta:
        model = Mark
        fields = ['title', 'category', 'created_at']
        
    def filter_by_tags(self, queryset, name, value):
        """
        通过 tag 名称过滤 Mark 实例。
        """
        if value:
            # 使用 contains 来模糊匹配 tags 的名称
            return queryset.filter(tags__name__icontains=value)
        return queryset