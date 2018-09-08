import re
import os 
from math import ceil
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
print(os.listdir(dir_path))
LEFT = 10
TOP = 10
TOTAL_WIDTH = 350
TOTAL_HEIGHT = 440
BOTTOM = 10
RIGHT = 10

origin_x = 0
origin_y = 0
scaling_x = 1
scaling_y = 1

filename = dir_path+os.sep+"jab4c20case_1.gcode"

def extract_number_for_var(string,var):
	elem = string[string.index(var)+len(var):]
	elem = re.findall(r"[-+]?\d*\.\d+|\d+", elem)
	#https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string
	return float(elem[0])
	
def extract_all_numbers(string):
	elem = re.findall(r"[-+]?\d*\.\d+|\d+", string)
	#https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string
	return (float(x) for x in elem)
	

def process_move(move):
	#Split a move into the relevant values
	comment = ""
	if(";" in move):
		comment = move[move.index(";"):]
		move = move[:move.index(";")]
	move = move.upper()
	G, F, X, Y, Z = extract_all_numbers(move)
	point = (X,Y)
	
	return G, F, comment, point, Z

def same_position(move1, move2):
	#Test if both moves have the same x and y
	process_move(move1)[3] == process_move(move2)[3]

def recombine_move(G, F,comment,point, Z):
	#Return a gcode string from the given values
	output = ("G%d F%d X%f Y%f Z%d "%(G, F, *point, Z))+comment
	return output
	
def is_inside(position):	#test if inside of bounds
	return (LEFT<position[0]<TOTAL_WIDTH-RIGHT and TOP<position[1]<TOTAL_HEIGHT-BOTTOM)
def is_outside(position):	#test if outside of bounds
	return not is_inside(position)
	
def crop_line(p1, p2):
	#Return a point between the two given points on the bounds
	if(is_outside(p1)):
		if(is_outside(p2)):
			raise Exception("both out of bounds",p1,p2)
		p = p1
		p1 = p2
		p2 = p
		
	x0 = p1[0]
	y0 = p1[1]
	dx = p2[0]-x0
	dy = p2[1]-y0
	
	#percent so that
	#x0+percent*dx and y0+percent*dy is on the border
	#p2 is the point outside. We put it on the border, then calculate its distance to p1 on both axes.
	#The smallest of the two is the one we use
	if(dx==0):
		ratiox = 1
	else:
		ratiox = (max(LEFT,min(TOTAL_WIDTH-RIGHT,p2[0]))-x0)/dx
	if(dy==0):
		ratioy = 1
	else:
		ratioy = (max(TOP,min(TOTAL_HEIGHT-BOTTOM,p2[1]))-y0)/dy
	ratio = min(ratiox,ratioy)
	#print(ratiox,ratioy)
	result = (x0+dx*ratio, y0+dy*ratio)
	return result
	
def startwith(string, start): #return if string starts with given value
	return len(string) >= len(start) and string[:len(start)]==start


def reverse_simple(moves):
	#Simplement inverse l'ordre des G0 G1
	#par blocs
	#entre les blocs qui ne sont pas G0 ou G1
	#N'insère ou enlève rien
	
	result = []
	movedata = [(0,0,0,10)]
	temp = []
	"""
	G0		 G0
	|		 |
	G01	--	G10	
	"""
	for move in moves:
		move=move.strip()
		if(startwith(move,"G0") or startwith(move,"G1")):
			temp.append(move)
		else:
			temp.reverse()
			result.append(temp)
			temp = []
			result.append(move)
	
	temp.reverse()
	result.append(temp)
	
def cleanup(moves):
	#Enlève les dupliquats et déplacements inutiles
	result = []
	consecutive_z10 = 0
	consecutive_pos = 0
	previous_pos = (0,0)
	for move in moves:
		move=move.strip()
		if(startwith(move,"G0") or startwith(move,"G1")):
			G, F, comment, point, Z = process_move(move)
			if(Z==10):
				consecutive_z10+=1
			else:
				consecutive_z10=0
			if(point == previous_pos):
				consecutive_pos+=1
			else:
				consecutive_pos=0
			if(consecutive_pos>=2 or consecutive_z10>=3):
				result.pop(-1)
			result.append(move)
			previous_pos = point
		else:
			result.append(move)
	return result
	
def get_borders(moves):
	#Return border extreme values 
	#Return order: minx, maxx, miny, maxy
	minx = float("inf")
	miny = float("inf")
	maxx = float("-inf")
	maxy = float("-inf")
	for move in moves:
		if(startwith(move,"G0") or startwith(move,"G1")):
			G, F, comment, (X,Y), Z = process_move(move)
			minx = min(X,minx)
			maxx = max(X,maxx)
			miny = min(Y,miny)
			maxy = max(Y,maxy)
	return minx, maxx, miny, maxy

