# -*- coding: utf-8 -*-


from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import random

# Define constants for the game
PLAYER_1 = 0
PLAYER_2 = 1
NUMSTR = ("player1", "player2")

SIZE = 10  # Grid size
NUMBER_OF_ZOMBIES = 10  # Number of Zombies in the game


# Grid Directions
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Up, Down, Left, Right

class Player():
    def __init__(self, number):
        self.number = number
        if number == PLAYER_1:
            self.pos = [0, 0] # Inicializar la posición del jugador 1 en la esquina superior izquierda
        else:
            self.pos = [SIZE-1, SIZE-1] # Inicializar la posición del jugador 2 en la esquina inferior derecha
    
    def get_pos(self):
        return self.pos
    
    def get_number(self):
        return self.number
    
    def moveUp(self):
        # Mueve al jugador hacia arriba disminuyendo la coordenada y
        if self.pos[1] == 0:
            self.pos[1] = 0 # El jugador ya está en el borde superior, no puede moverse más arriba
        else:
            self.pos[1] -= 1 # Disminuir la coordenada y en 1 para mover al jugador hacia arriba

    def moveDown(self):
        # Mueve al jugador hacia abajo aumentando la coordenada y
        print(self.pos)
        if self.pos[1] == SIZE - 1:
            self.pos[1] = SIZE - 1  # El jugador ya está en el borde inferior, no puede moverse más abajo
        else:
            self.pos[1] += 1 # Aumentar la coordenada y en 1 para mover al jugador hacia abajo
    def moveLeft(self):
        # Mueve al jugador hacia la izquierda disminuyendo la coordenada x
        print(self.pos)
        if self.pos[0] == 0:
            self.pos[0] = 0 # El jugador ya está en el borde izquierdo, no puede moverse más a la izquierda
        else:
            self.pos[0] -= 1   # Disminuir la coordenada x en 1 para mover al jugador hacia la izquierda
    def moveRight(self):
        # Mueve al jugador hacia la derecha aumentando la coordenada x
        print(self.pos)
        if self.pos[0] == SIZE -1:
            self.pos[0] = SIZE -1 # El jugador ya está en el borde derecho, no puede moverse más a la derecha
        else:
            self.pos[0] += 1  # Aumentar la coordenada x en 1 para mover al jugador hacia la derecha
        
    
    def __str__(self):
        return f"P<{NUMSTR[self.number]}, {self.pos}>"


class Zombie():
    def __init__(self, x, y):
         # Inicializar la posición del zombie
        self.x = x
        self.y = y
        
    def get_pos(self):
        return ((self.x, self.y))
    
    def set_pos(self, x, y):
        self.x = x
        self.y = y
    
class Cell():
    def __init__(self):
        self.znumber = ""  # Número de zombis cercanos (inicialmente desconocido)
        self.zombie_inside = None
        self.player_inside = None
        
    def get_zombie(self):
        # Obtener el zombi dentro de la celda
        return self.zombie_inside
    
    def has_zombie(self):
        # Comprobar si la celda tiene un zombi dentro
        return self.zombie_inside != None
                
    def put_zombie(self, zombie):
         # Colocar un zombi dentro de la celda
        self.zombie_inside = zombie
        
    def put_player(self, player):
        # Colocar un jugador dentro de la celda
        self.player_inside = player
        
    def remove_player(self):
        # Quitar al jugador de la celda
        self.player_inside = None
        
    def get_znumber(self):
        # Obtener el número de zombis cercanos
        return self.znumber
        
    def update_znumber(self, znumber):
        # Actualizar el número de zombis cercanos
        self.znumber = str(znumber)
    
