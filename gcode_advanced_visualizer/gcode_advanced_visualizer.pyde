from gcode_manipulation import *
from gcode_draw import draw_gcode, set_draw_orig, set_last_point
from gcode_draw import rotate_color_set
"""
Utilisation:
    Cliquer sur l'écran pour avancer dans le GCODE
    a,z,q,s GAUCHE,DROITE pour avancer/reculer
    ESPACE pour lire
    
    C pour changer les couleurs
    V pour prendre une capture d'écran
"""

filename = "jab4c20case_1.gcode"

#Initialiser le Gcode
#On peut le manipuler
gcode = import_gcode(filename)
gcode = scale(gcode,1,1)
#gcode = rotate(gcode,1.756)
#gcode = shift(gcode,50,50)
#gcode = fit_inside(gcode,480,480,keep_ratio=True)

#Initialiser les variables de l'affichage de l'écran
minx,maxx,miny,maxy = get_borders(gcode)
print("X:",minx,"to",maxx)
print("Y:",miny,"to",maxy)

screenwidth = int(ceil(max(maxx, maxx-minx)))
screenheight = int(ceil(max(maxy, maxy-miny)))
print("Width:",screenwidth,"Height:",screenheight)

#Initialiser les variables de l'interface
#Elles seront redéfinies plus tard
redraw_background = True
last_drawn = 0
reading = True
requested = 0
first_time = True
key_held = False
f = None #font

last_filepath = None

def setup():
    #Taille du dessin + 16 de bordure de chaque côté
    #32 pour le slider
    #48 pour l'apperçu de texte
    size(screenwidth+32,screenheight+32+32+48)
    global f
    f = createFont("Arial",16,True)
    #print(dir(this))
    #this.frame.setResizable(True)
    #setResizable(True)
    
def redraw_background():
    #Dessine les boites de la fenêtre
    noStroke()
    fill(0)
    rect(0,0,2048,2048)
    fill(232)
    rect(0, 0, screenwidth+32, screenheight+32)
    fill(255)
    rect(16, 16, screenwidth, screenheight)
    #Dessine le cadre des positions dessinées
    noFill()
    stroke(248)
    cadrex=max(0,minx)
    cadrey=max(0,miny)
    rect(cadrex+16, cadrey+16, max(maxx,maxx-minx)-cadrex, max(maxy,maxy-miny)-cadrey)
    #Croix de l'origine
    stroke(160)
    origx = 16+max(0,-minx)
    origy = 16+max(0,-miny)
    line(origx-8,origy,origx+8,origy)
    line(origx,origy-8,origx,origy+8)

def select_file(filepath):
    if(filepath==None):
        print("No file selected")
    else:
        global last_filepath
        last_filepath = filepath #Next will reopen this
        
        if(not endwith(filepath.getAbsolutePath(),".gcode")):
            print(filepath,"is not a .gcode file")
        elif(filepath.exists()):
            print("Opening",filepath)
            global filename
            filename = str(filepath.getAbsolutePath())
            
            global last_drawn
            last_drawn = 0
            global requested
            requested = 0
            
            set_last_point(None,None)
            global gcode
            gcode = import_gcode(filename)
            print(len(gcode),"lines read")
            global minx,maxx,miny,maxy
            minx,maxx,miny,maxy = get_borders(gcode)
            print("X:",minx,"to",maxx)
            print("Y:",miny,"to",maxy)
            global screenwidth, screenheight
            screenwidth = int(ceil(max(maxx, maxx-minx)))
            screenheight = int(ceil(max(maxy, maxy-miny)))
            print("Width:",screenwidth,"Height:",screenheight)
            global first_time
            first_time=True
            global reading
            reading = True
            setup()
            size(screenwidth+32,screenheight+32+32+48)
            print("gcode updated")
        else:
            print(filepath,"doesn't exist")
    loop()
    
