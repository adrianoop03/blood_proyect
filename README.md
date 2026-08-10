# Damn Beast 

## Videojuego 2D desarrollado con Python y Pygame

---

## Integrantes

* **Lautaro Tonini**
* **Fabrizio Rossato**
* **Adriano Oyola**
* **Gregorio Bizzotto**

---

#Descripción del juego

**Damn Beast** es un videojuego de acción 2D desarrollado en **Python utilizando Pygame**.

El jugador controla a un cazador de criaturas que debe recorrer diferentes escenarios, enfrentarse a enemigos y completar las distintas situaciones que presenta el juego.

El videojuego cuenta con diferentes sistemas que interactúan entre sí:

* Movimiento del jugador.
* Sistema de cámara.
* Animaciones.
* Sistema de sonido.
* Sistema de vida.
* Sistema de aguante.
* Sistema de combate.
* Balas.
* Enemigos.
* Inteligencia artificial de enemigos.
* Spawn de enemigos.
* Sistema de curación.
* Efectos de sangre.
* Menú principal.
* Menú de opciones.
* Sistema de pausa.
* Sistema de puntuación.
* HUD.
* Sistema de niveles.
* Colisiones.
* Máquina de estados.

El proyecto fue desarrollado de manera grupal aplicando programación modular y diferentes **patrones de diseño** para separar responsabilidades y facilitar el mantenimiento del código.

---

# Historia

Damn Beast cuenta la historia de un alcohólico de pasado incierto que se dedica a **cazar criaturas por dinero**.

Su vida es bastante sencilla: conseguir dinero, comer, emborracharse y disfrutar de las mujeres. No le interesa convertirse en un héroe, salvar el mundo ni descubrir qué ocurrió con su pasado.

Frecuenta un bar donde consigue diferentes trabajos. Desde allí recibe encargos para cazar criaturas y obtener dinero a cambio.

Para él, enfrentarse a criaturas peligrosas simplemente forma parte de su trabajo.

##Las armas legendarias

Durante una de sus tantas noches de borrachera, el protagonista terminó apostando **su propia alma contra un dios desconocido**.

Contra todo pronóstico, ganó la apuesta y consiguió unas **armas legendarias**, cuyo verdadero origen y poder siguen siendo un misterio.

Pero esa no fue la única apuesta relacionada con el alcohol.

En otra ocasión se enfrentó a **Dionisio, el dios del alcohol**, y de aquel encuentro consiguió **la Peta**.

### La Peta

La Peta es una **petaca especial** que posee propiedades sobrenaturales.

Cuando el protagonista bebe de ella, consigue **recuperar vida**, convirtiéndola en uno de los objetos más importantes para sobrevivir durante las cacerías.

A pesar de todo lo que ocurre a su alrededor, al protagonista no le interesan demasiado las consecuencias de sus acciones.

Su filosofía es sencilla:

> **Vivir, comer, beber y conseguir mujeres.**

Mientras pueda seguir haciendo todo eso, continuará aceptando trabajos en el bar y enfrentándose a cualquier criatura que se cruce en su camino.

---

# Tecnologías usadas

El proyecto fue desarrollado utilizando las siguientes tecnologías:

### Lenguaje

* **Python 3**

### Motor / librería

* **Pygame 2.6.1**

### Mapas

* **PyTMX 3.32**

PyTMX es utilizado para cargar y administrar los mapas creados mediante herramientas compatibles con el formato TMX.

### Base de datos

* **SQLite**
* SQL

### Control de versiones

* **Git**
* **GitHub**

### Herramientas de asistencia

