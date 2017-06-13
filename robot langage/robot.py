# ------------------------------------------------------------
# the micro langage to lead the Dobot Magician
#
# allowed sinthax :
#
# "move(numer,number)"
# "touch()"
# "touch"
# the three choises can be written with or without spaces
# the three choises allowed lower and upper cases.
# "touch" can be written with or without brackets
# ------------------------------------------------------------
import ply.lex as lex
import ply.yacc as yacc

# we define the required tokens for our langage.
tokens = (
   'digit',
   'lbracket',
   'rbracket',
   'separator',
   'move',
   'touch',
)

# we define the characters which represente each token
t_digit       = r'[0-9]+'
t_lbracket    = r'\('
t_rbracket    = r'\)'
t_separator   = r','
t_move        = r'(?i)Move'
t_touch       = r'(?i)Touch'
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
             | toucher commande
             | toucher
             '''

# when we meet "move(number,number)"
def p_bouger(p):
    ''' bouger : move lbracket digit separator digit rbracket'''
    print "go to : ("+p[3]+","+p[5]+")"
    
#when we meet "touch"/"touch()
def p_toucher(p):
    ''' toucher : touch lbracket rbracket
                | touch
                '''
    print("toucher")
    

# if we meet a grammar error in our input file
def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")
 
# Build the lexer
lexer = lex.lex()
# Build the parser
yacc.yacc()


s = open("data.txt", "r")
chaine=""
for ligne in s:
    chaine+=ligne

yacc.parse(chaine)



