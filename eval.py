# coding: utf-8
# 参考文章 https://zhuanlan.zhihu.com/p/33820915


OPERATOR, INT, DOUBLE = 'OPERATOR', 'INT', 'DOUBLE'

operator_list = {
    '+': 0, '-': 0, '*': 0, '/': 0, '%': 0,
    '&': 0, '|': 0, '^': 0, '**': 0, '<': 0, '>': 0, '(': 0, ')': 0, '~': 0
}


class Token(object):
    def __init__(self, value, tag):
        self.value = value if value else ''
        self.tag = tag if value else INT

    def __str__(self):
        return 'token' + ' value :' + self.value + ' tag ' + self.tag


class Reader(object):
    def __init__(self, input_data):
        self.seq = input_data
        self.cursor = 0
        self.max_index = len(input_data) - 1
        self.min_index = 0
        # 假设不能从负

    def next(self):
        value = self.seq[self.cursor]
        self.cursor = self.cursor + 1
        return value

    def cursor_data(self):
        return self.seq[self.cursor]

    def has_next(self):
        return self.cursor <= self.max_index

    def peek(self):
        if self.cursor + 1 > self.max_index:
            raise IndexError()
        return self.seq[self.cursor + 1]

    def last_value(self):
        if self.cursor - 2 < self.min_index:
            raise IndexError('index must more than zero')
        return self.seq[self.cursor - 2]


class Lexer(object):
    def __init__(self, input_expression):
        self.Reader = Reader(input_expression)

    def read_num(self):
        ans = ['', INT]
        reader = self.Reader
        while reader.has_next() \
                and (self.is_digit(reader.cursor_data()) or reader.cursor_data() == '.'
                     or self.is_escape(reader.cursor_data())):
            # 一直读取数
            cur_value = self.Reader.next()
            if self.is_escape(cur_value):
                continue
            ans[0] = ans[0] + cur_value

        if reader.has_next() and reader.cursor_data() == 'e' and \
                (reader.peek() == '+' or reader.peek() == '-'):
            # 检查是否存在计数法
            ans[0] = ans[0] + reader.next() + reader.next()
            while reader.has_next() and self.is_digit(reader.cursor_data()):
                ans[0] = ans[0] + reader.next()

        if ans[0].find('.') != -1 or ans[0].find('e-') != -1:
            ans[1] = DOUBLE
        return ans

    def parse(self):
        token_list = []
        reader = self.Reader
        while reader.has_next():
            cur_value = reader.next()
            if self.is_escape(cur_value):
                continue
            if self.is_digit(cur_value):
                ret = self.read_num()
                token_list.append(Token(cur_value + ret[0], ret[1]))
            elif cur_value in operator_list:
                # TODO: 如何处理－和位运算
                if (cur_value == '*' or cur_value == '>' or cur_value == '<') \
                        and cur_value == reader.cursor_data():
                    cur_value = cur_value + reader.next()
                    token_list.append(Token(cur_value, OPERATOR))
                elif cur_value == '~':
                    ret = self.read_num()
                    token_list.append(Token(cur_value + ret[0], INT))
                elif cur_value == '-':
                    last_value = reader.last_value()
                    if last_value in operator_list:
                        ret = self.read_num()
                        token_list.append(Token(cur_value + ret[0], INT))
                    else:
                        token_list.append(Token(cur_value, OPERATOR))
                else:
                    token_list.append(Token(cur_value, OPERATOR))
        return token_list

    @staticmethod
    def is_digit(char):
        return '0' <= char <= '9'

    @staticmethod
    def is_escape(char):
        return char == ' ' or char == '\n' or char == '\t'


class NumberNode(object):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value

    def __str__(self):
        return str(self.value)


class OperatorNode(object):
    def __init__(self, op, le, re):
        self.op = op
        self.le = le
        self.re = re

    def __str__(self):
        return 'OperatorNode {' + 'op: ' + str(self.op) + 'le： ' + str(self.le) + 're: ' + str(self.re) + '}'

    def eval(self):
        result = 0
        if self.op == '+':
            result = self.le.eval() + self.re.eval()
        elif self.op == '-':
            result = self.le.eval() - self.re.eval()
        elif self.op == '*':
            result = self.le.eval() * self.re.eval()
        elif self.op == '/':
            result = self.le.eval() / self.re.eval()
        elif self.op == '%':
            result = self.le.eval() % self.re.eval()
        elif self.op == '**':
            result = self.le.eval() ** self.re.eval()
        elif self.op == '<<':
            result = self.le.eval() << self.re.eval()
        elif self.op == '>>':
            result = self.le.eval() >> self.re.eval()
        elif self.op == '&':
            result = self.le.eval() & self.re.eval()
        elif self.op == '|':
            result = self.le.eval() | self.re.eval()
        elif self.op == '^':
            result = self.le.eval() ^ self.re.eval()
        return result


class ExpressionTreeConstructor(object):
    def __init__(self, tokenlist):
        self.reader = Reader(tokenlist)
        self.operator = []
        self.num = []

    def get_op_top(self):
        return self.operator[len(self.operator)-1]

    def build_tree(self):
        while self.reader.has_next():
            cur_value = self.reader.next()
            if cur_value.tag == INT:
                if cur_value.value.startswith('~'):
                    self.num.append(NumberNode(~int(cur_value.value[1])))
                else:
                    self.num.append(NumberNode(int(cur_value.value)))
            elif cur_value.tag == DOUBLE:
                self.num.append(NumberNode(float(cur_value.value)))
                # 浮点数没有取反
                # 将数放入数栈
            else:
                # 操作符
                # 运算符高的可以先执行所以就先执行运算符低的addNode() 表示后运算
                # python 运算符优先级　https://docs.python.org/3/reference/expressions.html#operator-precedenc
                # 如何建树　将优先级低的放到最后运算,将优先级高的作为一个表达式节点然后递归运算
                if cur_value.value == '(':
                    self.operator.append(cur_value.value)
                elif cur_value.value == ')':
                    # 需要弹出
                    while len(self.operator) and self.get_op_top() != '(':
                        self.add_node()
                    self.operator.pop()
                elif cur_value.value == '**':
                    while len(self.operator) and self.get_op_top() == cur_value.value:
                        self.add_node()
                    self.operator.append(cur_value.value)
                elif cur_value.value in ['*', '/', '%']:
                    while len(self.operator) and self.get_op_top() in ['*', '/', '%']:
                        self.add_node()
                    self.operator.append(cur_value.value)
                elif cur_value.value in ['+', '-']:
                    while len(self.operator) and self.get_op_top() not in ['(', '|', '&', '^']:
                        self.add_node()
                    self.operator.append(cur_value.value)
                elif cur_value.value in ['|', '&', '^', '<<', '>>']:
                    while len(self.operator) and self.get_op_top() != '(':
                        self.add_node()
                    self.operator.append(cur_value.value)

        while len(self.operator):
            self.add_node()
        return self.num[0]

    def add_node(self):
        # 构建表达式　　1+2
        re = self.num.pop()  # 先弹出的是作用的数 2
        le = self.num.pop() if len(self.num) else NumberNode(0)  # 被作用的数 1
        op = self.operator.pop()  # +
        self.num.append(OperatorNode(op, le, re))


if __name__ == '__main__':
    from sys import argv
    print(ExpressionTreeConstructor(Lexer(argv[1]).parse()).build_tree().eval(), sep='\n')