* GitHub Copilot
* ChatGPT
* Claude Code

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/adrianoop03/blood_proyect.git
```

## 2. Ingresar al proyecto

```bash
cd blood_proyect
```

## 3. Crear un entorno virtual

```bash
python -m venv .venv
```

## 4. Activar el entorno virtual

En Windows:

```bash
.venv\Scripts\activate
```

## 5. Instalar las dependencias

```bash
pip install -r requirements.txt
```

Las principales dependencias utilizadas por el proyecto son:

```text
pygame==2.6.1
pytmx==3.32
```

---

# Ejecución

Una vez instalado el proyecto y activado el entorno virtual, ejecutar:

```bash
python main.py
```

El juego iniciará mostrando el menú principal.

Desde el menú se puede acceder a las diferentes opciones disponibles y comenzar una partida.

---

# Controles

| Tecla             | Acción                   |
| ----------------- | ------------------------ |
| `W`               | Mover hacia arriba       |
| `A`               | Mover hacia la izquierda |
| `S`               | Mover hacia abajo        |
| `D`               | Mover hacia la derecha   |
| `Mouse`           | Apuntar                  |
| `Click izquierdo` | Atacar / disparar        |
| `Espacio`         | Esquivar                 |
| `ESC`             | Pausar / abrir menú      |

Los controles se encuentran centralizados mediante el patrón **Command**, permitiendo separar las acciones del juego de la entrada del usuario.

---

# 📸 Capturas

A continuación se presentan algunas capturas del videojuego.

### Menú principal
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/15cc938f-6cc4-43f2-a460-3135d5bdfbcf" />



### Gameplay


<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/77e8e902-5e33-4188-af7b-855839f6a5b7" />



#Patrones de diseño

El proyecto utiliza diferentes patrones de diseño para organizar la arquitectura del videojuego.

Los patrones se encuentran organizados dentro de la carpeta:

```text
patterns/
```

---

## Command

Ubicación:

```text
patterns/command/
```

El patrón **Command** se utiliza para encapsular las acciones que puede realizar el jugador.

En el proyecto se encuentra implementado mediante:

```text
patterns/command/controls.py
```

Su objetivo es separar la entrada del usuario de la lógica que ejecuta cada acción.

Por ejemplo, una determinada tecla puede representar una acción como:

* Mover.
* Atacar.
* Esquivar.
* Pausar.

Esto permite modificar los controles sin tener que modificar directamente toda la lógica del jugador.

---

## Decorator

Ubicación:

```text
patterns/decorator/
```

Se utiliza para agregar funcionalidades o comportamientos adicionales a objetos existentes sin modificar directamente su estructura original.

En el proyecto se encuentra utilizado para implementar el efecto de **sangre**:

```text
patterns/decorator/blood.py
```

De esta manera se puede agregar el efecto visual al comportamiento de las entidades sin tener que modificar completamente su implementación original.

---

## Observer

Ubicación:

```text
patterns/observer/
```

El patrón **Observer** permite que determinados objetos sean notificados cuando ocurre un cambio en otro objeto.

En el proyecto se utiliza para elementos de la interfaz como:

```text
patterns/observer/hud.py
patterns/observer/skill_board.py
```

Esto permite mantener actualizados elementos de la interfaz cuando cambia información del jugador, como su estado o habilidades.

---

## State

Ubicación:

```text
patterns/state/
```

El patrón **State** permite representar diferentes estados del videojuego y cambiar entre ellos.

El proyecto cuenta con estados como:

```text
menu_state.py
options_state.py
playing_state.py
```

Esto permite separar claramente situaciones como:

* Menú principal.
* Opciones.
* Partida.

De esta manera cada estado puede tener su propia lógica de actualización, eventos y renderizado.

---

## Strategy

Ubicación:

```text
patterns/strategy/
```

El patrón **Strategy** permite encapsular diferentes comportamientos que pueden intercambiarse de manera independiente.

En el proyecto se utiliza para diferentes comportamientos relacionados con:

* Movimiento.
* Cámara.
* Animaciones.
* Apuntar.
* Rotación.
* Efectos.

Algunos de los archivos implementados son:

```text
movement.py
camera.py
animator.py
animationPlayer.py
aim.py
rotator.py
effects.py
```

Esto permite modificar el comportamiento de una entidad sin tener que modificar toda la clase principal.

---

## Repository

Ubicación:

```text
patterns/repository/
```

El patrón **Repository** permite separar la lógica de acceso a los datos de la lógica principal del videojuego.

Esto facilita trabajar con la información almacenada en la base de datos sin mezclar las consultas SQL con la lógica de las entidades y del juego.

---

## Singleton

Ubicación:

```text
patterns/singleton/
```

El patrón **Singleton** permite garantizar que determinada clase tenga una única instancia compartida durante la ejecución del programa.

Es útil para componentes que necesitan ser accesibles desde diferentes partes del videojuego sin crear múltiples instancias innecesarias.

---

## Factory

Ubicación:

```text
patterns/factory/
```

El patrón **Factory** permite centralizar la creación de determinados objetos, evitando que el código que los utiliza tenga que conocer todos los detalles de su construcción.

Este enfoque facilita la creación y administración de diferentes tipos de objetos dentro del videojuego.

---

#Base de datos

El proyecto utiliza una base de datos para almacenar información relacionada con los jugadores y sus puntuaciones.

La estructura de acceso a los datos se encuentra organizada dentro de:

```text
database/
```

Entre los archivos principales se encuentran:

```text
database/
├── connection.py
├── config_repository.py
├── player_repository.py
└── score_repository.py
```

Además, el proyecto cuenta con:

```text
database.sql
seed.sql
```

---

## Conexión

El archivo:

```text
database/connection.py
```

se encarga de establecer la conexión con la base de datos.

De esta manera, el resto de la aplicación puede utilizar una conexión centralizada para realizar las operaciones necesarias.

---

## Repositorios

Se utilizan repositorios para separar las operaciones relacionadas con los datos.

### Player Repository

```text
player_repository.py
```

Se encarga de las operaciones relacionadas con los jugadores.

### Score Repository

```text
score_repository.py
```

Se encarga de gestionar las puntuaciones obtenidas durante las partidas.

### Config Repository

```text
config_repository.py
```

Se utiliza para gestionar información relacionada con la configuración almacenada.

---

## Base de datos y puntuaciones

La base de datos permite mantener información persistente del jugador y sus puntuaciones.

El flujo general es:

```text
Jugador
   ↓
