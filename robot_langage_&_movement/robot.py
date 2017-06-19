# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# the micro langage to lead the Dobot Magician
#
# allowed syntax :
#
# "mov(number,number)"
# "touch()"
# "touch"
# "wait(number)"
# "scroll(number,number,number,number)"
#
# the three choises can be written with or without spaces
# the three choises allowed lower and upper cases.
# "touch" can be written with or without brackets
# ------------------------------------------------------------

import ply.lex as lex
import ply.yacc as yacc
import time
import Dobotfunctions as Dfonct

# we define the required tokens for our langage.
tokens = (
   'digit',
   'lbracket',
   'rbracket',
   'separator',
   'move',
   'touch',
   'wait',
   'scroll',
)

# we define the characters which represente each token
t_digit       = r'[0-9]+\.*[0-9]*'
t_lbracket    = r'\('
t_rbracket    = r'\)'
t_separator   = r','
t_move        = r'(?i)Mov'
t_touch       = r'(?i)Touch'
t_wait        = r'(?i)Wait'
t_scroll      = r'(?i)Scroll'
t_ignore_space  = r'\s'

# we define the robot/screen's specialization

api=None
ecran=None
z_min=None

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
             | scroller commande
             | scroller
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
    print ("pause de : " + p[3] + "ms")
    time.sleep(float(p[3])/1000.)

def p_scroller(p):
    ''' scroller : scroll lbracket digit separator digit separator digit separator digit rbracket'''
    coord1=ecran.Calc_Coordinates(p[3],p[5])
    coord2=ecran.Calc_Coordinates(p[7],p[9])
    print ("scroll from ({}({} pixels),{}({} pixels)) to ({}({} pixels),{}({} pixels))".format(coord1[0],p[3],coord1[1],p[5],coord2[0],p[7],coord2[1],p[9]))
    Dfonct.Scroll(api,coord1[0],coord1[1],coord2[0],coord2[1],z_min)

# if we meet a grammar error in our input file
def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


#we define our robot, our screen (smartphone) and our file to execute (with the langage)
def robot(robot,Ecran,Zmin,file):
    """we define our robot, our test screen and our input to execute our code from the input"""
    global api
    api=robot
    global ecran
    ecran=Ecran
    global z_min
    z_min=Zmin

    s = open(file, "r")

    chaine=""
    for ligne in s:
        chaine+=ligne

    s.close

    # we survey that the langage is respected
    lex.lex()
    # we survey that the grammar is respected
    yacc.yacc()
    # we interpret our grammar
    yacc.parse(chaine)