# -*- coding: utf-8 -*-

def main():
	message = 'Bienvenido'
	print(message)

	raz_social = raw_input('Ingrese razon social: ')

	# términos del texto ingresado
	terms = raz_social.split()

	errors = []

	if faltanEspaciosAlCostadoDeEspeciales(terms):
		errors.append('Los caracteres "&", "+" y "$" deben emplearse considerando un espacio entre cada signo.')

	if " - " in raz_social or " / " in raz_social:
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
		errors.append("En el caso que contenga letras o iniciales con punto y espacio, o solo espacio, estos espacios no se considerarán, debiendo juntarse las letras o iniciales.")

	if "α" in raz_social:
		errors.append("El símbolo Alfa no puede incorporarse. Es correcto si se escribe la palabra ALFA en lugar del símbolo respectivo.")

	if raz_social.endswith('.'):
		errors.append("En el caso de denominaciones que concluyen con un punto no se considera dicho signo.")

	if presentaComasIncorrectasOTildes(terms):
		errors.append("No se considera la coma en los números ni la tilde en las palabras.")

	if len(errors) == 0:
		print 'Ingresaste una razon social valida: %s' % (raz_social)	
	else:
		print 'Ingresaste 1 razon social no valida: %s' % (raz_social)
		for error in errors:
			print error

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
	# Cant letras que están después del '         >1 and ' pos <> 1
	for term in terms:
		ocurrences = term.count("'")

		if ocurrences == 0:
			continue

		if ocurrences > 1:
			return True

		if term[0] == "'":
			return True

		pos = term.find("'")
		characters = len(term) - pos - 1
		if characters > 1 and pos != 1:
			return True

	return False

# D. H. B. 	(Incorrecto)   -> 1 term de 2 car donde el último es 1 pto
# D.H.B. 	(Correcto)
# R B C 	(Incorrecto)   -> 1 term de 1 car
# RBC 		(Correcto)
def presentaInicialesIncorrectas(terms):
	for term in terms:
		if len(term) == 2 and term[1] == '.' or len(term) == 1 and term.isalpha() and term != 'Y':
			return True

	return False

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
	# tildes = ['Á', 'É', 'Í', 'Ó', 'Ú', 'á', 'é', 'í', 'ó', 'ú']
	tildes = [181, 144, 214, 224, 233, 160, 130, 161, 162, 163]
	iEspecial = tildes[2]
	# print "Valor de Í => %d - %d" % (ord(iEspecial[0]), ord(iEspecial[1]))
	for char in term:
		# print "El caracter %s (%d) se encuentra en tildes? => %r" % (char, ord(char), char in tildes)
		if ord(char) in tildes:
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

 

main()