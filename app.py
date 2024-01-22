import flet as ft
from datetime import datetime, timedelta
import threading
import time
from playsound import playsound

is_timer_running = False

class PomodoroApp:
    def __init__(self, page):
        self.page = page
        self.alarms = []  # Lista para almacenar las alarmas
        self.is_timer_running = False
        self.task_name_input = ft.TextField(label="Nombre de la Tarea", width=300)
        self.task_duration_input = ft.TextField(label="Duración de la Tarea (HH:MM o decimal)", width=300)
        self.timer_label = ft.Text(value="", size=30)
        self.status_label = ft.Text(value="", size=20)
        self.start_button = ft.ElevatedButton("Iniciar", on_click=self.on_start_button_click)
        self.alarm_triggered = False
        self.alarms_view = ft.Column()

        self.alarm_title_input = ft.TextField(label="Título de la Alarma", width=300)
            # Crear las opciones para el Dropdown de hora
        hour_options = [ft.dropdown.Option(f"{i:02d}") for i in range(24)]
        self.alarm_hour_input = ft.Dropdown(options=hour_options, label="Hora de inicio", width=100)
        # Crear las opciones para el Dropdown de minutos
        minute_options = [ft.dropdown.Option(f"{i:02d}") for i in range(60)]
        self.alarm_minute_input = ft.Dropdown(options=minute_options, label="Minutos de inicio", width=100)
        # Similar para alarm_end_hour_input y alarm_end_minute_input
        self.alarm_end_hour_input = ft.Dropdown(options=hour_options, label="Hora de finalización", width=100)
        self.alarm_end_minute_input = ft.Dropdown(options=minute_options, label="Minutos de finalización", width=100)
        self.add_alarm_button = ft.ElevatedButton("Agregar Alarma", on_click=self.on_add_alarm_button_click)


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
        task_name = self.task_name_input.value  # Asegúrate de que task_name_input sea accesible en tu clase
        task_duration_str = self.task_duration_input.value  # Lo mismo para task_duration_input
        task_duration = self.convert_duration_to_hours(task_duration_str)
        if task_duration is not None:
            self.start_pomodoro(task_name, task_duration, self.timer_label, self.status_label, self.start_button)
        else:
            # Mostrar error de duración no válida
            print("Duración no válida")


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
            # Obtener los valores de los controles de entrada de la alarma
            title = self.alarm_title_input.value
            start_time_str = f"{self.alarm_hour_input.value}:{self.alarm_minute_input.value}"
            end_time_str = f"{self.alarm_end_hour_input.value}:{self.alarm_end_minute_input.value}"

            # Llamar a la función add_alarm con los valores obtenidos
            self.add_alarm(title, start_time_str, end_time_str)

    def run(self):
        # No necesitamos redefinir los controles aquí porque ya los definimos en __init__
        self.page.add(
        self.task_name_input,
        self.task_duration_input,
        self.start_button,
        self.timer_label,
        self.status_label,
        self.alarm_title_input,
        self.alarm_hour_input,
        self.alarm_minute_input,
        self.alarm_end_hour_input,
        self.alarm_end_minute_input,
        self.add_alarm_button,
        self.alarms_view
        )
        # Iniciar el hilo para verificar las alarmas
        alarm_checker_thread = threading.Thread(target=self.check_alarms, daemon=True)
        alarm_checker_thread.start()



def main(page: ft.Page):
    app = PomodoroApp(page)
    app.run()

ft.app(target=main)