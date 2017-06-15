# ------------------------------------------------------------
# the micro langage to lead the Dobot Magician
#
# allowed syntax :
#
# "mov(number,number)"
# "touch()"
# "touch"
# "wait(number)"
# the three choises can be written with or without spaces
# the three choises allowed lower and upper cases.
# "touch" can be written with or without brackets
# ------------------------------------------------------------
import ply.lex as lex
import ply.yacc as yacc
import time
import DobotDllType as dType
import Dobotfunctions as Dfonct
import screen as screen

# we define the required tokens for our langage.
tokens = (
   'digit',
   'lbracket',
   'rbracket',
   'separator',
   'move',
   'touch',
   'wait',
)

# we define the characters which represente each token
t_digit       = r'[0-9]+\.*[0-9]*'
t_lbracket    = r'\('
t_rbracket    = r'\)'
t_separator   = r','
t_move        = r'(?i)Mov'
t_touch       = r'(?i)Touch'
t_wait        = r'(?i)Wait'
t_ignore_space  = r'\s'


# we define the special characters representing special tokens
    
def t_newline(t):
    r'\n+'
    pass

def t_tab(t):
    r'\t+'
    pass

# if a token in the input file doesn't exist
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# we define our grammar for our langage (everithing pass by this function)
def p_move(p):
    '''commande : bouger commande
             | bouger
             | attendre commande
             | attendre
             | toucher commande
             | toucher
             '''

# when we meet "move(number,number)"
def p_bouger(p):
    ''' bouger : move lbracket digit separator digit rbracket'''
    coord=ecran.Calc_Coordinates(p[3],p[5])
    print ("go to : ({}({}pixels),{}({}pixels)".format(coord[0],p[3],coord[1],p[5]))
    Dfonct.Movement(api,coord[0],coord[1],z_min+30)
    
#when we meet "touch"/"touch()
def p_toucher(p):
    ''' toucher : touch lbracket rbracket
                | touch
                '''
    print ("touch")
    Dfonct.Touch(api,z_min)

#when we meet "wait(xxx)"
def p_attendre(p):
    ''' attendre : wait lbracket digit rbracket'''
    print "pause de : " + p[3] + "ms"
    time.sleep(float(p[3])/1000.)


# if we meet a grammar error in our input file
def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")
 
# Build the lexer
lexer = lex.lex()

#init the robot

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}
    
api = dType.load()
state = dType.ConnectDobot(api, "", 115200)[0]
print("[Etat de la connexion / Connect status : {}] \n".format(CON_STR[state]))

if (state == dType.DobotConnect.DobotConnect_NoError):
    
    # Build the parser
    yacc.yacc()
    largueur=raw_input("veuillez entrer la largueur (en pixels) de l'ecran : ")
    hauteur=raw_input("veuillez entrer la hauteur (en pixels) de l'ecran : ")
    Dfonct.Init(api)    
    ecran=screen.screen(api,largueur,hauteur) 
    z_min=Dfonct.Calc_Z_Min(api)
    
    s = open("scriptest.txt", "r")

    chaine=""
    for ligne in s:
        chaine+=ligne

    s.close
    
    yacc.parse(chaine)

#Disconnect Dobot
print("fermeture de la connexion")
dType.DisconnectDobot(api)