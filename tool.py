import arcade
import math
import random
from typing import Protocol


class Tool(Protocol):
    """
    Protocolo que define las operaciones que una herramienta debe ofrecer.

    Cada herramienta concreta tiene un `name` unico que coincide con el
    valor "tool" de las entradas en la lista de trazos.
    """
    name: str

    def draw_traces(self, traces: list[dict]):
        ...

    def get_name(self):
        return self.name


class PencilTool(Tool):
    name = "PENCIL"

    def draw_traces(self, traces: list[dict]):
        for trace in traces:
            if trace["tool"] != self.name:
                continue
            # draw_line_strip requiere al menos 2 puntos
            if len(trace["trace"]) < 2:
                continue
            arcade.draw_line_strip(trace["trace"], trace["color"])


class MarkerTool(Tool):
    """
    Marcador. Similar al lapiz pero con un grosor mayor.

    El grosor debera ser un argumento al __init__ con un default razonable
    (por ejemplo 8 pixeles).

    Pista: arcade.draw_line_strip no soporta grosor directamente, pero
    `arcade.draw_lines` o `arcade.draw_line` si lo aceptan.
    """
    name = "MARKER"

    def __init__(self, thickness: int = 8):
        # El marcador usa un grosor mayor que el lapiz normal.
        self.thickness = thickness

    def draw_traces(self, traces: list[dict]):
        for trace in traces:
            if trace["tool"] != self.name:
                continue
            if len(trace["trace"]) < 2:
                continue
            points = trace["trace"]
            # Dibujo segmento por segmento porque draw_line permite grosor.
            for i in range(len(points) - 1):
                start = points[i]
                end = points[i + 1]
                arcade.draw_line(start[0], start[1], end[0], end[1], trace["color"], self.thickness)


class SprayTool(Tool):
    """
    Spray. En cada punto del trazo dibuja N pixeles dispersos
    aleatoriamente dentro de un radio.

    El numero de pixeles por punto y el radio deberan ser argumentos al
    __init__ con defaults razonables (por ejemplo 12 pixeles dentro de un
    radio de 10).

    Pista: usar `random.uniform` para dispersar dentro del radio y
    `arcade.draw_point` para dibujar cada pixel.
    """
    name = "SPRAY"

    def __init__(self, pixel_count: int = 12, radius: int = 10):
        # pixel_count controla cuantos puntitos salen por cada punto del trazo.
        self.pixel_count = pixel_count
        # radius controla que tan disperso se ve el spray.
        self.radius = radius

    def draw_traces(self, traces: list[dict]):
        for trace in traces:
            if trace["tool"] != self.name:
                continue
            for point in trace["trace"]:
                pixels_drawn = 0
                # Repito hasta conseguir puntitos que caigan dentro del radio.
                while pixels_drawn < self.pixel_count:
                    offset_x = random.uniform(-self.radius, self.radius)
                    offset_y = random.uniform(-self.radius, self.radius)
                    distance = math.sqrt(offset_x * offset_x + offset_y * offset_y)
                    if distance <= self.radius:
                        arcade.draw_point(point[0] + offset_x, point[1] + offset_y, trace["color"], 2)
                        pixels_drawn += 1


class EraserTool(Tool):
    """
    Borrador. NO es una herramienta que dibuje: su efecto es modificar la
    lista de trazos al pasar el cursor sobre ellos.

    Comportamiento esperado:
    - Mientras el usuario arrastra el cursor con esta herramienta
      seleccionada, los PUNTOS de cualquier trazo que esten dentro de
      `radius` pixeles del cursor deben eliminarse.
    - El borrador NO elimina trazos enteros: solo los puntos cercanos.
    - Cuidado: si se elimina un punto en medio de un trazo, dibujarlo
      como una sola line_strip va a unir los extremos restantes con una
      linea cruzada incorrecta. Decida como manejar esto (por ejemplo,
      dividiendo el trazo en dos al borrar puntos intermedios).
    - El borrador no tiene draw_traces propio (no se dibuja a si mismo),
      pero puede necesitar un metodo extra para procesar la lista de
      trazos. La firma de ese metodo y como se invoca desde main.py
      forma parte del ejercicio.
    """
    name = "ERASER"

    def __init__(self, radius: int = 18):
        # Este radio decide que puntos quedan suficientemente cerca para borrar.
        self.radius = radius

    def draw_traces(self, traces: list[dict]):
        pass

    def erase(self, traces: list[dict], x: int, y: int):
        # Armo una nueva lista para conservar solo las partes no borradas.
        new_traces = []
        for trace in traces:
            current_trace = []
            for point in trace["trace"]:
                dx = point[0] - x
                dy = point[1] - y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance <= self.radius:
                    if len(current_trace) > 0:
                        # Cierro este pedazo para que no se unan lineas por el hueco.
                        new_traces.append({"tool": trace["tool"], "color": trace["color"], "trace": current_trace})
                        current_trace = []
                else:
                    current_trace.append(point)
            if len(current_trace) > 0:
                # Guardo el ultimo pedazo que quedo despues de borrar.
                new_traces.append({"tool": trace["tool"], "color": trace["color"], "trace": current_trace})
        return new_traces
