import re
import os 
from math import ceil
dir_path = os.path.dirname(os.path.realpath(__file__))
#print(dir_path)
#print(os.listdir(dir_path))
LEFT = 0
TOP = 0
TOTAL_WIDTH = 350
TOTAL_HEIGHT = 440
BOTTOM = 0
RIGHT = 0

origin_x = 0
origin_y = 0
scaling_x = 2
scaling_y = 2

filename = "jab4c20case_3.gcode"
#filename = "jab4c20case_1.gcode"
try:
    filename=os.environ['USEFILE']
except:
    print("No USEFILE parameter given: using default filename")

def extract_number_for_var(string,var):
	elem = string[string.index(var)+len(var):]
	elem = re.findall(r"[-+]?\d*\.\d+|\d+", elem)
	#https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string
	return float(elem[0])
	
def extract_all_numbers(string):
  if(";" in string):string = string[:string.index(";")]
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
  x=round(point[0]*1000000)/1000000
  y=round(point[1]*1000000)/1000000
  output = ("G"+str(int(G))+" F"+str(int(F))+" X"+str(x)+" Y"+str(y)+" Z"+str(Z))+comment
  return output
	
def is_inside(position):	#test if inside of bounds
	return (LEFT<position[0] and position[0]<TOTAL_WIDTH-RIGHT and TOP<position[1] and position[1]<TOTAL_HEIGHT-BOTTOM)
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
	
def cleanup_airmoves(moves):
    #Enlève les déplacements dans l'air inutiles et les accélère
    result = []
    consecutive_z10 = 0
    for move in moves:
        move=move.strip()
        if(startwith(move,"G0") or startwith(move,"G1")):
            G, F, comment, point, Z = process_move(move)
            if(Z==10):
                F=2000
                consecutive_z10+=1
            else:
                consecutive_z10=0
            if(consecutive_z10>=3):
                result.pop(-1)
            result.append(recombine_move(G,F,comment,point,Z))
        else:
            result.append(move)
    return result


def cleanup_spikes(moves):
    #Enlève les pics et dents de scie
    NEUTRAL_STATE = 0
    POTENTIAL_SPIKE = 1
    state = NEUTRAL_STATE
    neutral_buffer = []
    spike_buffer = []
    current_z = 10
    current_position = (0,0)
    
    gcode_result = []
    
    for move in moves:
        move=move.strip()
        if(startwith(move,"G0") or startwith(move,"G1")):
            G, F, comment, pos, Z = process_move(move)
            
            same_pos = (pos == current_position)
            change_pos = (not same_pos)
            same_z = (Z == current_z)
            change_z = (not same_z)
            
            if(state == NEUTRAL_STATE):
                if(same_pos and same_z):
                    neutral_buffer.append(move)
                elif(change_pos and same_z):
                    gcode_result.extend(neutral_buffer) #flush buffer
                    neutral_buffer = [move]
                    current_position = pos
                elif(change_pos and change_z):
                    #dent de scie /|
                    #ajoute un côté à la dent de scie pour en faire un rectangle |-|
                    neutral_buffer.append(0,1000,";Eviter dent de scie",current_position,Z)
                    gcode_result.extend(neutral_buffer) #flush buffer
                    neutral_buffer = [move]
                    current_position = pos
                    current_z = Z
                elif(same_pos and change_z):
                    #pic ou dent: changer d'état
                    state = POTENTIAL_SPIKE
                    spike_buffer = [move]
                    current_z = Z
                    current_position = pos
            elif(state == POTENTIAL_SPIKE):
                if(same_pos and same_z):
                    spike_buffer.append(move)
                elif(same_pos and change_z):
                    #Pic détecté!
                    state = NEUTRAL_STATE
                    #On enlève le pic et on revient au départ
                    neutral_buffer.append(";Pic enleve ici")
                    spike_buffer = []
                    neutral_buffer.append(move)
                    current_z = Z
                elif(change_pos and same_z):
                    #Pic évité! restart en mode normal
                    state = NEUTRAL_STATE
                    gcode_result.extend(neutral_buffer) #flush buffer
                    neutral_buffer = [move]
                    current_position = pos
                elif(change_pos and change_z):
                    #Dent de scie |\
                    #ajoute un côté à la dent de scie pour en faire un rectangle |-|
                    neutral_buffer.append(0,1000,";Eviter dent de scie'",pos,current_z)
                    gcode_result.extend(neutral_buffer) #flush buffer
                    neutral_buffer = spike_buffer
                    spike_buffer = [move]
                    current_position = pos
                    current_z = Z
                    
    gcode_result.extend(neutral_buffer)
    neutral_buffer = []
    gcode_result.extend(spike_buffer)
    spike_buffer = []
    
    return gcode_result
	
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
                            0, previous_f, previous_comment + " [after cut floor]", insert_point, 0))
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
                        #Insérer un point en de G0 au sol
                        lines.append(recombine_move(
                        0, F, comment + " [before cut floor]", insert_point, Z))
                    
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
    print("Opening "+filename)
    gcode = import_gcode(filename)
    
    gcode = scale(gcode,scaling_x,scaling_y)
    gcode = shift(gcode,-origin_x,-origin_y)
    #gcode = fit_inside(gcode,10,10)
    minx, maxx,miny,maxy = get_borders(gcode)
    stepx = TOTAL_WIDTH-LEFT-RIGHT
    stepy = TOTAL_HEIGHT-BOTTOM-TOP
    print("gcode size: %d %d"%(maxx,maxy))
    print("Cadre size: %d %d"%(stepx,stepy))
    total_images = int(ceil(maxx/stepx) * ceil(maxy/stepy))
    counter = 0
    print("Broken up in "+str(total_images))
    for xx in range(0, int(ceil(maxx)), stepx):
        for yy in range(0, int(ceil(maxy)), stepy):
            lines = shift(gcode,-xx,-yy)
            lines = remove_borders(lines)
            lines=cleanup_airmoves(lines)
            lines=cleanup_spikes(lines)
            export_gcode(lines,filename+"modified_x"+str(xx)+"_y"+str(yy)+".gcode")
            counter+=1
            print("Section "+str(counter)+" out of "+str(total_images))
    print("Done")
    exit()
    
		
