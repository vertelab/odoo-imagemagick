# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2014-2017 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import odoo
from odoo.tools.safe_eval import _SAFE_OPCODES, test_expr, _import
from odoo.tools.misc import ustr
from opcode import opmap
from psycopg2 import OperationalError
from types import CodeType

import logging
_logger = logging.getLogger(__name__)

_SAFE_OPCODES.add(opmap['STORE_ATTR'])

def safe_eval(expr, globals_dict=None, locals_dict=None, mode="eval", nocopy=False, locals_builtins=False):
    """safe_eval(expression[, globals[, locals[, mode[, nocopy]]]]) -> result

    System-restricted Python expression evaluation

    Evaluates a string that contains an expression that mostly
    uses Python constants, arithmetic expressions and the
    objects directly provided in context.

    This can be used to e.g. evaluate
    an OpenERP domain expression from an untrusted source.

    :throws TypeError: If the expression provided is a code object
    :throws SyntaxError: If the expression provided is not valid Python
    :throws NameError: If the expression provided accesses forbidden names
    :throws ValueError: If the expression provided uses forbidden bytecode
    """
    if isinstance(expr, CodeType):
        raise TypeError("safe_eval does not allow direct evaluation of code objects.")

    if globals_dict is None:
        globals_dict = {}

    # prevent altering the globals/locals from within the sandbox
    # by taking a copy.
    if not nocopy:
        # isinstance() does not work below, we want *exactly* the dict class
        if (globals_dict is not None and type(globals_dict) is not dict) \
            or (locals_dict is not None and type(locals_dict) is not dict):
            _logger.warning(
                "Looks like you are trying to pass a dynamic environment, "
                "you should probably pass nocopy=True to safe_eval().")

        globals_dict = dict(globals_dict)
        if locals_dict is not None:
            locals_dict = dict(locals_dict)

    globals_dict.update(
        __builtins__={
            '__import__': _import,
            'True': True,
            'False': False,
            'None': None,
            'str': str,
            # ~ 'unicode': unicode,
            'bool': bool,
            'int': int,
            'float': float,
            # ~ 'long': long,
            'enumerate': enumerate,
            'dict': dict,
            'list': list,
            'tuple': tuple,
            'map': map,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            # ~ 'reduce': reduce,
            'filter': filter,
            'round': round,
            'len': len,
            'repr': repr,
            'set': set,
            'all': all,
            'any': any,
            'ord': ord,
            'chr': chr,
            'cmp': cmp,
            'divmod': divmod,
            'isinstance': isinstance,
            'range': range,
            'xrange': xrange,
            'zip': zip,
            'Exception': Exception,
        }
    )
    if locals_builtins:
        if locals_dict is None:
            locals_dict = {}
        locals_dict.update(globals_dict.get('__builtins__'))
    c = test_expr(expr, _SAFE_OPCODES, mode=mode)
    try:
        return eval(c, globals_dict, locals_dict)
    except odoo.osv.orm.except_orm:
        raise
    except odoo.exceptions.Warning:
        raise
    except odoo.exceptions.RedirectWarning:
        raise
    except odoo.exceptions.AccessDenied:
        raise
    except odoo.exceptions.AccessError:
        raise
    except OperationalError:
        # Do not hide PostgreSQL low-level exceptions, to let the auto-replay
        # of serialized transactions work its magic
        raise
    except Exception as e:
        import sys
        exc_info = sys.exc_info()
        raise ValueError('"%s" while evaluating\n%r' % (ustr(e), expr), exc_info[2])
