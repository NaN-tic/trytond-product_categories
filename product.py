# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = ['Template', 'Category']

"""
Add to categories the following:
 - New type, view --> Like root but inside of it
 - New checkboxes:
    * Unique --> One one child can be in a product at a time
    * Required --> One of its child must be in the product
    * Accounting --> Category related in accounting, will not appear in the
      Many2Many view, but it will on the Accounting Category field
"""


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'

    @classmethod
    def validate(cls, vlist):
        super(Template, cls).validate(vlist)
        cls._check_categories(vlist)

    @classmethod
    def _check_categories(cls, templates):
        Category = Pool().get('product.category')

        if not Transaction().context.get('check_categories', True):
            return

        required_categories = Category.search([
                ('required', '=', True),
                ('kind', '=', 'view'),
            ])

        unique_categories_ids = [c.id for c in Category.search([
                ('unique', '=', True),
                ('kind', '=', 'view'),
            ])]

        childs_required = []
        for required in required_categories:
            required_id = required.id
            childs = Category.search([
                    ('parent', 'child_of', [required_id]),
                    ('id', '!=', required_id),
                    ])
            childs_required.append([c.id for c in childs])

        for template in templates:
            if childs_required:
                tpl_categories_ids = [c.id for c in template.categories]
                exisits = cls.check_if_exisit(childs_required, tpl_categories_ids)
                if not exisits:
                    cat_required = [c.name for c in required_categories]
                    raise UserError(gettext(
                        'product_categories.missing_categories',
                        template=template.rec_name,
                        categories=', '.join(cat_required[:3])))

            if unique_categories_ids:
                childs = Category.search([
                    ('parent', 'child_of', unique_categories_ids),
                    ('id', 'not in', unique_categories_ids)])

                unique_values = [a for a in template.categories if a in childs]
                # Get all parents to compare them
                parents = [u.parent.id for u in unique_values]

                if len(parents) != len(set(parents)):
                    raise UserError(gettext(
                        'product_categories.repeated_unique',
                        template=template.rec_name))

    @staticmethod
    def check_if_exisit(list1, list2):
        for template in list2:
            for required_parent in list1:
                if template in required_parent:
                    list1.remove(required_parent)
        return list1 == []


class Category(metaclass=PoolMeta):
    __name__ = 'product.category'
    kind = fields.Selection([
        ('other', 'Other'),
        ('view', 'View'),
        ], 'Kind', required=True)
    unique = fields.Boolean('Unique',
        states={
            'invisible': Eval('kind') != 'view',
        }, depends=['kind'])
    required = fields.Boolean('Required',
        states={
            'invisible': Eval('kind') != 'view',
        }, depends=['kind'])
    sequence = fields.Integer('Sequence')

    @classmethod
    def __setup__(cls):
        super(Category, cls).__setup__()
        cls._order.insert(0, ('sequence', 'ASC'))

    @staticmethod
    def default_kind():
        return 'other'