class Game():
    def __init__(self, manager):
        # Inicializar el juego
        self.players = manager.list([Player(PLAYER_1), Player(PLAYER_2)])
        self.cells = [[Cell() for i in range(SIZE)] for j in range(SIZE)]
        self.zombies = [Zombie(random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)) for _ in range(NUMBER_OF_ZOMBIES)]
        self.cure = [random.randint(0, SIZE-1),random.randint(0, SIZE-1)]
        while self.cure == [0, 0] or self.cure == [SIZE-1, SIZE-1]:
            self.cure = self.cure = [random.randint(0, SIZE-1),random.randint(0, SIZE-1)]
        self.lista_pos = [(0,0),(SIZE-1, SIZE-1), (self.cure[0], self.cure[1])]
        
        # Asegurarse de que los zombis no se coloquen en posiciones ocupadas
        for zombie in self.zombies:
            while zombie.get_pos() in self.lista_pos: 
                new_x, new_y = random.randint(0, SIZE-1), random.randint(0, SIZE-1)
                zombie.set_pos(new_x, new_y)
            self.lista_pos.append((zombie.get_pos()[0],zombie.get_pos()[1]))
         
                
        self.running = Value('i', 1) #1 running
        self.lock = Lock()

        # Colocar los zombis en las celdas correspondientes
        for zombie in self.zombies:
            self.cells[zombie.x][zombie.y].put_zombie(zombie)
        print(self.lista_pos)
    
    def player_got_cure(self, number):
        # Comprobar si el jugador ha obtenido la cura
        if self.players[number].get_pos() == self.cure:
            return True
        else:
            return False
        
    def is_player_caught(self, number):
        # Comprobar si el jugador ha sido atrapado por un zombi
        x, y = self.players[number].get_pos()[0],self.players[number].get_pos()[1]
        return self.cells[x][y].has_zombie()
    
    def get_player(self, number):
        # Obtener el jugador por su número
        return self.players[number]
    
    def is_running(self):
        # Comprobar si el juego está en ejecución
        return self.running.value == 1
    
    def stop(self):
        # Detener el juego
        self.running.value = 0
        
    def moveUp(self, number):
        # Mover al jugador hacia arriba
        self.lock.acquire()
        self.cells[self.players[number].get_pos()[0]][self.players[number].get_pos()[1]].remove_player()
        print(self.players[number].get_pos())
        p = self.players[number]
        p.moveUp()
        self.players[number] = p
        self.cells[self.players[number].get_pos()[0]][self.players[number].get_pos()[1]].put_player(self.players[number])
        self.lock.release()
    def moveDown(self, player):
        # Mover al jugador hacia abajo
        self.lock.acquire()
        self.cells[self.players[player].get_pos()[0]][self.players[player].get_pos()[1]].remove_player()
        p = self.players[player]
        p.moveDown()
        self.players[player] = p
        self.cells[self.players[player].get_pos()[0]][self.players[player].get_pos()[1]].put_player(self.players[player])
        self.lock.release()
    def moveRight(self, player):
        # Mover al jugador hacia la derecha
        self.lock.acquire()
        self.cells[self.players[player].get_pos()[0]][self.players[player].get_pos()[1]].remove_player()
        p = self.players[player]
        p.moveRight()
        self.players[player] = p
        self.cells[self.players[player].get_pos()[0]][self.players[player].get_pos()[1]].put_player(self.players[player])
        self.lock.release()
    def moveLeft(self, player):
        # Mover al jugador hacia la izquierda
        self.lock.acquire()
        self.cells[self.players[player].get_pos()[0]][self.players[player].get_pos()[1]].remove_player()
        p = self.players[player]
        p.moveLeft()
        self.players[player] = p
        self.cells[self.players[player].get_pos()[0]][self.players[player].get_pos()[1]].put_player(self.players[player])
        self.lock.release()
    
    def zombies_nearby(self, x, y):
        # Contar el número de zombis cercanos a una posición dada
        count = 0
        for direction in DIRECTIONS:
            new_x = x + direction[0]
            new_y = y + direction[1]
            if 0 <= new_x < SIZE and 0 <= new_y < SIZE and self.cells[new_x][new_y].has_zombie():
                count += 1
        return count
    
    def update_znumber(self, x, y, znumber):
        # Actualizar el número de zombis cercanos en una celda específica
        self.cells[x][y].update_znumber(znumber)
    
    def get_info(self):
        # Obtener la información actual del juego
        x1, y1 = self.players[PLAYER_1].get_pos()[0],self.players[PLAYER_1].get_pos()[1]
        x2, y2 = self.players[PLAYER_2].get_pos()[0],self.players[PLAYER_2].get_pos()[1]
        
        # Actualizar el número de zombis cercanos y el estado de la celda del jugador 1
        
        if not self.cells[x1][y1].has_zombie():
            self.cells[x1][y1].update_znumber(self.zombies_nearby(x1,y1))
        else: 
            self.cells[x1][y1].update_znumber("Z")
            
         # Actualizar el número de zombis cercanos y el estado de la celda del jugador 2    
            
        if not self.cells[x2][y2].has_zombie():
            self.cells[x2][y2].update_znumber(self.zombies_nearby(x2,y2))
        else: 
            self.cells[x2][y2].update_znumber("Z")
            
        # Construir el diccionario de información
            
        info = {
            'player1_caught': self.is_player_caught(PLAYER_1),
            'player2_caught': self.is_player_caught(PLAYER_2),
            'pos_player1': self.players[PLAYER_1].get_pos(),
            'pos_player2': self.players[PLAYER_2].get_pos(),
            'is_running': self.running.value == 1,
            'z_number_1': self.cells[x1][y1].get_znumber(),
            'z_number_2': self.cells[x2][y2].get_znumber(),
            'player1_cure': self.player_got_cure(PLAYER_1),
            'player2_cure': self.player_got_cure(PLAYER_2),
            'cure_pos': [self.cure[0], self.cure[1]]
            
        }
        return info
    
    
    
def player(number, conn, game):
        try:
            print(f"starting player {NUMSTR[number]}:{game.get_info()}")
            conn.send( (number, game.get_info()) )
            while game.is_running():
                command = ""
                while command != "next":
                    command = conn.recv()
                    if command == "up":
                        game.moveUp(number)
                    elif command == "down":
                        game.moveDown(number)
                    elif command == "right":
                        game.moveRight(number)
                    elif command == "left":
                        game.moveLeft(number)
                    elif command == "quit":
                        game.stop()
                conn.send(game.get_info())
        except:
            traceback.print_exc()
            conn.close()
        finally:
            print(f"Game ended {game}")
#Incializamos el prgograma solo si se conectan 2 jugadores
    
def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)

    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)










