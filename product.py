# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
import collections


__metaclass__ = PoolMeta

__all__ = ['Template', 'ProductCategories', 'Category']
"""
Add to categories the following:
 - New type, view --> Like root but inside of it
 - New checkboxes:
    * Unique --> One one child can be in a product at a time
    * Required --> One of its child must be in the product
    * Accounting --> Category related in accounting, will not appear in the
      Many2Many view, but it will on the Accounting Category field

Add to products the following:
 - Categories: Many2Many field relating a product with categories
 - Accounting category: Same as before but Many2One and only getting those with
   the accounting tag set

   This module should be refractored in version 4.0

"""


class Template:
    __name__ = 'product.template'
    # TODO: Remove in 4.0
    categories = fields.Many2Many('product.template-product.categories',
        'product', 'category', 'Tags')

    @classmethod
    def __setup__(cls):
        super(Template, cls).__setup__()
        # TODO: Remove in 4.0
        cls.category.domain = [('kind', '=', 'accounting')]
        cls._error_messages.update({
                'missing_categories': ('The template %s is missing some '
                    'required categories'),
                'repeated_unique': ('The template %s has repeated '
                    'categories marked as unique'),
                })

    @classmethod
    def validate(cls, vlist):
        super(Template, cls).validate(vlist)
        cls._check_categories(vlist)

    # TODO: Update in 4.0 to work with new categories field
    @classmethod
    def _check_categories(cls, template):
        Categories = Pool().get('product.category')
        required_categories = Categories.search([
            ('required', '=', True),
            ('kind', '=', 'view')])
        unique_categories = Categories.search([
            ('unique', '=', True),
            ('kind', '=', 'view')])

        required_categories = [r.id for r in required_categories]
        unique_categories_ids = [u.id for u in unique_categories]

        childs_required = Categories.search([
                ('parent', 'child_of', required_categories),
                ('id', 'not in', required_categories)])
        childs_required = [c.id for c in childs_required]

        for id in template:
            template = cls(id)

            template_categories_ids = [c.id for c in template.categories]

            exisits = cls.check_if_exisit(childs_required,
                template_categories_ids)

            if not exisits:
                cls.raise_user_error('missing_categories', template.rec_name)

            childs = Categories.search([
                ('parent', 'child_of', unique_categories_ids),
                ('id', 'not in', unique_categories_ids)])

            unique_values = filter(lambda a: a in childs, template.categories)
            # Get all parents to compare them
            parents = [u.parent.id for u in unique_values]

            if len(parents) != len(set(parents)):
                cls.raise_user_error('repeated_unique', template.rec_name)

    @staticmethod
    def check_if_exisit(list1, list2):
        list_1 = collections.Counter(list1)
        list_2 = collections.Counter(list2)

        if len(list1) > len(list2):
            list_1.subtract(list_2)
            return all(v >= 0 for k, v in list_1.items())
        else:
            list_2.subtract(list_1)
            return all(v >= 0 for k, v in list_2.items())


class ProductCategories(ModelSQL):
    "Categories for products"
    __name__ = 'product.template-product.categories'

    product = fields.Many2One('product.template', 'Product', required=True,
        ondelete='CASCADE', select=True)
    category = fields.Many2One('product.category', 'Category', required=True,
        domain=[('kind', 'not in', ['view', 'accounting'])],
        ondelete='CASCADE', select=True)


class Category:
    __name__ = 'product.category'

    kind = fields.Selection([
        ('other', 'Other'),
        ('accounting', 'Accounting'),
        ('view', 'View'),
        ], 'Kind', required=True)

    unique = fields.Boolean('Unique', states={
        'invisible': Eval('kind') != 'view',
        })
    required = fields.Boolean('Required', states={
        'invisible': Eval('kind') != 'view',
        })

    @staticmethod
    def default_kind():
        return 'other'