def shift(moves, x=0, y=0):
	#Décale les coordonnées du gcode par le décalage donné
	result = []
	for move in moves:
		move=move.strip()
		if(startwith(move,"G0") or startwith(move,"G1")):
			G, F, comment, (X,Y), Z = process_move(move)
			X+=x
			Y+=y
			result.append(recombine_move(G, F, comment, (X,Y), Z))
		else:
			result.append(move)
	return result

def scale(moves, xscale=1,yscale=1):
	#Multiplie les coordonnées du gcode par l'échelle donnée
	result = []
	for move in moves:
		move=move.strip()
		if(startwith(move,"G0") or startwith(move,"G1")):
			G, F, comment, (X,Y), Z = process_move(move)
			X*=xscale
			Y*=yscale
			result.append(recombine_move(G, F, comment, (X,Y), Z))
		else:
			result.append(move)
	return result

def fit_inside(moves, width, height, keep_ratio=False):
	#Force le gcode à tenir dans le rectangle donné
	#Si keep_ratio = True, garde les proportions originelles
	result = []
	minx, maxx, miny, maxy = get_borders(moves)
	moves = shift(moves,-minx,-miny)
	xscale = width/(maxx-minx)
	yscale = height/(maxy-miny)
	if(keep_ratio):
		xscale = min(xscale, yscale)
		yscale = xscale
	moves = scale(moves, xscale, yscale)
	return moves
	
def import_gcode(filename):
	#Ouvre un fichier et renvoie une liste de lignes
	gcodefile = open(filename,"r")
	gcode = gcodefile.readlines()
	gcodefile.close()
	return gcode
	
def export_gcode(moves, filename):
	#Ecrit une liste de lignes dans un fichier
	fileout = open(filename,"w")
	for line in moves:
		fileout.write(line+"\n")
	fileout.close()

def remove_borders(gcode, left=LEFT, top=TOP, total_width=TOTAL_WIDTH, total_height=TOTAL_HEIGHT, right=RIGHT, bottom=BOTTOM):
	global LEFT, TOP, TOTAL_HEIGHT, TOTAL_WIDTH, RIGHT, BOTTOM 
	LEFT = left
	TOP = top
	TOTAL_HEIGHT = total_height
	TOTAL_WIDTH = total_width
	RIGHT = right
	BOTTOM = bottom
	
	previous_position = (0,0)
	previous_comment = ";point initial"
	previous_g = 0
	previous_f = 2000
	previous_z = 10
	
	lines = [] #résultat ici
	
	for move in gcode:
		move = move.strip() #enlève les espaces et \n de fin et début de ligne
		if(startwith(move,"G0") or startwith(move,"G1")):
			#C'est un déplacement, il faut le travailler
			G, F, comment, point, Z = process_move(move)
			if(is_outside(previous_position)):
				#Le point précédent était dehors. 
				if(is_outside(point)):
					#Ce point aussi: on laisse tomber un point
					pass
				else:
					#Ce point est dedans: on insère un point intermédiaire
					insert_point = crop_line(point,previous_position)
					if(previous_z == 0):
						#Insérer un point en l'air avant (si on va dessiner)
						lines.append(recombine_move(
							0, previous_f, previous_comment + " [after cut]", insert_point, 10))
					lines.append(recombine_move(
						previous_g, previous_f, previous_comment + " [moved]", insert_point, previous_z))
					lines.append(move)
			else:
				#Le point précédent était dedans
				if(is_inside(point)):
					#Ce point aussi: on le garde
					lines.append(move)
				else:
					#Ce point est dehors: on insère un point intermédiaire
					insert_point = crop_line(point,previous_position)
					lines.append(recombine_move(
						G, F, comment + " [moved]", insert_point, Z))
						
					if(Z == 0):
						#Insérer un point en l'air après (si on était en train de dessiner)
						lines.append(recombine_move(
							0, F, comment + " [before cut]", insert_point, 10))
						G=0
						Z=10
					point = insert_point
			
			previous_position = point
			previous_comment = comment
			previous_g = G
			previous_f = F
			previous_z = Z
		else:
			lines.append(move)
	return lines
	
if __name__ == "__main__":
	gcode = import_gcode(filename)
	minx, maxx,miny,maxy = get_borders(gcode)
	
	#gcode = scale(gcode,1/2,1/2)
	#gcode = shift(gcode,50,50)
	#gcode = fit_inside(gcode,10,10)
	
	for xx in range(0, int(ceil(maxx)), TOTAL_WIDTH-LEFT-RIGHT):
		for yy in range(0, int(ceil(maxy)), TOTAL_HEIGHT-BOTTOM-TOP):
			lines = shift(gcode,xx,yy)
			lines = remove_borders(lines)
			lines=cleanup(lines)
			"""
			for line in lines:
				print(repr(line))
			"""
			export_gcode(lines,filename+"modified_x"+str(xx)+"_y"+str(yy)+".gcode")
	

		