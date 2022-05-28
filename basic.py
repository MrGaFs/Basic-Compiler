# CONSTANT

DIGITS = '0123456789'


# TOKENS

TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_EOF = 'EOF'


class Token:
	def __init__(self, type_, value=None):
		self.type = type_
		self.value = value

	def __repr__(self):
		return f'{self.type}:{self.value}' if self.value else f'{self.type}'

# Lexer


class Lexer:
	def __init__(self, text):
		self.text = text
		self.pos = -1
		self.cur_char = None

	def advance(self):
		self.pos += 1
		self.cur_char = self.text[self.pos] if self.pos < len(self.text) else None

	def tokenizer(self):
		tokens = []
		self.advance()
		while self.cur_char is not None:
			if self.cur_char in ' \t':
				self.advance()
			elif self.cur_char in DIGITS:
				tokens.append(self.make_number())
			elif self.cur_char == '+':
				tokens.append(Token(TT_PLUS))
				self.advance()
			elif self.cur_char == '-':
				tokens.append(Token(TT_MINUS))
				self.advance()
			elif self.cur_char == '*':
				tokens.append(Token(TT_MUL))
				self.advance()
			elif self.cur_char == '/':
				tokens.append(Token(TT_DIV))
				self.advance()
			elif self.cur_char == '(':
				tokens.append(Token(TT_LPAREN))
				self.advance()
			elif self.cur_char == ')':
				tokens.append(Token(TT_RPAREN))
				self.advance()
			else:
				char = self.cur_char
				self.advance()
				return [], Error(f'Invalid Character {char}')
		tokens.append(Token(TT_EOF))
		return tokens, None

	def make_number(self):
		num = ''
		dot_count = 0
		while self.cur_char is not None and self.cur_char in DIGITS + '.':
			if self.cur_char == '.':
				if dot_count == 1:
					break
				dot_count += 1
			num += self.cur_char
			self.advance()
		return Token(TT_INT, int(num)) if dot_count == 0 else Token(TT_FLOAT, float(num))


# ===============================================================================
# Node
# ===============================================================================

class NumberNode:
	def __init__(self, token):
		self.token = token

	def __repr__(self):
		return f'{self.token}'


class BinOpNode:
	def __init__(self, left_node, op_token, right_node):
		self.left_node = left_node
		self.op_token = op_token
		self.right_node = right_node

	def __repr__(self):
		return f'({self.left_node}, {self.op_token}, {self.right_node})'


class UnaryOpNode:
	def __init__(self, op_token, node):
		self.op_token = op_token
		self.node = node

	def __repr__(self):
		return f'({self.op_token}, {self.node})'

# =============================================
# ParseResult
# =============================================


class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None

	def register(self, res):
		if isinstance(res, ParseResult):
			if res.error:
				self.error = res.error
			return res.node

		return res

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		self.error = error
		return self

# =============================================
# Parser
# =============================================


class Parser:
	def __init__(self, token):
		self.token = token
		self.token_idx = -1
		self.cur_token = None
		self.advance()

	def parse(self):
		res = self.expr()
		if not res.error and self.cur_token.type != TT_EOF:
			return res.failure(Error('Invalid Syntax'))
		return res

	def advance(self):
		self.token_idx += 1
		if self.token_idx < len(self.token):
			self.cur_token = self.token[self.token_idx]
		return self.cur_token

	def factor(self):
		res = ParseResult()
		tok = self.cur_token
		if tok.type in (TT_PLUS, TT_MINUS):
			res.register(self.advance())
			factor = res.register(self.factor())
			if res.error:
				return res
			return res.success(UnaryOpNode(tok, factor))
		elif tok.type in (TT_INT, TT_FLOAT):
			res.register(self.advance())
			return res.success(NumberNode(tok))
		elif tok.type == TT_LPAREN:
			res.register(self.advance())
			expr = res.register(self.expr())
			if res.error:
				return res
			if self.cur_token.type == TT_RPAREN:
				res.register(self.advance())
				return res.success(expr)
			else:
				return res.failure(Error('Invalid Syntax'))

		return res.failure(Error('Invalid Syntax'))

	def term(self):
		return self.bin_op(self.factor, (TT_MUL, TT_DIV))

	def expr(self):
		return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

	def bin_op(self, func, ops):
		res = ParseResult()
		left = res.register(func())
		if res.error:
			return res

		while self.cur_token.type in ops:
			op_token = self.cur_token
			res.register(self.advance())
			right = res.register(func())
			if res.error:
				return res
			left = BinOpNode(left, op_token, right)

		return res.success(left)


# Error


class Error:
	def __init__(self, message):
		self.message = message

	def __str__(self):
		return f'Error: {self.message}'


class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		if res.error:
			self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self

# ==========================================
# VALUES
# ==========================================


class Number:
	def __init__(self, value):
		self.value = value
		self.set_context()
		self.context = None

	def set_context(self, context=None):
		self.context = context
		return self

	def added_to(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value).set_context(self.context), None

	def subbed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value).set_context(self.context), None

	def multed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value).set_context(self.context), None

	def dived_by(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, Error("Runtime Error divided by 0")

			return Number(self.value / other.value).set_context(self.context), None

	def __repr__(self):
		return str(self.value)

# ==========================================
# CONTEXT
# ==========================================


class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos

# ==========================================
# INTERPRETER
# ==========================================


class Interpreter:
	def visit(self, node, context):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.no_visit_method)
		return method(node, context)

	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	def visit_NumberNode(self, node, context):
		return RTResult().success(
			Number(node.token.value).set_context(context)
		)

	def visit_BinOpNode(self, node, context):
		res = RTResult()
		result = None
		left = res.register(self.visit(node.left_node, context))
		if res.error:
			return res
		right = res.register(self.visit(node.right_node, context))
		if res.error:
			return res

		if node.op_token.type == TT_PLUS:
			result, error = left.added_to(right)
		elif node.op_token.type == TT_MINUS:
			result, error = left.subbed_by(right)
		elif node.op_token.type == TT_MUL:
			result, error = left.multed_by(right)
		elif node.op_token.type == TT_DIV:
			result, error = left.dived_by(right)

		if res.error:
			return res.failure(res.error)
		else:
			return res.success(result)

	def visit_UnaryOpNode(self, node, context):
		res = RTResult()
		number = res.register(self.visit(node.node, context))
		if res.error:
			return res

		error = None

		if node.op_token.type == TT_MINUS:
			number, error = number.multed_by(Number(-1))

		if error:
			return res.failure(error)
		else:
			return res.success(number)


def runner(text):
	lexer = Lexer(text)
	tokens, error = lexer.tokenizer()
	if error:
		return None, error
	parser = Parser(tokens)
	tree = parser.parse()
	# Run program
	interpreter = Interpreter()
	context = Context('<program>')
	result = interpreter.visit(tree.node, context)
	return result.value, tree.error
