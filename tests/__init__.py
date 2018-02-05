# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.product.tests.test_product_categories import suite
except ImportError:
    from .test_product_categories import suite

__all__ = ['suite']
