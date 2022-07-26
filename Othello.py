import pygame, sys
from pygame.locals import *
pygame.init()
screen = pygame.display.set_mode((500,500), 0, 32)
big_font = pygame.font.SysFont(None, 90)
lil_font = pygame.font.SysFont(None, 50)





class Plateau():
    """
    Construit le plateau en faisant une liste des objets Case utilisé
    """
    def __init__(self, mode):
        self._turn = "Black"
        # Liste des valeurs utilisé pour l'algorithme min-max
        self.value_list = [5.1,1.1,4.05,4.1,4.15,4.2,1.2,5.2,1.3,2.1,3.02,3.04,3.06,3.08,2.2,1.4,4.25,3.10,3.58,3.12,3.14,3.60,3.16,4.3,4.35,3.18,3.20,3.22,3.24,3.26,3.28,4.4,4.45,3.30,3.32,3.34,3.36,3.38,3.40,4.5,4.55,3.42,3.62,3.44,3.46,3.64,3.48,4.6,1.5,2.3,3.50,3.52,3.54,3.56,2.4,1.6,5.3,1.7,4.65,4.7,4.75,4.8,1.8,5.4]
        self._timer = 0
        self._game_mode = mode
        # Construction d'une matrice représentant le plateau de jeu avec tout ses "Cases" et les bordures
        self._board = [[None for i in range(10)] for i in range(10)]
        for i in range((len(self._board)-2)**2):
            self._board[int(i/8)+1][i%8+1] = Case(i%8+1, int(i/8)+1)
        # Les 4 pions de bases :
        self._board[4][4].set_pion("White")
        self._board[5][4].set_pion("Black")
        self._board[5][5].set_pion("White")
        self._board[4][5].set_pion("Black")
        # Attribution des valeurs de la liste pour chaque cases respectives
        for x in self._board:
            for y in x:
                if y != None:
                    y.value = self.value_list.pop(0)


    @property
    def turn(self):
        return self._turn

    @property
    def game_mode(self):
        return self._game_mode

    @property
    def board(self):
        return self._board


    def next_turn(self): # Tour de jeu suivant
        if self._turn == "Black":
            self._turn = "White"
        else:
            self._turn = "Black"

    def pass_turn(self): # Regarde s'il l'on doit passer le tour au joueur suivant s'y aucun coup ne peut être effectué
        for x in self._board:
            for y in x:
                if y != None:
                    if y.clickable == True:
                     return True
        self.next_turn()
        for x in self._board:
            for y in x:
                if y != None:
                    if y.pion == "":
                        y.is_clickable(self)
    
    def end(self): # Regarde s'il l'on doit arrêter la partie s'il ne reste plus de places pour mettres un pion
        if self._game_mode: # Lors du mode VS l'IA, il y a un délai entre chaque action
            if self._timer < pygame.time.get_ticks():
                self._timer = pygame.time.get_ticks()+1000
                while self._timer > pygame.time.get_ticks():
                    pass
        nmb_black = 0
        nmb_white = 0
        for x in self._board:
            for y in x:
                if y != None:
                    if y.pion == "":
                        return False
                    elif y.pion == "Black":
                        nmb_black += 1
                    else:
                        nmb_white += 1
        result(nmb_black, nmb_white) # Apparaît l'écran des résultats

    def ai_choose(self): # Méthode permettant a l'IA de trouver la meilleur case ou il doit mettre un pion par rapport a l'algorithme min-max
        choice = None
        for x in self._board:
            for y in x:
                if y != None:
                    if y.pion == "" and y.clickable == True:
                        if choice == None:
                            choice = y
                        elif choice.value < y.value:
                            choice = y
        return choice