def draw():
    global gcode
    
    global first_time
    if(first_time):
        redraw_background()
        set_draw_orig(16+max(0,-minx),16+max(0,-miny))
        this.setSize(screenwidth+32,screenheight+32+32+48)
        first_time=False
        
        ####Prends une capture d'écran de la zone de dessin uniquement
        #A commenter, remplacé par la touche "V"
        # set_last_point(None,None)
        # draw_gcode(gcode)
        # border = 8
        # partialSave = get(16+max(0,int(-minx)),16+max(0,int(-miny)),
        #                 int(ceil(maxx)),int(ceil(maxy)))
        # partialSave.save(filename+".png")
        # redraw_background()
        # set_last_point(None,None)
        
    global last_drawn, reading, requested
    codesize = len(gcode)
    
    #print("Reading",reading,requested,codesize)
    if(reading):
        #Avancement automatique
        if(requested<codesize):
            requested+=1
        else:
            reading=False
            
    if(requested>last_drawn):
        #Dessiner les lignes manquantes
        draw_moves = gcode[last_drawn:requested]
        draw_gcode(draw_moves)
        last_drawn = requested
    elif(requested<last_drawn):
        #Redessiner depuis le début
        redraw_background()
        last_drawn=0
        draw_moves = gcode[last_drawn:requested]
        set_last_point(None,None)
        draw_gcode(draw_moves)
        last_drawn = requested
    
    ###Keyboard control
    global key_held
    RIGHT = 39
    LEFT = 37 #Ces variables ne sont pas bien définies dans Processing Python
    # print("Pressed:",keyPressed,"CODED:",key==CODED,"keyCode:",keyCode)
    # print("Keycodes for: RIGHT:",RIGHT,"LEFT:",LEFT,"UP:",UP,"DOWN:",DOWN)
    # #Bug: Python Processing defines RIGHT and LEFT by 0 instead of the correct values
    
    if ((keyPressed) and (key == 'z')):
        #Avancer en continu
        requested = min(requested+1,codesize)
    if ((keyPressed) and (key == 'a')):
        #Reculer en continu
        requested = max(requested-1,0)
        
    if ((keyPressed) and (key == 's') and not key_held):
        #Avancer une fois
        requested = min(requested+1,codesize)
        key_held = True
    if ((keyPressed) and (key == 'q') and not key_held):
        #Reculer une fois
        requested = max(requested-1,0)
        key_held = True
    if ((keyPressed) and (keyCode == RIGHT) and (key == CODED) and not key_held):
        #Avancer une fois
        requested = min(requested+1,codesize)
        key_held = True
    if ((keyPressed) and (keyCode == LEFT) and (key == CODED) and not key_held):
        #Reculer une fois
        requested = max(requested-1,0)
        key_held = True
    
    if ((keyPressed) and (key != ' ')  and not key_held):
        #Si on appuye sur n'importe quelle touche sauf espace, lecture automatique s'arrête
        reading=False
        
    if ((keyPressed) and (key == ' ') and not key_held):
        #Toggle pour la lecture automatique
        reading = not reading
        key_held = True
        
    if ((keyPressed) and (key == 'c') and not key_held):
        #Change le set de couleurs
        rotate_color_set()
        redraw_background()
        set_last_point(None,None)
        last_drawn=0
        key_held = True
        
    if ((keyPressed) and (key == 'v') and not key_held):
        #Prends une capture d'écran
        border = 8
        partialSave = get(16-border+max(0,int(-minx)),16-border+max(0,int(-miny)),
                        int(ceil(maxx))+2*border,int(ceil(maxy))+2*border)
        partialSave.save(filename+"_"+str(last_drawn)+".png")
        print("Saved image",filename+"_"+str(last_drawn)+".png")
        key_held = True
    
    if ((keyPressed) and (key == 'o') and not key_held):
        #Quand on relâche, affiche le prompt pour ouvrir un fichier
        key_held = True
    
    if not (keyPressed):
        if(key_held and (key == 'o')): 
            #key release done like this because "keyReleased" is broken
            selectInput("Ouvrir le fichier gcode:","select_file",last_filepath)
            noLoop()
        key_held = False
    # else:
    #     print("Key pressed:",keyPressed,"is:",(key),"is held:",key_held)
    #     print(dir(keyPressed))
        
        
    ###Progress bar
    if(mousePressed):
        #Sélectionner selon la position de la souris
        requested = int(min(max(0,float(mouseX-16)/screenwidth*codesize),codesize))
        reading=False
        
    noStroke()
    fill(192)
    rect(0,screenheight+32,screenwidth+32,32)
    fill(64)
    ratio = requested/float(codesize)
    rect(screenwidth*ratio,screenheight+32,32,32)
    
    ###Current gcode line preview
    textFont(f,14)
    fill(0);
    rect(0,screenheight+64,screenwidth+64+2048,48)
    string1 = ""
    string2 = ""
    string3 = ""
    if(requested>2):
        string1=gcode[requested-2]
    if(requested>1 and requested<=codesize):
        string2=gcode[requested-1]
    if(requested<codesize):
        string3=gcode[requested]
    fill(128);
    text(string1,0,screenheight+64+16-3);
    text(string3,0,screenheight+64+48-3);
    fill(255);
    text(string2,0,screenheight+64+32-3);
