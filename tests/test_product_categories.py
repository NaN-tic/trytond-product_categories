# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
from decimal import Decimal
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool


class TestProductCategoriesCase(ModuleTestCase):
    'Test Product Categories module'
    module = 'product_categories'


    @with_transaction()
    def test_categories(self):
        'Test the validate categories'
        pool = Pool()
        Category = pool.get('product.category')
        Template = pool.get('product.template')
        Uom = pool.get('product.uom')

        uom, = Uom.search([], limit=1)

        category = Category()
        category.name = "Category"
        category.save()
        cat1 = Category()
        cat1.name = "Cat1"
        cat1.kind = 'view'
        cat1.required = True
        cat1.unique = True
        cat1.save()
        cat1a = Category()
        cat1a.name = "Cat1a"
        cat1a.parent = cat1
        cat1a.save()

        template = Template()
        template.name = 'Template'
        template.type = 'goods'
        template.list_price = Decimal(20)
        template.cost_price = Decimal(10)
        template.default_uom = uom
        template.categories = [category]
        self.assertRaises(Exception, Template.create, [template._save_values])
        template.categories = [category, cat1, cat1a]
        template.save()
        self.assertEqual(len(template.categories), 3)



def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        TestProductCategoriesCase))
    return suite
