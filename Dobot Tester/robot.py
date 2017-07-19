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


class Robot():
    
    def __init__(self,robot,Ecran,fenetre,Zmin,language,pas):
        self.robot=robot
        self.Ecran=Ecran
        self.fenetre=fenetre
        self.Zmin=Zmin
        self.language=language
        self.pas=pas

    def action(self):
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
            coord=self.Ecran.Calc_Coordinates(p[3],p[5])
            Dfonct.Movement(self.robot,coord[0],coord[1],self.Zmin+30)
            self.fenetre.setpourcent(self.fenetre.getpourcent()+self.pas)
    
        #when we meet "touch"/"touch()
        def p_toucher(p):
            ''' toucher : touch lbracket rbracket
                        | touch
                        '''
            Dfonct.Touch(self.robot,self.Zmin)
            self.fenetre.setpourcent(self.fenetre.getpourcent()+self.pas)

        #when we meet "wait(xxx)"
        def p_attendre(p):
            ''' attendre : wait lbracket digit rbracket'''
            time.sleep(float(p[3])/1000.)
            self.fenetre.setpourcent(self.fenetre.getpourcent()+self.pas)
    

        def p_scroller(p):
            ''' scroller : scroll lbracket digit separator digit separator digit separator digit rbracket'''
            coord1=self.Ecran.Calc_Coordinates(p[3],p[5])
            coord2=self.Ecran.Calc_Coordinates(p[7],p[9])
            Dfonct.Scroll(self.robot,coord1[0],coord1[1],coord2[0],coord2[1],self.Zmin)
            self.fenetre.setpourcent(self.fenetre.getpourcent()+self.pas)

        # if we meet a grammar error in our input file
        def p_error(p):
            if p:
                print("Syntax error at '%s'" % p.value)
            else:
                print("Syntax error at EOF")
 
         # we survey that the langage is respected
        lex.lex()
        # we survey that the grammar is respected
        yacc.yacc()
        # we interpret our grammar
        yacc.parse(self.language)