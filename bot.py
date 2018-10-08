# encoding: utf-8
import logging

DEFAULT_RESPONSE = u"Disculpa, no entendí. ¿Deseas volver a empezar?"
DEFAULT_POSSIBLE_ANSWERS = [u"Sí", u"No"]

class Bot(object):
	def __init__(self, send_callback, users_dao, tree):
		self.send_callback = send_callback
		self.users_dao = users_dao
		self.tree = tree

	def enviarFb(self, text):
		possible_answers = None
		self.send_callback(self.user_id, text, possible_answers)

	def handleRazSocial(self, user_id, raz_social):
		errors = validarRazSocial(raz_social)

		if len(errors) == 0:
			response_text = '¡El nombre que deseas registrar es correcto!'
			self.enviarFb(response_text)
			self.users_dao.add_user_event(user_id, 'bot', response_text)
		else:
			response_text = '¡El nombre que deseas registrar es incorrecto!'
			self.enviarFb(response_text)
			self.users_dao.add_user_event(user_id, 'bot', response_text)
			for error in errors:
				self.enviarFb("- " + error)
		

	def handle(self, user_id, user_message):
		logging.info("Se invocó el método handle")
		self.user_id = user_id
	
		# obtener el historial de eventos/mensajes
		self.users_dao.add_user_event(user_id, 'user', user_message)
		history = self.users_dao.get_user_events(user_id)
		tree = self.tree
	
		# determinar 1 rpta en func al mensaje escrito por el usuario
		new_conversation = True
		bot_asked_about_restart = False
		evaluate_company_name = False

		for text, author in history:
			bot_reply = True
		# 	logging.info("text: %s", text)
		# 	logging.info("author: %s", author)

			if author == 'bot':
				new_conversation = False
				bot_asked_about_restart = False
				evaluate_company_name = False

				if text == DEFAULT_RESPONSE:
					bot_asked_about_restart = True
				elif text == u"Ingresa tu razón social":
					evaluate_company_name = True
				elif 'say' in tree and text == tree['say'] and 'answers' in tree:
					tree = tree['answers']

			elif author == 'user':
				if new_conversation:
					response_text = tree['say']
					possible_answers = tree['answers'].keys()
					possible_answers.sort()

				elif evaluate_company_name:
					raz_social = text

				else:
					if bot_asked_about_restart:
						if text == u'Sí':
							tree = self.tree
							response_text = tree['say']
							possible_answers = tree['answers'].keys()
							possible_answers.sort()
							self.users_dao.remove_user_events(user_id)
							break
						elif text == u'No':
							bot_reply = False
							continue

					key = get_key_if_valid(text, tree)
					if key is None:
						response_text = DEFAULT_RESPONSE
						possible_answers = DEFAULT_POSSIBLE_ANSWERS
					else:
						tree = tree[key]
						if 'say' in tree:
							response_text = tree['say']
						if 'answers' in tree:
							possible_answers = tree['answers'].keys()
							possible_answers.sort()
						else:
							possible_answers = None

		# # logging.info("response_text: %s", response_text)
		# # logging.info("possible_answers: %r", possible_answers)
		if bot_reply:
			if evaluate_company_name:
				self.handleRazSocial(user_id, raz_social)
			else:
				self.send_callback(user_id, response_text, possible_answers)
				self.users_dao.add_user_event(user_id, 'bot', response_text)

def validarRazSocial(raz_social):
	# términos del texto ingresado
	terms = raz_social.split()

	errors = []

	if faltanEspaciosAlCostadoDeEspeciales(terms):
		errors.append('Los caracteres "&", "+" y "$" deben emplearse considerando un espacio entre cada signo.')

	not_allowed = [" -", "- ", " /", "/ "]
	if any(expr in raz_social for expr in not_allowed):
		errors.append('Los caracteres "-" y "/" deben transcribirse sin considerar espacios.')

	if raz_social.startswith('(') and raz_social.endswith(')'):
		errors.append('Se admite el uso de paréntesis cuando estos formen parte de la denominación dentro, al medio o al final, no en los extremos.')

	if '"' in raz_social:
		errors.append('En ningún caso serán consideradas las comillas "" que consten al comienzo, en el medio, al final o en los extremos de la razón social.')

	if '=' in raz_social:
		errors.append('Cuando en la razón social se emplea el signo igual "=", deberá reemplazarse por el guion "-"" sin considerar espacios entre una palabra y la otra.')

	if usaApostrofeInvalido(terms):
		errors.append("En el caso de incluir apostrofe (') dentro de una misma palabra, no se considerará espacio alguno. De haberse empleado entre dos palabras distintas, debe considerarse un espacio después del apostrofe.")

	if presentaInicialesIncorrectas(terms):
		errors.append("De contener letras o iniciales con punto y espacio, o solo espacio, estos espacios no se considerarán, debiendo juntarse las letras o iniciales. A menos que una Y junte a las iniciales.")

	if "α" in raz_social:
		errors.append("El símbolo Alfa no puede incorporarse. Es correcto si se escribe la palabra ALFA en lugar del símbolo respectivo.")

	if raz_social.endswith('.'):
		errors.append("En el caso de denominaciones que concluyen con un punto no se considera dicho signo.")

	if presentaComasIncorrectasOTildes(terms):
		errors.append("No se considera la coma en los números ni la tilde en las palabras.")

	return errors

