from odoo import models, fields, api
from odoo.tools.float_utils import float_round
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    conversion_uom_id = fields.Many2one(
        'uom.uom',
        string="Conversion UoM (Purchase Unit)",
        tracking=True
    )

    conversion_ratio = fields.Float(
        string="Conversion Ratio",
        digits=(16, 4),
        help="Number of conversion units per 1 main unit",
        tracking=True
    )

    price_per_conversion = fields.Float(
        string="Price per Conversion Unit",
        digits=(16, 2),
        help="Price per conversion unit (e.g., per KG)",
        tracking=True
    )

    base_price = fields.Float(
        string="Price per Base UoM",
        digits=(16, 2),
        help="Price per base unit (e.g., per Unit)",
        tracking=True
    )

    @api.onchange('price_per_conversion', 'conversion_ratio')
    def _onchange_conversion_price(self):
        for rec in self:
            if rec.conversion_ratio:
                new_base = rec.price_per_conversion * rec.conversion_ratio
                rec.base_price = float_round(new_base, precision_digits=2)

    @api.onchange('base_price', 'conversion_ratio')
    def _onchange_base_price(self):
        for rec in self:
            if rec.conversion_ratio:
                new_conv = rec.base_price / rec.conversion_ratio
                rec.price_per_conversion = float_round(new_conv, precision_digits=2)

    # -------------------------
    # CORE CALCULATION METHOD
    # -------------------------

    def _compute_sync_vals(self, vals, rec):
        """Return updated vals per record"""
        r = vals.get('conversion_ratio', rec.conversion_ratio)
        b = vals.get('base_price', rec.base_price)
        c = vals.get('price_per_conversion', rec.price_per_conversion)

        if not r:
            return vals

        new_vals = vals.copy()

        # Priority logic
        if 'base_price' in vals and 'price_per_conversion' not in vals:
            new_vals['price_per_conversion'] = float_round(b / r, precision_digits=2)

        elif 'price_per_conversion' in vals and 'base_price' not in vals:
            new_vals['base_price'] = float_round(c * r, precision_digits=2)

        elif 'conversion_ratio' in vals:
            # prefer base_price as source of truth
            new_vals['price_per_conversion'] = float_round(b / r, precision_digits=2)

        return new_vals

    # -------------------------
    # CREATE
    # -------------------------

    @api.model_create_multi
    def create(self, vals_list):
        new_vals_list = []
        for vals in vals_list:
            dummy = self.new(vals)
            vals = self._compute_sync_vals(vals, dummy)
            new_vals_list.append(vals)

        return super().create(new_vals_list)

    # -------------------------
    # WRITE
    # -------------------------

    def write(self, vals):
        for rec in self:
            new_vals = self._compute_sync_vals(vals, rec)
            super(ProductTemplate, rec).write(new_vals)
        return True

    @api.constrains('conversion_ratio')
    def _check_ratio(self):
        for rec in self:
            if rec.conversion_ratio <= 0:
                raise ValidationError("Conversion ratio must be strictly > 0")