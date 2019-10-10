# -*- coding: utf-8 -*-
# © 2017 Leonardo Rochael Almeida
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import contextlib
import pprint

from logging import getLogger

from openerp import models
# from openerp.addons.base.ir import ir_model


_log = getLogger(__name__)


MAP_KEY = 'store_get_delay_map'
DELAYED_KEY = 'delay_store_set_list'
DELAYED_TODO_KEY = 'delay_recompute_todo'


class patch_into(object):
    """
    Decorate method to monkey-patch into a class
    """

    def __init__(self, target):
        self.target = target

    def __call__(self, method):
        _log.info("patching %s into %s", method.func_name, self.target)
        if getattr(self.target, method.func_name, None) is None:
            # regular patching without origin
            setattr(self.target, method.func_name, method)
        else:
            self.target._patch_method(method.func_name, method)
        # return original monkeypatch unchanged:
        return method


# by LeoRochael - torna assíncrona computação de campos related store=True
# de acordo com delay_map - usado por stock_pycking.py em ybp_overrides
@patch_into(models.BaseModel)
@contextlib.contextmanager
def delay_store_compute(self, delay_map):
    """
    Example of use:

    STOCK_PICKING_DELAY_MAP = {
        'stock.picking': [
            'group_id', 'state', 'max_date', 'priority',
            'min_date', 'weight', 'weight_net',
            'invoice_state',
        ],
        'account.invoice': [
            'amount_total_taxes',
            'ii_value', 'icms_base', 'amount_wh', 'residual',
            'amount_untaxed', 'issqn_value_wh',
        ],
    }


    # by LeoRochael - otimizações de performance para stock picking
    class StockPicking(models.Model):
        _inherit = 'stock.picking'

        # vide ybp_serialize_barcode_scan
        @api.multi
        def do_recompute_remaining_quantities(self):
            if not self.env.context.get('skip_do_recompute_remaining_quantities'):
                super(StockPicking, self).do_recompute_remaining_quantities()

        # torna assíncrono cálculo de campos obrigatórios no ato da reserva
        @api.multi
        def action_assign(self):
            with self.delay_store_compute(STOCK_PICKING_DELAY_MAP) as self:
                return super(StockPicking, self).action_assign()

        # torna assíncrono cálculo de campos obrigatórios também no cancelamento
        @api.multi
        def action_cancel(self):
            with self.delay_store_compute(STOCK_PICKING_DELAY_MAP) as self:
                return super(StockPicking, self).action_cancel()

    

    """
    old_context = self.env.context
    if MAP_KEY in old_context:
        raise NotImplementedError("Don't know how to stack recompute delays")
    delayed_model_field_map = {
        model_name: set(fields)
        for model_name, fields in delay_map.items()
    }
    context_update = {
        # Pauses the recomputation of old-style store function fields:
        MAP_KEY: delayed_model_field_map,
        # Stores the paused old-style fields recomputations to be done later:
        DELAYED_KEY: [],
        # Stores the paused new-style fields recomputations to be done later:
        DELAYED_TODO_KEY: {},
    }

    self = self.with_context(**context_update)
    env = self.env
    context = env.context

    _log.debug("Delaying recompute:\n%s", pprint.pformat(context[MAP_KEY]))

    yield self

    _log.debug("Recomputing the delayed:\n%s",
               pprint.pformat(context[DELAYED_KEY]))
    # the next block of lines adapted from inside BaseModel._write()
    done = {}
    env.recompute_old.extend(context[DELAYED_KEY])
    while env.recompute_old:
        sorted_recompute_old = sorted(env.recompute_old)
        env.clear_recompute_old()
        for __, model_name, ids_to_update, fields_to_recompute in \
                sorted_recompute_old:
            key = (model_name, tuple(fields_to_recompute))
            todo_model = env[model_name]
            # avoid to do several times the same computation
            done.setdefault(key, todo_model)
            todo = (todo_model.browse(ids_to_update) - done[key]).exists()
            if todo:
                done[key] |= todo
                todo._store_set_values(fields_to_recompute)

    # recompute delayed new-style fields
    for field in list(context[DELAYED_TODO_KEY]):
        recs_list = context[DELAYED_TODO_KEY].pop(field)
        for recs in recs_list:
            env.add_todo(field, recs)
    recompute.origin(self)


def _separate_delayed_fields(context, model, fields):
    """
    Separate the fields that should be done now from the ones to be done later
    """
    now = []
    later = []
    delayed_fields = context.get(MAP_KEY, {}).get(model, set())
    # Not using set() operations to preserve field order. Is it necessary?
    for field in fields:
        if field in delayed_fields:
            later.append(field)
        else:
            now.append(field)
    return (now, later)


@patch_into(models.BaseModel)
def _store_get_values(self, cr, uid, ids, fields, context):
    result = []

    # collect the original values
    values = _store_get_values.origin(
        self, cr, uid, ids, fields, context,
    )
    for priority, store_model, store_ids, store_fields in values:
        now_fields, later_fields = _separate_delayed_fields(
            context, store_model, store_fields,
        )
        # return the non-delayed now and save the delayed in context for later
        if now_fields:
            _log.debug("_store_get_values(): %r not delaying:%s",
                       store_model, now_fields)
            result.append((priority, store_model, store_ids, now_fields))
        if later_fields:
            delayed = (priority, store_model, store_ids, later_fields)
            _log.debug("_store_get_values(): %r delaying:%s",
                       store_model, delayed)
            context[DELAYED_KEY].append(delayed)
    return result


@patch_into(models.BaseModel)
def recompute(self):
    context = self.env.context
    delay_map = context.get(MAP_KEY, {})
    todo = self.env.all.todo

    delay_fields = {
        field for field in todo
        if field.name in delay_map.get(field.model_name, ())
    }

    for field in list(delay_fields):
        # Also delay all fields sharing the same compute methods as these.
        # No need to recurse.
        delay_fields.update(field.computed_fields)

    field_delay_map = {}
    for field in delay_fields:
        recs_list = todo.pop(field, None)
        if recs_list is not None:
            field_delay_map[field] = recs_list

    if field_delay_map:
        _log.debug("%s delaying: %s", recs_list, field.name)

    for field, recs_list in field_delay_map.items():
        context[DELAYED_TODO_KEY].setdefault(field, []).extend(recs_list)

    if todo:
        _log.debug('Not delaying recompute of:\n%s', pprint.pformat(todo))

    recompute.origin(self)
