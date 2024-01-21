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

    def add_alarm(self, title, start_time_str, end_time_str):
        start_time = datetime.strptime(start_time_str, '%H:%M')
        end_time = datetime.strptime(end_time_str, '%H:%M')
        self.alarms.append((title, start_time, end_time))
        self.display_alarms()  # Actualizar la lista de alarmas en la UI

    def display_alarms(self):
        # Función para mostrar las alarmas programadas en la UI
        alarms_view = ft.Column()
        for title, start, end in self.alarms:
            alarms_view.controls.append(ft.Text(value=f"{title}: {start.strftime('%H:%M')} - {end.strftime('%H:%M')}"))
        self.page.add(alarms_view)
        self.page.update()


    def pomodoro_timer(self, task_name, duration, timer_label, status_label, start_button):
        print(f"Iniciando Pomodoro para '{task_name}' con duración de {duration} horas.")
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration)
        pomodoro_duration = 0.30 # 25 minutos
        short_break = 0.15 # 5 minutos
        long_break = 0.12 # 25 minutos
        cycles = 0

        while datetime.now() < end_time:
            # Fase de Trabajo
            status_label.value = "Trabajo"
            status_label.update()
            self.play_sound("static\sounds\ding-idea-40142.mp3")
            self.update_timer_label(timer_label, datetime.now() + timedelta(minutes=pomodoro_duration))
            cycles += 1

            if datetime.now() >= end_time:
                break

            # Fase de Descanso
            if cycles % 4 == 0:
                status_label.value = "Descanso Largo"
                status_label.update()
                self.play_sound("static\sounds\pop-39222.mp3")
                self.update_timer_label(timer_label, datetime.now() + timedelta(minutes=long_break))
            else:
                status_label.value = "Descanso Corto"
                status_label.update()
                self.play_sound("static\sounds\surprise-sound-effect-99300.mp3")
                self.update_timer_label(timer_label, datetime.now() + timedelta(minutes=short_break))

        # Restablecer estado cuando el Pomodoro termine
        status_label.value = "Pomodoro Finalizado"
        timer_label.value = ""
        status_label.update()
        timer_label.update()
        self.play_sound("static\sounds\transition-explosion-121425.mp3")
        global is_timer_running
        is_timer_running = False
        start_button.enabled = True
        start_button.update()

    def start_pomodoro(self, e, task_name_input, task_duration_input, timer_label, status_label, start_button):
        global is_timer_running
        if self.is_timer_running:
            print("El temporizador ya está en curso.")
            return

        self.is_timer_running = True
        start_button.enabled = False
        start_button.update()

        task_name = task_name_input.value
        task_duration = self.convert_duration_to_hours(task_duration_input.value)
        if task_duration is None:
            self.page.controls[-1].value = "Por favor, ingrese una duración válida (ej. 1:30 o 1.5)."
            self.page.update()
            is_timer_running = False
            start_button.enabled = True
            start_button.update()
            return

        threading.Thread(target=self.pomodoro_timer, args=(task_name, task_duration, timer_label, status_label, start_button)).start()

    def check_alarms(self):
        while True:
            now = datetime.now()
            for title, start, end in self.alarms:
                if start <= now < end and not self.is_timer_running:
                    duration = (end - now).total_seconds() / 3600  # Duración en horas
                    print(f"Es hora de iniciar la alarma para: {title}")
                    self.start_pomodoro(title, duration, ...)  # Pasa aquí los labels y botones correspondientes
                    break  # Solo inicia una alarma a la vez
            time.sleep(60)  # Revisa cada minuto


    def add_alarm(self, title, start_time_str, end_time_str):
        start_time = datetime.strptime(start_time_str, '%H:%M')
        end_time = datetime.strptime(end_time_str, '%H:%M')
        # Verificar si la nueva alarma se solapa con alguna existente
        for _, existing_start, existing_end in self.alarms:
            if not (end_time <= existing_start or start_time >= existing_end):
                print("Error: La alarma se solapa con otra existente.")
                return  # No agregar la alarma y tal vez mostrar un mensaje de error en la UI
        self.alarms.append((title, start_time, end_time))
        self.display_alarms()


    def run(self):
        # Crear la interfaz de usuario aquí
        task_name_input = ft.TextField(label="Nombre de la Tarea", width=300)
        task_duration_input = ft.TextField(label="Duración de la Tarea (HH:MM o decimal)", width=300)
        timer_label = ft.Text(value="", size=30)
        status_label = ft.Text(value="", size=20)
        start_button = ft.ElevatedButton("Iniciar", on_click=lambda e: self.start_pomodoro(e, task_name_input, task_duration_input, timer_label, status_label, start_button))
        alarm_checker_thread = threading.Thread(target=self.check_alarms, daemon=True)
        alarm_checker_thread.start()

        alarm_title_input = ft.TextField(label="Título de la Alarma", width=300)
        alarm_start_input = ft.TextField(label="Hora de Inicio (HH:MM)", width=300)
        alarm_end_input = ft.TextField(label="Hora de Finalización (HH:MM)", width=300)
        add_alarm_button = ft.ElevatedButton("Agregar Alarma", on_click=lambda e: self.add_alarm(alarm_title_input.value, alarm_start_input.value, alarm_end_input.value))

        self.page.add(task_name_input, task_duration_input, start_button, timer_label, status_label, alarm_title_input, alarm_start_input, alarm_end_input, add_alarm_button)
        

def main(page: ft.Page):
    app = PomodoroApp(page)
    app.run()

# Esto inicia la aplicación y Flet manejará la creación de la instancia de Page y la pasará a tu función main.
ft.app(target=main)