# A & B INGENIEROS S.A. (CORRECTO)
# A&B INGENIEROS S.A. 	(INCORRECTO)
def faltanEspaciosAlCostadoDeEspeciales(terms):
	for term in terms:
		if len(term)>1 and ("&" in term or "+" in term or "$" in term):
			return True

	return False

# PAPI’S	 (CORRECTO)   Pos: 4 - Tam: 6 - Letras: 1 = 6-4-1
# D’MAMI	 (CORRECTO)   Pos: 1 - Tam: 6 - Letras: 4 = 6-1-1
# Juan'  	 (CORRECTO)   Pos: 4 - Tam: 5 - Letras: 0 = 5-4-1
# Juan'Ramos (INCORRECTO) Letras = Tam - Pos - 1
# 'Juan 	 (INCORRECTO)
# 'Ramos 	 (INCORRECTO)
def usaApostrofeInvalido(terms):
	# Es incorrecto cuando:
	# tener más de 1 ' en el mismo término
	# or
	# Cant letras que hay antes del '             =0
	# or
	# Son 2 letras y termina en ' (como en D' MAMI)
	# or
	# Cant letras que están después del '         >1 and ' pos <> 1
	for term in terms:
		ocurrences = term.count("'")

		if ocurrences == 0:
			continue

		if ocurrences > 1:
			return True

		if term[0] == "'":
			return True

		if len(term) == 2 and term[1] == "'": # D' P'
			return  True

		pos = term.find("'")
		characters = len(term) - pos - 1
		if characters > 1 and pos != 1:
			return True

	return False

# D. H. B. 	(Incorrecto)   -> 1 term de 2 car donde el último es 1 pto
# D.H.B. 	(Correcto)
# R B C 	(Incorrecto)   -> 1 term de 1 car
# RBC 		(Correcto)
# D Y H     (Correcto) -> la Y es una excepción a la regla (también &, + y $)
def presentaInicialesIncorrectas(terms):
	# buscamos si aparecen los conectores excepción y los excluímos
	conectoresExcepcion = ['Y', '&', '+', '$']
	for conector in conectoresExcepcion:
		terms = saltarConectorExcepcionDeIniciales(terms, conector)

	for term in terms: ## && ||
		if len(term) == 2 and term[1] == '.' or len(term) == 1 and term.isalpha() and term != 'Y':
			return True

	return False

def saltarConectorExcepcionDeIniciales(terms, conector):
	if conector in terms:
		# índice del conector excepción
		index = terms.index(conector)
		# obviar elemento siguiente
		if index < len(terms)-1:
			nextTerm = terms[index+1]
			if len(nextTerm)==1:
				del terms[index+1]
		# obviar elemento anterior
		if index > 0:
			prevTerm = terms[index-1]
			if len(prevTerm)==1:
				del terms[index-1]
		# importa borrar 1ro el sgte, para no alterar la posición del anterior

	return terms

# LIBRERÍA 2,000 S.R.L.		(INCORRECTO)
# LIBRERÍA 2000 S.R.L.		(CORRECTO)
# LEÓN Y RAMIREZ S.R.L.		(INCORRECTO)
# LEON Y RAMIREZ S.R.L.		(CORRECTO)
def presentaComasIncorrectasOTildes(terms):
	for term in terms:
		if presentaTildes(term) or presentaComasIncorrectas(term):
			return True

	return False

def presentaTildes(term):
	tildes = ['Á', 'É', 'Í', 'Ó', 'Ú', 'á', 'é', 'í', 'ó', 'ú']
	# tildes = [181, 144, 214, 224, 233, 160, 130, 161, 162, 163]
	# iEspecial = tildes[2]
	# print "Valor de Í => %d - %d" % (ord(iEspecial[0]), ord(iEspecial[1]))
	for char in term:
		# print "El caracter %s (%d) se encuentra en tildes? => %r" % (char, ord(char), char in tildes)
		if char in tildes:
			return True

	return False

def presentaComasIncorrectas(term):
	# saltamos los terms que no deben ser evaluados
	for char in term:
		if not char.isdigit() and char != ',':
			return False

	# es incorrecto porque presenta una coma dentro de un nro
	if ',' in term:
		return True

	return False

def get_key_if_valid(text, dictionary):
	for key in dictionary:
		if key.lower() == text.lower():
			return key

	return None
