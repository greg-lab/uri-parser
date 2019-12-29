"""
URI parser created by Greg on 8th April 2019.
According to RFC 3986 (see: https://tools.ietf.org/html/rfc3986)
It is recommended to be a part of HTTP parser and therefore I assume that input URI does not have a scheme or host.

Expected input has a following format:

	/src/dict1/dict2/file?param1=value&param2=value#fragment

Usage example:

	my_parser = UriParser('/src/dict1/dict2/file?param1=value&param2=value#fragment')
	try:
		my_parser.parse()

		path = my_parser.get_path()          # '/src/dict1/dict2/file'
		fragment = my_parser.get_fragment()  # 'fragment'
		query = my_parser.get_query_params() # {'param1': 'value', 'param2': 'value'}

	except UriSyntaxError:
		print('Something went wrong')
	


"""

class UriSyntaxError(Exception):
	# Raised when URI is syntactically incorrect.
	pass

class UriParser:
	def __init__(self, uri_content):
		self._uri_content = uri_content
		self._path = ''
		self._fragment = ''
		self._query = ''
		self._query_params = {}
		self._iter = 0

		self._reserved_chars = (
			':',   '/',   '?',   '#',   '[',   ']',   '@',
			'!',   '$',   '&',   '\'',  '(',   ')',   '*',
			',',   ';',   '=',
		)

	def get_path(self):
		return self._path

	def get_fragment(self):
		return self._fragment

	def get_query_params(self):
		return self._query_params

	def parse(self):
		self._split_uri()
		self._parse_path()
		self._parse_fragment()
		self._parse_query()

	# Splits URI into three strings (path, query and format)
	def _split_uri(self):
		if self._uri_content.find('?') != -1:
			if self._uri_content.find('#') != -1:
				if self._uri_content.index('?') > self._uri_content.index('#'):
					raise UriSyntaxError

				tokens = self._uri_content.split('?', 1)
				self._path = tokens[0]
				self._query, self._fragment = tokens[1].split('#', 1)
			else:
				self._path, self._query = self._uri_content.split('?', 1)

		elif self._uri_content.find('#') != -1:
			self._path, self._fragment = self._uri_content.split('#', 1)
		else:
			self._path = self._uri_content

	# Checks charset and decodes percent-encoded characters.
	def _parse_path(self):
		self._iter = 0
		decoded_path = ''

		next_char = self._get_next_char(self._path)

		while next_char is not None:
			if next_char == '%':
				first_hex_digit = self._get_next_char(self._path)
				second_hex_digit = self._get_next_char(self._path)

				if first_hex_digit is None or second_hex_digit is None:
					raise UriSyntaxError

				decoded_path += self._decode(first_hex_digit + second_hex_digit)

			elif next_char in self._reserved_chars and next_char not in ('/', ':'):
				raise UriSyntaxError

			else:
				decoded_path += next_char

			next_char = self._get_next_char(self._path)

		self._path = decoded_path

	# Checks charset and decodes percent-encoded characters.
	def _parse_fragment(self):
		self._iter = 0
		decoded_fragment = ''

		next_char = self._get_next_char(self._fragment)

		while next_char is not None:
			if next_char == '%':
				first_hex_digit = self._get_next_char(self._fragment)
				second_hex_digit = self._get_next_char(self._fragment)

				if first_hex_digit is None or second_hex_digit is None:
					raise UriSyntaxError

				decoded_fragment += self._decode(first_hex_digit + second_hex_digit)

			elif next_char in self._reserved_chars:
				raise UriSyntaxError

			else:
				decoded_fragment += next_char

			next_char = self._get_next_char(self._fragment)

		self._fragment = decoded_fragment

	# Checks charset, splits query into query params which are decoded and put into dictionary.
	def _parse_query(self):
		if self._query == '':
			return
		for c in self._query:
			if c in self._reserved_chars and c not in ('&', '='):
				raise UriSyntaxError

		tokens = self._query.split('&')
		for token in tokens:
			if token.count('=') != 1:
				raise UriSyntaxError
			param, value = token.split('=', 1)
			param = self._decode_all(param)
			value = self._decode_all(value)
			self._query_params[param] = value

	# Decodes percent-encoded character.
	# e.g. when '%2B' is passed, '+' is returned.
	def _decode(self, hex_num):
		try:
			value = int(hex_num, 16)
		except ValueError:
			raise UriSyntaxError

		return chr(value)

	# Decodes all encodings in provided string.
	def _decode_all(self, string):
		self._iter = 0
		outStr = ''
		next_char = self._get_next_char(string)

		while next_char is not None:
			if next_char == '%':
				first_hex_digit = self._get_next_char(string)
				second_hex_digit = self._get_next_char(string)

				if first_hex_digit is None or second_hex_digit is None:
					raise UriSyntaxError

				outStr += self._decode(first_hex_digit + second_hex_digit)
			else:
				outStr += next_char

			next_char = self._get_next_char(string)

		return outStr


	# Returns another character from provided string.
	# If there is no more characters left, None is returned.
	def _get_next_char(self, string):
		if self._iter == len(string):
			return None

		self._iter += 1
		return string[self._iter - 1]
		