Juego
   ↓
Score Manager
   ↓
Score Repository
   ↓
Base de datos
```

De esta forma, la lógica del juego no necesita encargarse directamente de las consultas SQL.

---

# Aportes de los integrantes

## Adriano Oyola

* Desarrollo del menú principal.
* Desarrollo de la interfaz.
* Desarrollo del menú de opciones.
* Desarrollo de elementos de UI.
* Implementación del spawn de enemigos.
* Integración de los diferentes elementos de interfaz con el juego.

## Lautaro Tonini

* Implementación del sistema de animaciones.
* Desarrollo del sistema de sonido.
* Implementación del movimiento de cámara.
* Desarrollo del sistema de efectos de sangre.
* Implementación de la máquina de estados.
* Integración de estados y comportamientos del juego.

## Fabrizio Rossato

* Diseño general del videojuego.
* Diseño de elementos visuales.
* Diseño de animaciones.
* Desarrollo de la historia.
* Aporte a la ambientación y estética general del proyecto.

## Gregorio Bizzotto

* Implementación del sistema de vida.
* Implementación del sistema de aguante.
* Desarrollo del sistema de enemigos.
* Desarrollo del sistema de balas.
* Implementación de la inteligencia artificial de los enemigos.
* Desarrollo de comportamientos de los enemigos.
* Integración de los sistemas relacionados con el combate.

---

#Trabajo grupal

Durante el desarrollo del proyecto se trabajó de manera colaborativa en:

* Diseño y planificación del videojuego.
* Desarrollo de la historia.
* Diseño de personajes y escenarios.
* Desarrollo de las diferentes mecánicas.
* Integración de sistemas.
* Implementación de patrones de diseño.
* Pruebas y corrección de errores.
* Organización del código.
* Uso de Git y GitHub.
* Integración de las diferentes ramas.
* Pruebas finales del videojuego.

---

#Estructura general

```text
Damn Beast/
│
├── assets/
│   ├── fonts/
│   ├── images/
│   ├── maps/
│   ├── sounds/
│   └── ui/
│
├── core/
│   ├── event_manager.py
│   ├── game.py
│   └── state_manager.py
│
├── database/
│   ├── connection.py
│   ├── config_repository.py
│   ├── player_repository.py
│   └── score_repository.py
│
├── entities/
│   ├── player.py
│   ├── enemy.py
│   ├── bullet.py
│   ├── enemy_bullet.py
│   ├── ranged_enemy.py
│   └── enemy_manager.py
│
├── managers/
│   ├── level_manager.py
│   ├── score_manager.py
│   └── sound_manager.py
│
├── patterns/
│   ├── command/
│   ├── decorator/
│   ├── factory/
│   ├── observer/
│   ├── repository/
│   ├── singleton/
│   ├── state/
│   └── strategy/
│
├── ui/
│   ├── menu.py
│   ├── options.py
│   └── pause.py
│
├── world/
│   ├── collision.py
│   ├── collisionmap.py
│   ├── level.py
│   └── tilemap.py
│
├── database.sql
├── seed.sql
├── main.py
├── config.py
└── requirements.txt
```

---

# Repositorio

El código fuente del proyecto se encuentra disponible en GitHub:

https://github.com/adrianoop03/blood_proyect

---

## Estado del proyecto

**Damn Beast** fue desarrollado como un proyecto académico grupal, integrando programación en Python, desarrollo de videojuegos con Pygame, gestión de datos, inteligencia artificial, interfaces, animaciones y patrones de diseño.

El proyecto busca combinar una experiencia de acción 2D con una ambientación propia y una estructura de código modular que permita continuar ampliando el videojuego.

