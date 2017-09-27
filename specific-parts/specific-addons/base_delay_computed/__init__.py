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
DELAYED_KEY = 'store_set_list'


class patch_into(object):
    """
    Decorate method to monkey-patch into a class
    """

    def __init__(self, target):
        self.target = target

    def __call__(self, method):
        _log.debug("patching %s into %s", method.func_name, self.target)
        if getattr(self.target, method.func_name, None) is None:
            # regular patching without origin
            setattr(self.target, method.func_name, method)
        else:
            self.target._patch_method(method.func_name, method)
        # return original monkeypatch unchanged:
        return method


@patch_into(models.BaseModel)
@contextlib.contextmanager
def delay_store_compute(self, delay_map):
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
        # The key below pauses recomputation of ALL new-style fields.
        # There is no way to filter only some fields.
        # 'recompute': False,  # disable new style field recompute
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

    # # recompute paused new-style fields if 'recompute': False in new context
    # # above:
    # if old_context.get('recompute', True) and env.recompute:
    #     # self here doesn't matter, `recompute()` should have been a method
    #     # on `self.env` instead:
    #     self.recompute()


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
            _log.debug("Not delaying:%s", now_fields)
            result.append((priority, store_model, store_ids, now_fields))
        if later_fields:
            delayed = (priority, store_model, store_ids, later_fields)
            _log.debug("Delaying:%s", delayed)
            context[DELAYED_KEY].append(delayed)
    return result
