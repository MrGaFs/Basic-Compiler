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
				self.advance()
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
				return [], Error('Invalid character')
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


# Error

class Error:
	def __init__(self, message):
		self.message = message

	def __str__(self):
		return f'Error: {self.message}'


def runner(text):
	lexer = Lexer(text)
	tokens, error = lexer.tokenizer()
	if error:
		return None, error
	return tokens, None
