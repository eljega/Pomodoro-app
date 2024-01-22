import flet as ft
from datetime import datetime, timedelta
import threading
import time
from playsound import playsound

is_timer_running = False
def generate_time_options(interval=5):
    options = []
    for hour in range(24):
        for minute in range(0, 60, interval):
            options.append(f"{hour:02d}:{minute:02d}")
    return options

class PomodoroApp:
    def __init__(self, page):
        self.page = page

        # Establecer estilo general de la página
        self.page.update()  # Actualizar la página para aplicar estilos

        self.alarms = []  # Lista para almacenar las alarmas
        self.is_timer_running = False
        self.alarm_triggered = False
        self.alarms_view = ft.Column()

        # Establecer colores base
        base_color = "#16213E"
        text_color = "#F8F9F9"
        button_color = "#0F3460"
        input_bg_color = "#2E4053"

        # Configurar los controles
        self.task_name_input = ft.TextField(label="Nombre de la Tarea", width=300)
        self.task_name_input.bgcolor = input_bg_color
        self.task_name_input.color = text_color
        

        self.task_duration_input = self.create_duration_dropdown()

        self.timer_label = ft.Text(value="", size=30, color=text_color)
        self.status_label = ft.Text(value="", size=20, color=text_color)

        self.start_button = ft.ElevatedButton("Iniciar", on_click=self.on_start_button_click)
        self.start_button.bgcolor = button_color
        self.start_button.color = text_color

        self.alarm_title_input = ft.TextField(label="Título de la Alarma", width=300)
        self.alarm_title_input.bgcolor = input_bg_color
        self.alarm_title_input.color = text_color

        self.alarm_start_time_input, self.alarm_end_time_input = self.create_time_dropdowns()

        self.add_alarm_button = ft.ElevatedButton("Agregar Alarma", on_click=self.on_add_alarm_button_click)
        self.add_alarm_button.bgcolor = button_color
        self.add_alarm_button.color = text_color

        

    def create_duration_dropdown(self):
        duration_options = [
            "1 hr", "1 hr 30 min", "2 hr", "2 hr 30 min", "3 hr",
            # ... más opciones según sea necesario ...
        ]
        dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(text=option) for option in duration_options],
            label="Duración de la Tarea",
            width=150
        )
        dropdown.bgcolor = "#1A1A2E"
        dropdown.color = "#E5E5E5"
        return dropdown

    def create_time_dropdowns(self):
        time_options = generate_time_options()
        start_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(text=option) for option in time_options],
            label="Hora de inicio",
            width=150
        )
        end_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(text=option) for option in time_options],
            label="Hora de finalización",
            width=150
        )
        start_dropdown.bgcolor = "#1A1A2E"
        start_dropdown.color = "#E5E5E5"
        end_dropdown.bgcolor = "#1A1A2E"
        end_dropdown.color = "#E5E5E5"
        return start_dropdown, end_dropdown

    def play_sound(self, file_path):
        playsound(file_path)

    def convert_duration_to_hours(self, duration_str):
        try:
            if ':' in duration_str:
                hours, minutes = map(int, duration_str.split(':'))
                return hours + minutes / 60
            else:
                return float(duration_str)
        except ValueError:
            return None

    def update_timer_label(self, label, end_time):
        """ Actualiza el label con el tiempo restante. """
        while datetime.now() < end_time:
            time_left = end_time - datetime.now()
            minutes, seconds = divmod(time_left.seconds, 60)
            label.value = f"{minutes:02d}:{seconds:02d}"
            label.update()
            time.sleep(1)

    is_timer_running = False


    def display_alarms(self):
        # Limpia los controles actuales para evitar duplicados
        self.alarms_view.controls.clear()

        for title, start, end, _ in self.alarms:
            self.alarms_view.controls.append(ft.Text(value=f"{title}: {start.strftime('%H:%M')} - {end.strftime('%H:%M')}"))

        self.page.update()  # Esto actualizará la página con los controles recién modificados

    def pomodoro_timer(self, task_name, duration, timer_label, status_label, start_button):
        print(f"Iniciando Pomodoro para '{task_name}' con duración de {duration} horas.")
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration)
        pomodoro_duration = 0.10 / 60  # 25 minutos
        short_break = 0.5 / 60  # 5 minutos
        long_break = 0.7 / 60  # 15 minutos (ajustado de 25 minutos a 15 para pruebas)
        cycles = 0

        while datetime.now() < end_time:
            # Fase de Trabajo
            status_label.value = "Trabajo"
            status_label.update()
            self.play_sound("static/sounds/ding-idea-40142.mp3")
            self.update_timer_label(timer_label, datetime.now() + timedelta(minutes=pomodoro_duration * 60))
            cycles += 1

            if datetime.now() >= end_time:
                break

            # Fase de Descanso
            break_duration = long_break if cycles % 4 == 0 else short_break
            status_label.value = "Descanso Largo" if cycles % 4 == 0 else "Descanso Corto"
            status_label.update()
            self.play_sound("static/sounds/pop-39222.mp3")
            self.update_timer_label(timer_label, datetime.now() + timedelta(minutes=break_duration * 60))

        # Restablecer estado cuando el Pomodoro termine
        status_label.value = "Pomodoro Finalizado"
        timer_label.value = "00:00"
        status_label.update()
        timer_label.update()
        self.play_sound("static/sounds/transition-explosion-121425.mp3")
        self.is_timer_running = False
        start_button.enabled = True
        start_button.update()
        self.alarm_triggered = False

        # En tu función que maneja el evento del botón de inicio
    def on_start_button_click(self, e):
        task_name = self.task_name_input.value
        task_duration_str = self.task_duration_input.value  # Ahora es el valor seleccionado del Dropdown

        # Convertir la duración seleccionada a horas
        task_duration = self.convert_duration_selection_to_hours(task_duration_str)

        if task_duration is not None:
            self.start_pomodoro(task_name, task_duration, self.timer_label, self.status_label, self.start_button)
        else:
            print("Duración no válida")

    def convert_duration_selection_to_hours(self, duration_str):
        # Convierte la selección de duración (p. ej., "1 hr 30 min") a un valor decimal en horas
        parts = duration_str.split()
        if len(parts) == 2:  # p. ej., "30 min"
            return float(parts[0]) / 60
        elif len(parts) == 4:  # p. ej., "1 hr 30 min"
            return float(parts[0]) + (float(parts[2]) / 60)
        return None

    def check_alarms(self):
        while True:
            now = datetime.now().time()  # Obtener la hora actual como un objeto time
            for title, start, end, duration in self.alarms:
                # Comparar directamente los objetos time
                if start <= now < end and not self.alarm_triggered:
                    # Activar alarma solo si `is_timer_running` es False para evitar solapamientos
                    if not self.is_timer_running:
                        self.alarm_triggered = True
                        self.start_pomodoro(title, duration, self.timer_label, self.status_label, self.start_button)
            time.sleep(30)
    
    def start_pomodoro(self, task_name, task_duration, timer_label, status_label, start_button):
        if self.is_timer_running or task_duration <= 0:
            print("El temporizador ya está en curso o la duración no es válida.")
            return

        self.is_timer_running = True
        start_button.enabled = False
        self.alarm_triggered = False
        start_button.update()

        threading.Thread(target=self.pomodoro_timer, args=(task_name, task_duration, timer_label, status_label, start_button)).start()

    def add_alarm(self, title, start_time_str, end_time_str):
        now = datetime.now().time()  # Obtener solo la hora actual
        start_time = datetime.strptime(start_time_str, '%H:%M').time()  # Convertir a objeto time
        end_time = datetime.strptime(end_time_str, '%H:%M').time()  # Convertir a objeto time

        # Validar que la hora de inicio no haya pasado ya
        if start_time < now:
            print("Error: La hora de inicio ya pasó.")
            return

        for alarm in self.alarms:
            _, existing_start, existing_end, _ = alarm
            if start_time == existing_start:
                print("Error: Ya existe una alarma con la misma hora de inicio.")
                return

        if end_time <= start_time:
            print("Error: La hora de finalización debe ser después de la hora de inicio.")
            return

        # Calcular la duración en horas de forma manual
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        duration_hours = (end_minutes - start_minutes) / 60.0

        # Verificar si la nueva alarma se solapa con alguna existente
        for _, existing_start, existing_end, _ in self.alarms:
            if not (end_time <= existing_start or start_time >= existing_end):
                print("Error: La alarma se solapa con otra existente.")
                return

        self.alarms.append((title, start_time, end_time, duration_hours))
        self.display_alarms()

    def on_add_alarm_button_click(self, event):
        # Obtener el valor seleccionado de los Dropdowns para la hora de inicio y finalización
        start_time_str = self.alarm_start_time_input.value
        end_time_str = self.alarm_end_time_input.value

        # Obtener el título de la alarma del campo de texto
        alarm_title = self.alarm_title_input.value

        # Llamar a la función para agregar la alarma con los valores obtenidos
        self.add_alarm(alarm_title, start_time_str, end_time_str)

    def run(self):
        try:
            # Añade los controles uno por uno directamente a la página
            self.page.add(self.task_name_input)
            self.page.add(self.task_duration_input)
            self.page.add(self.start_button)
            self.page.add(self.timer_label)
            self.page.add(self.status_label)
            self.page.add(self.alarm_title_input)
            self.page.add(self.alarm_start_time_input)
            self.page.add(self.alarm_end_time_input)
            self.page.add(self.add_alarm_button)
            self.page.add(self.alarms_view)
            print("Todos los controles se han agregado a la página")

        except Exception as e:
            print(f"Error al agregar controles a la página: {e}")

        # Inicia el hilo para verificar las alarmas
        alarm_checker_thread = threading.Thread(target=self.check_alarms, daemon=True)
        alarm_checker_thread.start()

def main(page: ft.Page):
    app = PomodoroApp(page)
    app.run()

ft.app(target=main)