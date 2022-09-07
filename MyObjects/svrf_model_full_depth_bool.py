import re
from MyObjects.tree_model import buildParseTree


def get_leaf_nodes(node, leafs):
    # print(node)
    if node:

        child = [node.getLeftChild(), node.getRightChild()]

        if child.count(None) == 2:
            leafs.append(node)
            # print(leafs)
        for n in child:
            # print(n)
            get_leaf_nodes(n, leafs)


def print_tree(node, level=0, name=None):
    if node:
        print_tree(node.getLeftChild(), level + 1, name)
        if level == 0:
            print(name + ' ' + ' ' * 4 * level + '-> ' + node.getRootVal())

        else:
            print(' ' * (len(name) + 2) + ' ' * 4 * level + '-> ' + node.getRootVal())

        print_tree(node.getRightChild(), level + 1, name)


def write_tree_in_list(node, line_list, level=0, name=None):
    """
    Preorder traversal to build HTML Tree
    """
    if node:
        line_list.append(f"<div class=level>")
        if level == 0:
            line_list.append("" + node.getRootVal() + "")
        else:
            line_list.append("" + node.getRootVal() + "")
        write_tree_in_list(node.getLeftChild(), line_list, level + 1, name)
        write_tree_in_list(node.getRightChild(), line_list, level + 1, name)
        line_list.append("</div>")