class Case():
    """
    Les cases du jeu et leurs méthodes
    """
    def __init__(self, x, y):
        self._posx = x*50
        self._posy = y*50
        self._pion = ""
        self._coordx = x
        self._coordy = y
        self._clickable = False
        self._value = 0
        pygame.draw.rect(screen, (100,200,100), (self._posx, self._posy, 49, 49))


    @property
    def pion(self):
        return self._pion

    @property
    def clickable(self):
        return self._clickable

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, nmb):
        self._value = nmb


    def get_pos(self): # Retourne position
        return (self._posx,self._posy)

    def set_pion(self, color): # Met le pion
        self._pion = color
        if color == "Black":
            pygame.draw.circle(screen, (0,0,0), (self._posx+24,self._posy+24), 20, 0)
        else:
            pygame.draw.circle(screen, (255,255,255), (self._posx+24,self._posy+24), 20, 0)

    def is_clicked(self, plat): # Permet de faire les choses que l'on doit faire lorsque cliqué
        if plat.turn == "Black":
            self.set_pion("Black")
        else:
            self.set_pion("White")
        self._clickable = False
        pygame.draw.circle(screen, (200,0,0), (self._posx+24,self._posy+24), 3, 0)

    def beginning_conversion(self, plat, check): # Méthode permettant de voir autour de la case s'il y a une possible conversion a effectué
        """S'y une possible conversion peut s'effectuer, elle apelle la fonction suivante.
           Le paramètre "check" est bouléen permettant de changer le fonctionnement de la méthode :
            - La fonction va dans l'autre cas retourner un bouléen determinant si au moins une conversion est possible, sans effectué la conversion en elle même"""
        if plat.turn == "White":
            other_color = "Black"
        else:
            other_color = "White"
        
        # TOUT les différents checks regardant autour de la case...
        if plat.board[self._coordy-1][self._coordx-1] != None: # Check Haut-Gauche
            if plat.board[self._coordy-1][self._coordx-1].pion == other_color:
                if check == True:
                    if plat.board[self._coordy-1][self._coordx-1].checking_conversion(plat, -1, -1, other_color, check) == True:
                        return plat.board[self._coordy-1][self._coordx-1].checking_conversion(plat, -1, -1, other_color, check)
                else:
                    plat.board[self._coordy-1][self._coordx-1].checking_conversion(plat, -1, -1, other_color, check)
        if plat.board[self._coordy-1][self._coordx] != None: # Check Haut
            if plat.board[self._coordy-1][self._coordx].pion == other_color:
                if check == True:
                    if plat.board[self._coordy-1][self._coordx].checking_conversion(plat, -1, 0, other_color, check) == True:
                        return plat.board[self._coordy-1][self._coordx].checking_conversion(plat, -1, 0, other_color, check)
                else:
                    plat.board[self._coordy-1][self._coordx].checking_conversion(plat, -1, 0, other_color, check)
        if plat.board[self._coordy-1][self._coordx+1] != None: # Check Haut-Droite
            if plat.board[self._coordy-1][self._coordx+1].pion == other_color:
                if check == True:
                    if plat.board[self._coordy-1][self._coordx+1].checking_conversion(plat, -1, +1, other_color, check) == True:
                        return plat.board[self._coordy-1][self._coordx+1].checking_conversion(plat, -1, +1, other_color, check)
                else:
                    plat.board[self._coordy-1][self._coordx+1].checking_conversion(plat, -1, +1, other_color, check)
        if plat.board[self._coordy][self._coordx-1] != None: # Check Gauche
            if plat.board[self._coordy][self._coordx-1].pion == other_color:
                if check == True:
                    if plat.board[self._coordy][self._coordx-1].checking_conversion(plat, 0, -1, other_color, check) == True:
                        return plat.board[self._coordy][self._coordx-1].checking_conversion(plat, 0, -1, other_color, check)
                else:
                    plat.board[self._coordy][self._coordx-1].checking_conversion(plat, 0, -1, other_color, check)
        if plat.board[self._coordy][self._coordx+1] != None: # Check Droite
            if plat.board[self._coordy][self._coordx+1].pion == other_color:
                if check == True:
                    if plat.board[self._coordy][self._coordx+1].checking_conversion(plat, 0, +1, other_color, check) == True:
                        return plat.board[self._coordy][self._coordx+1].checking_conversion(plat, 0, +1, other_color, check)
                else:
                    plat.board[self._coordy][self._coordx+1].checking_conversion(plat, 0, +1, other_color, check)
        if plat.board[self._coordy+1][self._coordx-1] != None: # Check Bas-Gauche
            if plat.board[self._coordy+1][self._coordx-1].pion == other_color:
                if check == True:
                    if plat.board[self._coordy+1][self._coordx-1].checking_conversion(plat, +1, -1, other_color, check) == True:
                        return plat.board[self._coordy+1][self._coordx-1].checking_conversion(plat, +1, -1, other_color, check)
                else:
                    plat.board[self._coordy+1][self._coordx-1].checking_conversion(plat, +1, -1, other_color, check)
        if plat.board[self._coordy+1][self._coordx] != None: # Check Bas
            if plat.board[self._coordy+1][self._coordx].pion == other_color:
                if check == True:
                    if plat.board[self._coordy+1][self._coordx].checking_conversion(plat, +1, 0, other_color, check) == True:
                        return plat.board[self._coordy+1][self._coordx].checking_conversion(plat, +1, 0, other_color, check)
                else:
                    plat.board[self._coordy+1][self._coordx].checking_conversion(plat, +1, 0, other_color, check)
        if plat.board[self._coordy+1][self._coordx+1] != None: # Check Bas-Droite
            if plat.board[self._coordy+1][self._coordx+1].pion == other_color:
                if check == True:
                    if plat.board[self._coordy+1][self._coordx+1].checking_conversion(plat, +1, +1, other_color, check) == True:
                        return plat.board[self._coordy+1][self._coordx+1].checking_conversion(plat, +1, +1, other_color, check)
                else:
                    plat.board[self._coordy+1][self._coordx+1].checking_conversion(plat, +1, +1, other_color, check)

    def checking_conversion(self, plat, y, x, color, check): # Méthode qui parcourt les cases jusqu'à savoir EXACTEMENT s'il faut convertir les pions ou pas
        if self._pion == color: # S'il tombe sur la même couleur il continue sa recherche
            if plat.board[self._coordy+y][self._coordx+x] != None:
                return plat.board[self._coordy+y][self._coordx+x].checking_conversion(plat, y, x, color, check)
            else: # Si on tombe sur la bordure on s'arrête
                return False
        elif self._pion == "": # Si on tombe sur une case vide on s'arrête
            return False
        else: # Si on tombe sur l'autre couleur, une conversion est possible, on peut donc repartir en arrière pour convertir tout les pion précédant
            if check == True: # On retourne un bouléen si on recherchait juste si une conversion était possible
                return True
            else:
                plat.board[self._coordy-y][self._coordx-x].finish_conversion(plat, -y, -x, color)
    
    def finish_conversion(self, plat, y, x, color): # Méthode permettant de convertir les pions jusqu'au pion posé
        if color == "White":
            other_color = "Black"
        else:
            other_color = "White"
        
        if self._pion == color: # Si on est toujours pas tombé sur le pion avec notre couleur initial, on convertit et on continue notre chemin
            self.set_pion(other_color)
            plat.board[self._coordy+y][self._coordx+x].finish_conversion(plat, y, x, color)

    def is_clickable(self, plat): # Détermine si une case peut être cliquable en utilisant les fonctions de conversion avec "check" = True
        if self.beginning_conversion(plat, True) == True:
            self._clickable = True
            if plat.turn == "Black":
                pygame.draw.circle(screen, (0,0,0), (self._posx+24,self._posy+24), 20, 1) # Indicateur pour pion noir
            else:
                pygame.draw.circle(screen, (255,255,255), (self._posx+24,self._posy+24), 20, 1) # Indicateur pour pion blanc
        else:
            self._clickable = False
            pygame.draw.rect(screen, (100,200,100), (self._posx, self._posy, 49, 49))





def othello(mode): # Écran de Jeu
    pygame.display.set_caption("Othello")
    screen.fill("black")
    plateau = Plateau(mode)
    for x in plateau.board: # Initialisation des cases cliquables
        for y in x:
            if y != None:
                if y.pion == "":
                    y.is_clickable(plateau)
    while True: # Main Game Loop
        for event in pygame.event.get(): # Events :
            if event.type == pygame.MOUSEBUTTONUP: # Click de souris
                for x in plateau.board:
                    for y in x:
                        if y != None: # Exclure la bordure
                            # Regarde si la souris a cliqué sur une des cases
                            if y.get_pos()[0] <= pygame.mouse.get_pos()[0] <= y.get_pos()[0]+49 and y.get_pos()[1] <= pygame.mouse.get_pos()[1] <= y.get_pos()[1]+49:
                                if y.clickable == True: # Vérifie s'y la case cliqué était bien "cliquable"
                                    y.is_clicked(plateau)
                                    y.beginning_conversion(plateau, False)
                                    plateau.next_turn()
                for x in plateau.board: # Check des cases clickables
                    for y in x:
                        if y != None:
                            if y.pion == "":
                                y.is_clickable(plateau)
                            if y.pion != "" and y.pion == plateau.turn: # Reset l'indicateur du dernier pion posé
                                y.set_pion(y.pion)
                pygame.display.update()
                plateau.pass_turn()
                plateau.end()

            if event.type == QUIT: # Fermer le jeu
                pygame.quit()
                sys.exit()

        if plateau.game_mode: # Partie du code pour l'IA lorsque le mode est activé
            if plateau.turn == "White": # Fonctionne comme pour le joueur, a chaque tour de l'IA
                choice = plateau.ai_choose()
                choice.is_clicked(plateau)
                choice.beginning_conversion(plateau, False)
                plateau.next_turn()
                for x in plateau.board:
                    for y in x:
                        if y != None:
                            if y.pion == "":
                                y.is_clickable(plateau)
                            if y.pion != "" and y.pion == plateau.turn:
                                y.set_pion(y.pion)
                plateau.pass_turn()
                plateau.end()
        pygame.display.update()



