"""@package vipermonkey.core.var_in_expr_visitor Visitor for
collecting the names of variables referenced in expressions in a VBA
object.

"""

# pylint: disable=pointless-string-statement
"""
ViperMonkey: Visitor for collecting the names of variables
referenced in expressions.

ViperMonkey is a specialized engine to parse, analyze and interpret Microsoft
VBA macros (Visual Basic for Applications), mainly for malware analysis.

Author: Philippe Lagadec - http://www.decalage.info
License: BSD, see source code or documentation

Project Repository:
https://github.com/decalage2/ViperMonkey

"""

# === LICENSE ==================================================================

# ViperMonkey is copyright (c) 2015-2016 Philippe Lagadec (http://www.decalage.info)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from vipermonkey.core.visitor import visitor
from vipermonkey.core.utils import safe_str_convert

class var_in_expr_visitor(visitor):
    """Get the names of all variables (and function calls if desired) that
    appear in an expression. The discovered variables/functions are
    saved in the self.variables (set) field of the visitor.

    """

    def __init__(self, context=None, follow_calls=False, get_functions=False):
        self.variables = set()
        self.visited = set()
        self.context = context
        self.follow_calls = follow_calls
        self.get_functions = get_functions
        
    def visit(self, item):
        from vipermonkey.core.expressions import SimpleNameExpression
        from vipermonkey.core.expressions import MemberAccessExpression
        from vipermonkey.core.expressions import Function_Call
        from vipermonkey.core import procedures
        
        # Already looked at this?
        if (item in self.visited):
            return False
        self.visited.add(item)

        # Simple variable?
        if (isinstance(item, SimpleNameExpression)):
            self.variables.add(safe_str_convert(item.name))

        # Tracking all function calls?
        if (self.get_functions and isinstance(item, Function_Call)):
            self.variables.add(safe_str_convert(item.name))
        
        # Array access?
        if (("Function_Call" in safe_str_convert(type(item))) and (self.context is not None)):

            # Is this an array or function?
            if (hasattr(item, "name") and (self.context.contains(item.name))):

                # Array access?
                ref = self.context.get(item.name)
                if isinstance(ref, (list, str)):
                    self.variables.add(safe_str_convert(item.name))

                # Function call?
                if ((isinstance(ref, procedures.Function) or isinstance(ref, procedures.Sub)) and self.follow_calls):

                    # Get variables from the function body also.
                    ref.accept(self)                    

        # Member access expression used as a variable?
        if (isinstance(item, MemberAccessExpression)):
            rhs = item.rhs
            if (isinstance(rhs, list)):
                rhs = rhs[-1]
            if (isinstance(rhs, SimpleNameExpression)):
                self.variables.add(safe_str_convert(item))
                    
        return True