class SVRF:

    def __init__(self, name='', path='./'):
        self.path = path
        self.name = name
        self.lines = None
        self.commented_lines = None
        self.code_lines = None
        self.bool_ops_set = {'AND', 'OR', 'NOT', 'NOR', 'NOR', 'XOR'}
        self.var_dict = {}
        self.big_bool_tree = None

    def update_svrf(self):
        self.update_lines()

    def set_path(self, new_path):
        self.path = new_path
        self.update_lines()

    def update_lines(self):
        with open(self.path + self.name) as f:
            self.lines = [line.rstrip() for line in f]
        self.comment_lines()
        self.build_var_dict()

    def comment_lines(self):
        line_list = self.lines
        inline_comments = []
        block_comments = []
        c_start_flag = False
        c_start = None
        for i, line in enumerate(line_list):
            if c_start_flag:
                if line.endswith('*/'):
                    c_end = i
                    block_comments.append([c_start, c_end])
                    c_start_flag = False
                else:
                    pass
            elif line.startswith('//'):
                inline_comments.append(i)
            elif line.startswith('/*'):
                c_start = i
                c_start_flag = True
        flatten_bock = []
        for i in block_comments:
            flatten_bock.extend(list(range(i[0], i[1] + 1)))
        inline_comments.extend(flatten_bock)
        inline_comments.sort()
        self.commented_lines = inline_comments
        self.code_lines = list(set(range(len(line_list))) - set(self.commented_lines))

    def build_var_dict(self):
        self.var_dict = {}
        for idx, line in enumerate(self.code_lines):
            x = re.search('=', self.lines[line])
            if x:  # the line contains assignment operator
                # first item is variable
                # remove whitespace from the variable name
                # second item is expression
                # remove comment at end of line, if any
                # strip white space at either ends
                # split expression at spaces
                variable = x.string[0:x.span()[0]].strip()
                raw_expr = x.string[x.span()[1]:].split('//')[0].strip()
                self.var_dict[variable] = {'line_no': self.code_lines[idx],
                                           'expression_raw': raw_expr,
                                           'expression_list': raw_expr.split()}
                # gather variables in the expression
                expr = {i.strip('(').strip(')') for i in self.var_dict[variable]['expression_list']}
                bool_intersection = self.bool_ops_set & expr  # intersection with boolean operators
                var_intersection = set(self.var_dict.keys()) & expr  # intersection with existing variables
                is_bool = len(bool_intersection) > 0 or len(var_intersection) > 0
                self.var_dict[variable]['is_bool'] = is_bool

    def build_bool_tree(self):
        pass
        # operator_list = ['+', '-', '*', '/', 'INSIDE', 'OR', 'or', 'NOT', 'AND', 'SIZE', 'BY', 'INTERACT',
        #                  'NOT-INTERACT','INSIDE','NOT-INSIDE','INTERNAL','EXPAND-EDGE','LESS-THAN']
        # var_dict = self.var_dict
        # for var_name, var_expr in var_dict.items():
        #     if var_expr['is_bool']:
        #         expression = var_expr['expression_raw']
        #         expr_spaced = re.sub(r'\)', " ) ", re.sub(r'\(', " ( ", expression))
        #         expr_spaced = expr_spaced.replace('BY', '')
        #         print(expr_spaced)
        #
        #         if expr_spaced.startswith('CMACRO'):
        #             expr_split = expr_spaced.split()
        #             expr_split.remove('CMACRO')
        #             expr_split[1], expr_split[0] = expr_split[0], expr_split[1]
        #             macro_name = expr_split[1]
        #             expr_spaced = ' '.join(expr_split[0:3])
        #             operator_list.append(macro_name)
        #         if expr_spaced.startswith('DEANGLE'):
        #             expr_split = expr_spaced.split()
        #             expr_split[1], expr_split[0] = expr_split[0], expr_split[1]
        #             macro_name = expr_split[1]
        #             expr_spaced = ' '.join(expr_split[0:3])
        #             operator_list.append(macro_name)
        #         if expr_spaced.startswith('OPCBIAS'):
        #             expr_split = expr_spaced.split()
        #             expr_split[1], expr_split[0] = expr_split[0], expr_split[1]
        #             macro_name = expr_split[1]
        #             expr_spaced = ' '.join(expr_split[0:3])
        #             operator_list.append(macro_name)
        #         if expr_spaced.find('WITH') != -1:
        #             expr_split = expr_spaced.split()
        #             print(expr_split)
        #             expr_split.remove('WITH')
        #             macro_name = expr_split[1]
        #             expr_spaced = expr_split[0] + ' ' + expr_split[1] + ' ' + ''.join(expr_split[2:])
        #             operator_list.append(macro_name)
        #         if expr_spaced.find('NOT INTERACT') != -1:
        #             expr_spaced = re.sub(r'NOT INTERACT', "NOT-INTERACT", expr_spaced)
        #         if expr_spaced.startswith('COPY'):
        #             expr_spaced = '_ ' + expr_spaced
        #             operator_list.append('COPY')
        #
        #         expr_spaced = '( ' + expr_spaced + ' )'
        #         # print((expr_spaced, operator_list))
        #         pt = buildParseTree(expr_spaced, operator_list)
        #         self.var_dict[var_name]['expression_tree'] = pt

    def build_single_bool_tree(self):
        operator_list = ['+', '-', '*', '/', 'INSIDE', 'OR', 'or', 'NOT', 'AND', 'SIZE', 'BY', 'INTERACT',
                         'NOT-INTERACT','INSIDE','NOT-INSIDE','INTERNAL','EXPAND-EDGE','LESS-THAN']
        var_dict = self.var_dict
        for var_name, var_expr in var_dict.items():
            if var_expr['is_bool']:
                expression = var_expr['expression_raw']
                expr_spaced = re.sub(r'\)', " ) ", re.sub(r'\(', " ( ", expression))
                expr_spaced = expr_spaced.replace('BY', '')

                if expr_spaced.startswith('CMACRO'):
                    expr_split = expr_spaced.split()
                    expr_split.remove('CMACRO')
                    expr_split[1], expr_split[0] = expr_split[0], expr_split[1]
                    macro_name = expr_split[1]
                    expr_spaced = ' '.join(expr_split[0:3])
                    operator_list.append(macro_name)

                if expr_spaced.startswith('DEANGLE'):
                    expr_split = expr_spaced.split()
                    expr_split[1], expr_split[0] = expr_split[0], expr_split[1]
                    macro_name = expr_split[1]
                    expr_spaced = ' '.join(expr_split[0:3])
                    operator_list.append(macro_name)

                if expr_spaced.startswith('OPCBIAS'):
                    expr_split = expr_spaced.split()
                    expr_split[1], expr_split[0] = expr_split[0], expr_split[1]
                    macro_name = expr_split[1]
                    expr_spaced = ' '.join(expr_split[0:3])
                    operator_list.append(macro_name)

                if expr_spaced.find('WITH') != -1:
                    expr_split = expr_spaced.split()
                    print(expr_split)
                    expr_split.remove('WITH')
                    macro_name = expr_split[1]
                    expr_spaced = expr_split[0] + ' ' + expr_split[1] + ' ' + ''.join(expr_split[2:])
                    operator_list.append(macro_name)

                if expr_spaced.find('NOT INTERACT') != -1:
                    expr_spaced = re.sub(r'NOT INTERACT', "NOT-INTERACT", expr_spaced)

                if expr_spaced.startswith('COPY'):
                    expr_spaced = '_ ' + expr_spaced
                    operator_list.append('COPY')

                var_dict[var_name]['expression_raw'] = expr_spaced
                # print(var_dict[var_name]['expression_raw'])

        big_expr_dict = {}
        for var_name, var_expr in var_dict.items():
            # print("-------------expression---------------")
            # print(expression)
            if var_expr['is_bool']:
                expression = var_expr['expression_raw']
                for key in reversed(var_dict.keys()):
                    # expression = expression.replace(key, )
                    replaced_expr = var_dict[key]['expression_raw']
                    if var_dict[key]['is_bool']:
                        replaced_expr = var_dict[key]['expression_raw']
                    else:
                        replaced_expr = key
                    expression = re.sub(rf"\b{key}\b", ' ( ' + replaced_expr + ' ) ', expression)
            big_expr_dict[var_name] = ' ( ' + expression + ' ) '

        for var_name, var_expr in big_expr_dict.items():
            print('=' * 20)
            print(var_name, var_expr)
            expr_spaced = var_expr
            print('-------------HERE---------------')
            print(expr_spaced, operator_list)
            print('-------------END---------------')
            pt = buildParseTree(expr_spaced, operator_list)
            self.var_dict[var_name]['expression_tree_big'] = pt
            # print_tree(pt, name=var_name)

    def print_bool_ops(self):
        var_dict = self.var_dict
        for var_name, var_expr in var_dict.items():
            if var_expr['is_bool']:
                msg = '  Line ' + str(var_expr['line_no']) + ': ' + str(var_name) + '   '
                buffer_space = round((40 - len(msg)) / 2)
                print('=' * 40)
                print('=' * buffer_space + msg + '=' * buffer_space)
                print('.' * 40)
                print_tree(var_expr['expression_tree_big'], name=var_name)

    def get_leafs(self, tree):
        leafs = []
        get_leaf_nodes(tree, leafs)
        return leafs

    def build_leaf_list(self):
        var_dict = self.var_dict
        for var_name, var_expr in var_dict.items():
            if var_expr['is_bool']:
                leafs = self.get_leafs(var_expr['expression_tree'])
                self.var_dict[var_name]['tree_leafs'] = leafs

    def write_bool_to_list(self):
        var_dict = self.var_dict
        line_list = ["<body class=level_0>"]
        for var_name, var_expr in var_dict.items():
            if var_expr['is_bool']:
                msg = "<div class=level> " + str(var_name) + ""
                line_list.append(msg)
                print(msg)
                write_tree_in_list(var_expr['expression_tree_big'], line_list, name=var_name)
                line_list.append("</div>")
        line_list.append("</body>")

        return line_list

