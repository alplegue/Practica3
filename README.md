# Practica4

El código proporcionado consta de dos archivos .py, imágenes y música de fondo para el jueggo. "Servidor.py" y "Jugador.py" implementan un juego en el que dos jugadores intentan evitar ser atrapados por zombis.

El archivo "Servidor.py" contiene la lógica del juego y se encarga de administrar la comunicación entre los jugadores. Utiliza la biblioteca multiprocessing para crear procesos independientes para cada jugador. Aquí se define la clase Player, que representa a un jugador en el juego, y la clase Zombie, que representa a un zombi. También se definen las clases Cell y Game para administrar las celdas y el estado del juego.

El servidor crea una instancia de la clase Game para inicializar el juego. Dentro de la clase Game, se crea una lista de jugadores y una matriz de celdas. Los jugadores se inicializan en las esquinas opuestas de la matriz. Además, se generan una serie de zombis y se colocan en ubicaciones aleatorias en la matriz.

El servidor también crea un objeto Listener de multiprocessing.connection para aceptar conexiones de los jugadores. Una vez que se establecen dos conexiones, se inician dos procesos independientes para manejar a cada jugador. Cada proceso representa a un jugador y se ejecuta en paralelo. El servidor recibe comandos de los jugadores, como "up", "down", "left" y "right".

El método get_info() en la clase Game se utiliza para obtener la información actual del juego, incluyendo las posiciones de los jugadores, el número de zombis cercanos, si los jugadores han sido atrapados por zombis y si han obtenido la cura.

El archivo "Jugador.py" es el código que se ejecuta en la computadora de cada jugador. Utiliza la biblioteca multiprocessing.connection para establecer una conexión con el servidor. El jugador interactúa con el juego a través de la interfaz gráfica con la biblioteca pygame. El jugador puede mover a su personaje con las teclas de dirección y debe evitar ser atrapado por los zombis.

En el juego, los jugadores pueden ganar o perder según las siguientes condiciones:

Ganar:

Si ambos jugadores logran llegar a la casilla de la cura antes de que los zombis los atrapen, se considera una victoria para ambos jugadores.

Perder:

Si uno de los jugadores es capturado por un zombi antes de llegar a la casilla de la cura, ese jugador pierde.
Si ambos jugadores son capturados por los zombis antes de llegar a la casilla de la cura, se considera una derrota para ambos jugadores.
En resumen, los jugadores ganan si ambos logran llegar a la casilla de la cura antes de ser atrapados por los zombis, y pierden si uno o ambos jugadores son capturados por los zombis antes de llegar a la casilla de la cura.
