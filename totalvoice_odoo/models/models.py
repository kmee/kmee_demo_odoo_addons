# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID



old_read_group_fill_results = models.BaseModel._read_group_fill_results

models.BaseModel._old_read_group_fill_results = \
    old_read_group_fill_results

def _read_group_fill_results(self, domain, groupby, remaining_groupbys,
                             aggregated_fields, count_field,
                             read_group_result, read_group_order=None):
    """Helper method for filling in empty groups for all possible values of
   the field being grouped by"""

    if not self._name == 'totalvoice.base' or groupby not in \
            self._group_by_full.keys():

        return self._old_read_group_fill_results(
            domain, groupby, remaining_groupbys, aggregated_fields,
            count_field, read_group_result,
            read_group_order=read_group_order)

    present_group_ids = \
        [x[groupby] for x in read_group_result if x[groupby]]

    all_groups, folded = self._group_by_full[groupby](
        self, present_group_ids, domain,
        read_group_order=read_group_order,
        access_rights_uid=SUPERUSER_ID
    )

    all_group_tuples = {k: (k, v) for k, v in all_groups}

    result_template = dict.fromkeys(aggregated_fields, False)
    result_template[groupby + '_count'] = False
    if remaining_groupbys:
        result_template['__context'] = {'group_by': remaining_groupbys}

    result = []
    known_values = {}

    def append_left(left_side):
        grouped_value = left_side[groupby] and left_side[groupby][0]
        if grouped_value not in known_values:
            result.append(left_side)
            known_values[grouped_value] = left_side
        else:
            known_values[grouped_value].update(
                {count_field: left_side[count_field]})

    def append_right(right_side):
        grouped_value = right_side[0]
        if grouped_value not in known_values:
            line = dict(result_template)
            line[groupby] = right_side
            line['__domain'] = [(groupby, '=', grouped_value)] + domain
            result.append(line)
            known_values[grouped_value] = line

    while read_group_result or all_groups:
        left_side = read_group_result[0] if read_group_result else None
        right_side = all_groups[0] if all_groups else None

        if left_side and not isinstance(left_side[groupby],
                                        (tuple, list)):
            if left_side[groupby] and \
                    all_group_tuples[left_side[groupby]]:
                left_side[groupby] = all_group_tuples[left_side[groupby]]

        assert left_side is None or left_side[groupby] is False \
               or isinstance(left_side[groupby], (tuple, list)), \
            'M2O-like pair expected, got %r' % left_side[groupby]
        assert right_side is None or isinstance(right_side,
                                                (tuple, list)), \
            'M2O-like pair expected, got %r' % right_side
        if left_side is None:
            append_right(all_groups.pop(0))
        elif right_side is None:
            append_left(read_group_result.pop(0))
        elif left_side[groupby] == right_side:
            append_left(read_group_result.pop(0))
            # discard right_side
            all_groups.pop(0)
        elif not left_side[groupby] or not left_side[groupby][0]:
            # left side == "Undefined" entry, not present on right_side
            append_left(read_group_result.pop(0))
        else:
            append_right(all_groups.pop(0))

    if folded:
        for r in result:
            r['__fold'] = folded.get(r[groupby] and r[groupby][0], False)

    return result

def _append_all(self, cr, uid, read_group_result, all_groups,
                all_group_tuples,
                groupby, result_template, domain, count_field):

    result = []
    known_values = {}

    while read_group_result or all_groups:
        left_side = read_group_result[0] if read_group_result else None
        right_side = all_groups[0] if all_groups else None

        if left_side and not isinstance(left_side[groupby],
                                        (tuple, list)):
            if left_side[groupby] \
                    and all_group_tuples[left_side[groupby]]:
                left_side[groupby] = all_group_tuples[left_side[groupby]]

        assert left_side is None or left_side[groupby] is False \
               or isinstance(left_side[groupby], (tuple, list)), \
            'M2O-like pair expected, got %r' % left_side[groupby]
        assert right_side is None or isinstance(right_side,
                                                (tuple, list)), \
            'M2O-like pair expected, got %r' % right_side

        if left_side is None:
            result, known_values = self._append_right(
                all_groups.pop(0), groupby, known_values, result,
                result_template, domain)
        elif right_side is None:
            result, known_values = self._append_left(
                read_group_result.pop(0), groupby, known_values, result,
                count_field)
        elif left_side[groupby] == right_side:
            result, known_values = self._append_left(
                read_group_result.pop(0), groupby, known_values, result,
                count_field)
            # discard right_side
            all_groups.pop(0)
        elif not left_side[groupby] or not left_side[groupby][0]:
            # left side == "Undefined" entry, not present on right_side
            result, known_values = self._append_left(
                read_group_result.pop(0), groupby, known_values, result,
                count_field)
        else:
            result, known_values = self._append_right(
                all_groups.pop(0), groupby, known_values, result,
                result_template, domain)

    return result

def _append_left(left_side, groupby, known_values, result, count_field):

    grouped_value = left_side[groupby] and left_side[groupby][0]
    if grouped_value not in known_values:
        result.append(left_side)
        known_values[grouped_value] = left_side
    else:
        known_values[grouped_value].update(
            {count_field: left_side[count_field]})

    return result, known_values

def _append_right(right_side, groupby, known_values, result,
                  result_template,
                  domain):

    grouped_value = right_side[0]
    if grouped_value not in known_values:
        line = dict(result_template)
        line[groupby] = right_side
        line['__domain'] = [(groupby, '=', grouped_value)] + domain
        result.append(line)
        known_values[grouped_value] = line

    return result, known_values


models.BaseModel._append_all = _append_all
models.BaseModel._append_right = _append_right
models.BaseModel._append_left = _append_left

models.BaseModel._read_group_fill_results = \
    _read_group_fill_results