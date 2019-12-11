# Copyright 2019 PLANA Solutions - Boyan Rabchev
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, _


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    out_task_id = fields.Many2one(
        'stock.picking.type',
        'Project Task Material',
    )

    def create_task_material_picking_type(self, warehouse, pick):
        loc = warehouse._get_input_output_locations(
            warehouse.reception_steps,
            warehouse.delivery_steps
        )

        sequence = self.env['ir.sequence'].sudo().create({
            'name': warehouse.name + ' ' + _('Sequence project task material'),
            'prefix': warehouse.code + '/CONSUM/', 'padding': 5,
            'company_id': warehouse.company_id.id,
        })
        return self.env['stock.picking.type'].create({
            'name': _('Project Task Material Operations'),
            'code': 'outgoing',
            'use_create_lots': False,
            'use_existing_lots': True,
            'sequence': pick.sequence + 1,
            'default_location_src_id': loc[1].id,
            'sequence_id': sequence.id,
            'warehouse_id': warehouse.id,
            'color': pick.color,
        }).id

    # Override to create project task material picking type
    def create_sequences_and_picking_types(self):
        res = super(Warehouse, self).create_sequences_and_picking_types()
        pick = self.env['stock.picking.type'].browse(res['out_type_id'])
        res['out_task_id'] = self.create_task_material_picking_type(self, pick)
        return res

    # Override to add project task material picking type in not presant
    def write(self, vals):
        res = super(Warehouse, self).write(vals)
        if res:
            for w in self:
                if not w.out_task_id:
                    pick_id = self.env['stock.picking.type'].search([
                        ('warehouse_id', '=', w.id),
                        ('name', '=', _('Project Task Material Operations'))
                    ], limit=1).id
                    if not pick_id:
                        pick_id = self.create_task_material_picking_type(
                            w, w.out_type_id
                        )
                    w.out_task_id = pick_id
        return res
