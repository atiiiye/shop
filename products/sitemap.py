from django.contrib.sitemaps import Sitemap

from products.models import Product


class ProductSitemap(Sitemap):
    change_freq="weekly"
    priority=1
    # protocol = "https"

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated