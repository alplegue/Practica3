# -*- coding: utf-8 -*-
"""
Created on Tue May 16 18:10:25 2023

@author: Alex
"""
from multiprocessing.connection import Client
import traceback
import pygame
import sys

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
NUMBERS = ("Player 1", "Player 2")
NUMSTR = ("Player 1", "Player 2")
NZOMBIES = 10

PLAYER_COLOR = [RED, BLUE]

PLAYER_1 = 0
PLAYER_2 = 1

X = 0
Y = 1

# Configuración del tamaño de la celda y el tamaño de la pantalla

SIZE = 10
SIZE2 = (700, 700)

# Configuración de la velocidad de cuadros por segundo

FPS = 60

# Carga de imágenes de personajes

character_images = [pygame.image.load("character1.png"), pygame.image.load("character2.png")]
    
# Clase que representa a un jugador en el juego

class Player():
    def __init__(self, number):
        self.number = number
        self.pos = [None, None]     # La posición inicial del jugador se establece como [None, None]
    
    def get_pos(self):
        return self.pos              # Devuelve la posición actual del jugador
    
    def get_number(self):
        return self.number          # Devuelve el número del jugador
    
    def set_pos(self, pos):
        self.pos = pos               # Establece la posición del jugador a la posición dada
        
    def __str__(self):
        return f"P<{NUMBERS[self.number], self.pos}>"        # Representación en cadena del jugador
    

        
        
# Clase que representa a un superviviente en el juego

class Survivor(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.pos = [0,0]        # La posición inicial del superviviente se establece como [0, 0]
        self.player = player        # El superviviente se asocia a un jugador específico
        self.image = character_images[self.player.get_number()]      # La imagen del superviviente se carga según el número del jugador
        self.rect = self.image.get_rect()    # Se obtiene el rectángulo del sprite del superviviente
        self.update()     # Se llama a la función de actualización del superviviente
    def update(self):
        pos = self.player.get_pos()      # Obtiene la posición actual del jugador asociado al superviviente
        self.rect.centerx = pos[0] * 70 + 48    # Establece la posición horizontal del sprite del superviviente
        self.rect.centery = pos[1] * 70 + 48    # Establece la posición vertical del sprite del superviviente
        
        
    def __str__(self):
        return f"S<{self.player}>"
    
# Clase que representa una cura en el juego
class Cure(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = [0, 0]   # La posición inicial de la cura se establece como [0, 0]
        self.image = pygame.image.load('cure.png')   # Se carga la imagen de la cura
        self.rect = self.image.get_rect()    # Se obtiene el rectángulo del sprite de la cura
        
    def update(self, pos):
        self.rect.centerx = pos[0] * 70 + 48     # Establece la posición horizontal del sprite de la cura
        self.rect.centery = pos[1] * 70      # Establece la posición vertical del sprite de la cura
    
class Cell():
    def __init__(self):
        self.znumber = ""
        self.zombie_inside = None
        self.player_inside = None
        
    def get_zombie(self):
        # Obtiene el zombie en la celda dada
        return self.zombie_inside
    
    def has_zombie(self):
        # Verifica si hay un zombie en la celda dada
        return self.zombie_inside != None
                
    def put_zombie(self, zombie):
        # Coloca un zombie en la celda dada
        self.zombie_inside = zombie
        self.znumber = "Z"
        
    def put_player(self, player):
        # Coloca un jugador en la celda dada
        self.player_inside = player
        
    def remove_player(self):
        # Quita el jugador de la celda dada
        self.player_inside = None
        
    def get_znumber(self):
        # Actualiza el número de zombies en la celda dada
        return self.znumber
        
    def update_znumber(self, znumber):
        # Obtiene el número de zombies en la celda dada
        self.znumber = str(znumber)
    

class Zombie(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = [0, 0] # La posición inicial del zombie se establece como [0, 0]
        self.image = pygame.image.load('zombie.png') # Se carga la imagen del zombie
        self.rect = self.image.get_rect() # Se obtiene el rectángulo del sprite del zombie
        
    def update(self, pos):
        self.rect.centerx = pos[0] * 70 + 48 # Establece la posición horizontal del sprite del zombie
        self.rect.centery = pos[1] * 70  # Establece la posición vertical del sprite del zombie
        
    
class Game():
    def __init__(self):
        self.cure_obtained = [False, False]    # Lista que almacena si cada jugador ha obtenido la cura
        self.player_caught = [False, False]  # Lista que almacena si cada jugador ha sido atrapado por un zombie
        self.players = [Player(i) for i in range(2)]     # Lista de jugadores, se crea un objeto Player para cada jugador
        self.zombies = [Zombie() for i in range(NZOMBIES)]  # Lista de zombies, se crea un objeto Zombie para cada zombie
        self.running = True  # Variable que indica si el juego está en ejecución
        self.cells = [[Cell() for i in range(SIZE)] for i in range(SIZE)]  # Matriz de celdas, se crea un objeto Cell para cada celda
        self.cure = Cure()  # Objeto de cura
        self.zombie = Zombie() #Objeto Zombie

    def get_player(self, number):
        return self.players[number]  # Obtiene el jugador con el número especificado

    def get_zombie(self, n):
        return self.zombies[n]  # Obtiene el zombie con el índice especificado

    def set_pos_player(self, number, pos):
        self.players[number].set_pos(pos)  # Establece la posición del jugador con el número especificado

    def set_pos_zombie(self, n, pos):
        self.zombies[n].set_pos(pos)  # Establece la posición del zombie con el índice especificado

    def get_znumber(self, x, y):
        return self.cells[x][y].get_znumber()  # Obtiene el número de zombies en la celda con las coordenadas especificadas

    def set_znumber(self, x, y, znumber):
        self.cells[x][y].update_znumber(znumber)  # Actualiza el número de zombies en la celda con las coordenadas especificadas

    def get_cells(self):
        return self.cells  # Obtiene la matriz de celdas

    def update(self, gameinfo):
        self.set_pos_player(PLAYER_1, gameinfo['pos_player1'])      # Actualiza la posición del jugador 1 con la información del juego
        self.set_pos_player(PLAYER_2, gameinfo['pos_player2'])   # Actualiza la posición del jugador 2 con la información del juego
        self.running = gameinfo['is_running']       # Actualiza el estado de ejecución del juego con la información del juego
        self.set_znumber(self.players[PLAYER_1].get_pos()[0], self.players[PLAYER_1].get_pos()[1], gameinfo['z_number_1'])  # Actualiza el número de zombies en la celda del jugador 1 con la información del juego
        self.set_znumber(self.players[PLAYER_2].get_pos()[0], self.players[PLAYER_2].get_pos()[1], gameinfo['z_number_2'])  # Actualiza el número de zombies en la celda del jugador 2 con la información del juego
        self.player_caught[0] = gameinfo['player1_caught']   # Actualiza si el jugador 1 ha sido atrapado por un zombie con la información del juego
        self.player_caught[1] = gameinfo['player2_caught']       # Actualiza si el jugador 2 ha sido atrapado por un zombie con la información del juego
        self.cure_obtained[0] = gameinfo['player1_cure']     # Actualiza si el jugador 1 ha obtenido la cura con la información del juego
        self.cure_obtained[1] = gameinfo['player2_cure']     # Actualiza si el jugador 2 ha obtenido la cura con la información del juego
        self.cure_pos = gameinfo['cure_pos']     # Actualiza la posición de la cura con la información del juego

    def is_running(self):
        return self.running  # Verifica si el juego está en ejecución

    def stop(self):
        self.running = False  # Detiene la ejecución del juego

    def __str__(self):
        return f"G<{self.players[PLAYER_1]}:{self.players[PLAYER_2]}>"  # Retorna una representación en cadena del juego en el formato "G<Jugador1:Jugador2>"

class Display():
    def __init__(self, game):
        self.game = game  # Referencia al objeto de juego
        self.survivors = [Survivor(game.get_player(i)) for i in range(2)]  # Lista de objetos Survivor para cada jugador
        self.all_sprites = pygame.sprite.Group()  # Grupo de sprites de todos los elementos
        self.survivor_group = pygame.sprite.Group()  # Grupo de sprites de los supervivientes
        for survivor in self.survivors:
            self.all_sprites.add(survivor)  # Agrega los sprites de los supervivientes al grupo de sprites de todos los elementos
            self.survivor_group.add(survivor)  # Agrega los sprites de los supervivientes al grupo de sprites de los supervivientes
        self.cure = game.cure  # Objeto de cura del juego
        self.zombie = game.zombie #Objeto Zombie del juego
        self.cells = game.get_cells()  # Matriz de celdas del juego
        self.screen = pygame.display.set_mode(SIZE2)  # Crea la ventana del juego con el tamaño especificado
        self.clock = pygame.time.Clock()  # Reloj para controlar la velocidad de actualización
        self.background = pygame.image.load('background.png')  # Carga la imagen de fondo del juego desde un archivo
        self.cure_sprite = pygame.sprite.Group()  # Grupo de sprites de la cura
        self.zombie_sprite = pygame.sprite.Group() #Grupo de sprites del zombie
        pygame.init()  # Inicializa Pygame
        pygame.mixer.music.load("música.mp3") #Cargamos la música del juego
        pygame.mixer.music.play() #Le damos a play para que suene
            
            
    def drawCells(self):
        blocksize = 70
        for x in range(10):
            for y in range(10):
                position = (70*x, 70*y)
                rect = pygame.Rect(70*x, 70*y, blocksize, blocksize)
                pygame.draw.rect(self.screen, WHITE, rect, 1)  # Dibuja un rectángulo blanco en la posición y tamaño especificados
                font = pygame.font.Font(None, 74)  # Fuente para el texto
                text = font.render(f"{self.cells[x][y].get_znumber()}", True, WHITE)  # Renderiza el texto con el número de zombies en la celda
                self.screen.blit(text, position)  # Muestra el texto en la posición especificada
        
        
                
        
    def analyze_events(self, side):
        events = []
        if self.game.player_caught[0] or self.game.player_caught[1]:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        events.append("quit")  # Agrega el evento "quit" a la lista de eventos si se presiona la tecla Esc

        if self.game.cure_obtained[0] or self.game.cure_obtained[1]:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                   if event.key == pygame.K_ESCAPE:
                       events.append("quit")  # Agrega el evento "quit" a la lista de eventos si se presiona la tecla Esc
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")  # Agrega el evento "quit" a la lista de eventos si se presiona la tecla Esc
                elif event.key == pygame.K_UP:
                    events.append("up")  # Agrega el evento "up" a la lista de eventos si se presiona la tecla de flecha hacia arriba
                elif event.key == pygame.K_DOWN:
                    events.append("down")  # Agrega el evento "down" a la lista de eventos si se presiona la tecla de flecha hacia abajo
                elif event.key == pygame.K_LEFT:
                    events.append("left")  # Agrega el evento "left" a la lista de eventos si se presiona la tecla de flecha hacia la izquierda
                elif event.key == pygame.K_RIGHT:
                    events.append("right")  # Agrega el evento "right" a la lista de eventos si se presiona la tecla de flecha hacia la derecha
            elif event.type == pygame.QUIT:
                events.append("quit")  # Agrega el evento "quit" a la lista de eventos si se cierra la ventana del juego
        return events
    
    def refresh(self):
        self.screen.fill(BLACK)  # Llena la pantalla con el color negro
        self.all_sprites.update()  # Actualiza todos los sprites
        self.screen.blit(self.background, (0, 0)) #Dibuja el fondo en la pantalla
        self.drawCells()  # Dibuja las celdas en la pantalla
        self.all_sprites.draw(self.screen)  # Dibuja todos los sprites en la pantalla
        font = pygame.font.Font(None, 100)  # Fuente para el texto
            
        if self.game.cure_obtained[0] or self.game.cure_obtained[1]:
            self.cure.update(self.game.cure_pos)  # Actualiza la posición de la cura
            self.cure_sprite.add(self.cure)  # Agrega el sprite de la cura al grupo de sprites de la cura
            self.cure_sprite.draw(self.screen)  # Dibuja el sprite de la cura en la pantalla
            if self.game.cure_obtained[0]:
                text1 = font.render("CURE FOUND.", True, RED)  # Renderiza el texto "CURE FOUND." en rojo
                text_rect1 = text1.get_rect(center=(SIZE2[0] // 2, SIZE2[1] // 2 - 250))  # Calcula el rectángulo del texto centrado en la pantalla
                text2 = font.render("PLAYER 1 WINS", True, RED)  # Renderiza el texto "PLAYER 1 WINS" en rojo
                text_rect2 = text2.get_rect(center=(SIZE2[0] // 2, SIZE2[1] // 2 + 250))  # Calcula el rectángulo del texto centrado en la pantalla
                self.screen.blit(text1, text_rect1)  # Muestra el texto en la pantalla
                self.screen.blit(text2, text_rect2)  # Muestra el texto en la pantalla
            else:
                text1 = font.render("CURE FOUND.", True, RED)  # Renderiza el texto "CURE FOUND." en rojo
                text_rect1 = text1.get_rect(center=(SIZE2[0] // 2, SIZE2[1] // 2 - 250))  # Calcula el rectángulo del texto centrado en la pantalla
                text2 = font.render("PLAYER 2 WINS", True, RED)  # Renderiza el texto "PLAYER 2 WINS" en rojo
                text_rect2 = text2.get_rect(center=(SIZE2[0] // 2, SIZE2[1] // 2 + 250))  # Calcula el rectángulo del texto centrado en la pantalla
                self.screen.blit(text1, text_rect1)  # Muestra el texto en la pantalla
                self.screen.blit(text2, text_rect2)  # Muestra el texto en la pantalla
                
        if self.game.player_caught[0]:
            self.zombie.update(self.game.players[0].get_pos()) #Botiene la posicion del jugador atrapado
            self.zombie_sprite.add(self.zombie) #Agrega el sprite del zombie al grupo de sprites del zombie
            self.zombie_sprite.draw(self.screen) #Dibuja el sprite del zombie en pantalla
            text1 = font.render("PLAYER 1 DIED.", True, RED)  # Renderiza el texto "PLAYER 1 DIED." en rojo
            text_rect1 = text1.get_rect(center=(SIZE2[0] // 2, SIZE2[1] // 2 - 250))  # Calcula el rectángulo del texto centrado en la pantalla
            text2 = font.render("PLAYER 2 WINS", True, RED)  # Renderiza el texto "PLAYER 2 WINS" en rojo
            text_rect2 = text2.get_rect(center=(SIZE2[0] // 2, SIZE2[1] // 2 + 250))  # Calcula el rectángulo del texto centrado en la pantalla
            self.screen.blit(text1, text_rect1)  # Muestra el texto en la pantalla
            self.screen.blit(text2, text_rect2)  # Muestra el texto en la pantalla
        if self.game.player_caught[1]:
            self.zombie.update(self.game.players[1].get_pos()) #Botiene la posicion del jugador atrapado
            self.zombie_sprite.add(self.zombie) #Agrega el sprite del zombie al grupo de sprites del zombie
            self.zombie_sprite.draw(self.screen) #Dibuja el sprite del zombie en pantalla
            text1 = font.render("PLAYER 2 DIED.", True, RED)  # Renderiza el texto "PLAYER 2 DIED." en rojo
            text_rect1 = text1.get_rect(center=(SIZE2[0] // 2, SIZE2[1] // 2 - 250))  # Calcula el rectángulo del texto centrado en la pantalla
            text2 = font.render("PLAYER 1 WINS", True, RED)  # Renderiza el texto "PLAYER 1 WINS" en rojo
            text_rect2 = text2.get_rect(center=(SIZE2[0] // 2, SIZE2[1] // 2 + 250))  # Calcula el rectángulo del texto centrado en la pantalla
            self.screen.blit(text1, text_rect1)  # Muestra el texto en la pantalla
            self.screen.blit(text2, text_rect2)  # Muestra el texto en la pantalla
        
        pygame.display.flip()  # Actualiza la pantalla
        
    def tick(self):
        self.clock.tick(FPS)  # Limita la velocidad de actualización a FPS
        
    @staticmethod
    def quit():
        pygame.quit()  # Cierra la ventana del juego y finaliza Pygame

        
def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()  # Crea una instancia de la clase Game
            number, gameinfo = conn.recv()   # Recibe el número de jugador y la información del juego del servidor
            game.update(gameinfo)  # Actualiza el estado del juego con la información recibida
            display = Display(game)      # Crea una instancia de la clase Display pasando el juego como argumento
            while game.is_running():   # Mientras el juego esté en ejecución
                events = display.analyze_events(number)   # Analiza los eventos de teclado en la interfaz gráfica
                for ev in events:
                    conn.send(ev)   # Envía los eventos al servidor
                    if ev == 'quit':
                        game.stop()     # Detiene el juego si se presiona la tecla de salir
                conn.send("next")    # Envía una señal al servidor para indicar que está listo para recibir la siguiente actualización del juego
                gameinfo = conn.recv()   # Recibe la información actualizada del juego del servidor
                game.update(gameinfo)          # Actualiza el estado del juego con la nueva información recibida
                display.refresh()       # Actualiza la interfaz gráfica del juego
                display.tick()    # Controla la velocidad de actualización de la pantalla
    except:
        traceback.print_exc()  # Imprime cualquier excepción que ocurra durante la ejecución del juego
    finally:
        pygame.quit()  # Cierra la ventana del juego y finaliza Pygame


if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)        
        
        
        
        
        
        
        
        
        
        
