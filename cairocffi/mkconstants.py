import re
import pycparser


def parse_constant(node):
    if isinstance(node, pycparser.c_ast.Constant):
        return node.value

    if isinstance(node, pycparser.c_ast.UnaryOp) and node.op == '-':
        return '-' + parse_constant(node.expr)


class Visitor(pycparser.c_ast.NodeVisitor):
    def visit_EnumeratorList(self, node):
        value = 0
        for enumerator in node.enumerators:
            if enumerator.value is not None:
                value_string = parse_constant(enumerator.value)
                value = int(value_string, 0)
            else:
                value_string = str(value)
            assert enumerator.name.startswith('CAIRO_')
            print('%s = %s' % (enumerator.name[6:], value_string))
            value += 1
        print('')


def generate(include_dir):
    # Remove comments, preprocessor instructions and macros.
    source = re.sub(
        b'/\*.*?\*/'
        b'|CAIRO_(BEGIN|END)_DECLS'
        b'|cairo_public '
        br'|^\s*#.*?[^\\]\n',
        b'',
        b''.join(open('%s/cairo%s.h' % (include_dir, suffix), 'rb').read()
                 for suffix in ['', '-pdf', '-ps', '-svg']),
        flags=re.DOTALL | re.MULTILINE)
    print('# Generated by mkconstants.py\n')
    Visitor().visit(pycparser.CParser().parse(source))
    print('_CAIRO_HEADERS = r"""\n%s\n"""' % source.strip())


if __name__ == '__main__':
    generate('/usr/include/cairo')