def result(nmb_black, nmb_white): # Écran du Résultat
    pygame.display.set_caption("Well Play")
    screen.fill((100,200,100))

    if nmb_black > nmb_white: # Condition de victoire de Noir
        screen.blit(big_font.render("Victory", True, (0, 0, 0)), (25, 100))
        screen.blit(lil_font.render(f"{nmb_black} pions", True, (0, 0, 0)), (60, 200))
        screen.blit(big_font.render("Defeat", True, (255, 255, 255)), (275, 100))
        screen.blit(lil_font.render(f"{nmb_white} pions", True, (255, 255, 255)), (300, 200))
    elif nmb_white > nmb_black: # Condition de victoire du Blanc
        screen.blit(big_font.render("Defeat", True, (0, 0, 0)), (25, 100))
        screen.blit(lil_font.render(f"{nmb_black} pions", True, (0, 0, 0)), (60, 200))
        screen.blit(big_font.render("Victory", True, (255, 255, 255)), (275, 100))
        screen.blit(lil_font.render(f"{nmb_white} pions", True, (255, 255, 255)), (300, 200))
    else: # Condition d'égalité
        screen.blit(big_font.render("Draw", True, (0, 0, 0)), (50, 100))
        screen.blit(lil_font.render(f"{nmb_black} pions", True, (0, 0, 0)), (60, 200))
        screen.blit(big_font.render("Draw", True, (255, 255, 255)), (300, 100))
        screen.blit(lil_font.render(f"{nmb_white} pions", True, (255, 255, 255)), (300, 200))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()



def main(): # Écran du Menu
    pygame.display.set_caption("Menu")
    screen.fill((100,200,100))
    
    screen.blit(big_font.render("Othello", True, (0, 0, 0)), (150, 50)) # Titre
    
    pygame.draw.rect(screen, (0,0,0), (50, 200, 400, 100)) # Bouton "Player VS Player"
    screen.blit(lil_font.render("Player VS Player", True, (255, 255, 255)), (115, 235))
    
    pygame.draw.rect(screen, (0,0,0), (50, 350, 400, 100)) # Bouton "Player VS AI"
    screen.blit(lil_font.render("Player VS AI", True, (255, 255, 255)), (115, 385))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP: # Vérifie s'y le joueur clique sur un bouton
                if 50 <= pygame.mouse.get_pos()[0] <= 450 and 200 <= pygame.mouse.get_pos()[1] <= 300:
                    othello(False)
                if 50 <= pygame.mouse.get_pos()[0] <= 450 and 350 <= pygame.mouse.get_pos()[1] <= 450:
                    othello(True)
        pygame.display.update()



if __name__ == "__main__":
    main()