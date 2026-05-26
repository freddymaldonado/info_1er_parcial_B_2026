import arcade
import json
from tool import EraserTool, MarkerTool, PencilTool, SprayTool

WIDTH = 800
HEIGHT = 600
TITLE = "Paint - Freddy Maldonado Pereyra - 1er Parcial Infografía"
TOOLBAR_HEIGHT = 70
TOOLBAR_COLOR = (230, 230, 230)
BUTTON_COLOR = (245, 245, 245)
SELECTED_BUTTON_COLOR = (180, 220, 255)

COLORS = {
    "black": arcade.color.BLACK,
    "red": arcade.color.RED,
    "blue": arcade.color.BLUE,
    "yellow": arcade.color.YELLOW,
    "green": arcade.color.GREEN,
}


class Paint(arcade.View):
    def __init__(self, load_path: str | None = None):
        super().__init__()
        self.background_color = arcade.color.WHITE
        self.tool = PencilTool()
        # Guardo las herramientas usadas para poder dibujar trazos de cada tipo.
        self.used_tools = {
            self.tool.name: self.tool,
            "MARKER": MarkerTool(),
            "SPRAY": SprayTool(),
            "ERASER": EraserTool(),
        }
        self.color = arcade.color.BLUE
        # Los botones son diccionarios simples con posicion y accion.
        self.buttons = []
        self.create_buttons()

        if load_path is not None:
            # Debe leer `load_path` y poblar self.traces con la lista de
            # trazos guardada. Decida el formato (JSON recomendado).
            file = open(load_path, "r")
            text = file.read()
            file.close()
            loaded_traces = json.loads(text)
            self.traces = []
            for trace in loaded_traces:
                # JSON guarda tuplas como listas, por eso reconstruyo los puntos.
                points = []
                for point in trace["trace"]:
                    points.append((point[0], point[1]))
                color = tuple(trace["color"])
                self.traces.append({"tool": trace["tool"], "color": color, "trace": points})
        else:
            self.traces = []

    def add_button(self, kind: str, value, text: str, left: int, width: int, color=None):
        right = left + width
        bottom = HEIGHT - 55
        top = HEIGHT - 12
        self.buttons.append({"kind": kind, "value": value, "text": text, "left": left, "right": right, "bottom": bottom, "top": top, "color": color})

    def create_buttons(self):
        # Creo la barra de botones de izquierda a derecha.
        x = 10
        gap = 8
        self.add_button("tool", "PENCIL", "LAPIZ", x, 66)
        x += 66 + gap
        self.add_button("tool", "MARKER", "MARCA", x, 66)
        x += 66 + gap
        self.add_button("tool", "SPRAY", "SPRAY", x, 66)
        x += 66 + gap
        self.add_button("tool", "ERASER", "BORRA", x, 66)
        x += 66 + gap + 8
        self.add_button("color", COLORS["black"], "", x, 32, COLORS["black"])
        x += 32 + gap
        self.add_button("color", COLORS["red"], "", x, 32, COLORS["red"])
        x += 32 + gap
        self.add_button("color", COLORS["green"], "", x, 32, COLORS["green"])
        x += 32 + gap
        self.add_button("color", COLORS["blue"], "", x, 32, COLORS["blue"])
        x += 32 + gap
        self.add_button("color", COLORS["yellow"], "", x, 32, COLORS["yellow"])
        x += 32 + gap + 8
        self.add_button("action", "save", "GUARDA", x, 78)
        x += 78 + gap
        self.add_button("action", "undo", "DESH", x, 58)
        x += 58 + gap
        self.add_button("action", "clear", "LIMPIA", x, 70)

    def select_tool(self, tool_name: str):
        # Esto permite cambiar herramienta desde los botones de la interfaz.
        if tool_name == "PENCIL":
            self.tool = PencilTool()
        elif tool_name == "MARKER":
            self.tool = MarkerTool()
        elif tool_name == "SPRAY":
            self.tool = SprayTool()
        elif tool_name == "ERASER":
            self.tool = EraserTool()
        self.used_tools[self.tool.name] = self.tool

    def save_drawing(self):
        # Guardo la lista de trazos completa en un JSON sencillo.
        file_name = "dibujo_guardado.json"
        text = json.dumps(self.traces, indent=2)
        file = open(file_name, "w")
        file.write(text)
        file.close()
        print(f"dibujo guardado en {file_name}")

    def button_was_clicked(self, button: dict, x: int, y: int):
        return button["left"] <= x <= button["right"] and button["bottom"] <= y <= button["top"]

    def handle_button_click(self, x: int, y: int):
        # Si el click cae en un boton, ejecuto su accion y no dibujo en el lienzo.
        for button in self.buttons:
            if not self.button_was_clicked(button, x, y):
                continue
            if button["kind"] == "tool":
                self.select_tool(button["value"])
            elif button["kind"] == "color":
                self.color = button["value"]
            elif button["kind"] == "action":
                if button["value"] == "save":
                    self.save_drawing()
                elif button["value"] == "undo":
                    if len(self.traces) > 0:
                        self.traces.pop()
                elif button["value"] == "clear":
                    self.traces = []
            return True
        return False

    def draw_button_border(self, button: dict, thickness: int):
        # Dibujo el borde con cuatro lineas para mantenerlo simple.
        left = button["left"]
        right = button["right"]
        bottom = button["bottom"]
        top = button["top"]
        arcade.draw_line(left, bottom, right, bottom, arcade.color.BLACK, thickness)
        arcade.draw_line(left, top, right, top, arcade.color.BLACK, thickness)
        arcade.draw_line(left, bottom, left, top, arcade.color.BLACK, thickness)
        arcade.draw_line(right, bottom, right, top, arcade.color.BLACK, thickness)

    def draw_button(self, button: dict):
        # El boton activo se marca con otro color o con borde mas grueso.
        fill_color = BUTTON_COLOR
        border_thickness = 1
        if button["kind"] == "color":
            fill_color = button["color"]
            if self.color == button["value"]:
                border_thickness = 4
        elif button["kind"] == "tool":
            if self.tool.name == button["value"]:
                fill_color = SELECTED_BUTTON_COLOR
                border_thickness = 3
        arcade.draw_lrbt_rectangle_filled(button["left"], button["right"], button["bottom"], button["top"], fill_color)
        self.draw_button_border(button, border_thickness)
        if button["text"] != "":
            text_x = button["left"] + 6
            text_y = button["bottom"] + 15
            arcade.draw_text(button["text"], text_x, text_y, arcade.color.BLACK, 10)

    def draw_toolbar(self):
        # La barra se dibuja al final para quedar encima de los trazos.
        arcade.draw_lrbt_rectangle_filled(0, WIDTH, HEIGHT - TOOLBAR_HEIGHT, HEIGHT, TOOLBAR_COLOR)
        arcade.draw_line(0, HEIGHT - TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT, arcade.color.BLACK, 1)
        for button in self.buttons:
            self.draw_button(button)

    def on_key_press(self, symbol: int, modifiers: int):
        # Seleccion de herramientas con las teclas numericas
        if symbol == arcade.key.KEY_1:
            self.tool = PencilTool()
        elif symbol == arcade.key.KEY_2:
            self.tool = MarkerTool()
        elif symbol == arcade.key.KEY_3:
            self.tool = SprayTool()
        elif symbol == arcade.key.KEY_4:
            self.tool = EraserTool()
        # Seleccion de color con teclas asd
        elif symbol == arcade.key.A:
            self.color = arcade.color.RED
        elif symbol == arcade.key.S:
            self.color = arcade.color.GREEN
        elif symbol == arcade.key.D:
            self.color = arcade.color.BLUE
        elif symbol == arcade.key.O:
            # Debe serializar self.traces a un archivo de texto (JSON
            # recomendado) para que pueda recargarse luego.
            self.save_drawing()

        self.used_tools[self.tool.name] = self.tool

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.handle_button_click(x, y):
                return
            if y >= HEIGHT - TOOLBAR_HEIGHT:
                return
            if isinstance(self.tool, EraserTool):
                # El borrador modifica trazos existentes, no crea un trazo nuevo.
                self.traces = self.tool.erase(self.traces, x, y)
            else:
                self.traces.append({"tool": self.tool.name, "color": self.color, "trace": [(x, y)]})

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if y >= HEIGHT - TOOLBAR_HEIGHT:
            return
        if isinstance(self.tool, EraserTool):
            # Mientras se arrastra, el borrador sigue eliminando puntos cercanos.
            self.traces = self.tool.erase(self.traces, x, y)
        elif self.traces:
            self.traces[-1]["trace"].append((x, y))

    def on_draw(self):
        self.clear()
        for tool in self.used_tools.values():
            tool.draw_traces(self.traces)
        self.draw_toolbar()


if __name__ == "__main__":
    import sys
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    # Invocacion: python main.py [ruta/a/dibujo.json]
    if len(sys.argv) > 1:
        app = Paint(sys.argv[1])
    else:
        app = Paint()
    window.show_view(app)
    arcade.run()
