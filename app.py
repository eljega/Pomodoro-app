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
        for title, start, end, _ in self.alarms:  # Añadido un cuarto elemento en la tupla para la duración
            alarms_view.controls.append(ft.Text(value=f"{title}: {start.strftime('%H:%M')} - {end.strftime('%H:%M')}"))
        self.page.add(alarms_view)
        self.page.update()



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
            now = datetime.now()
            for title, start, end, duration in self.alarms:
                if start.time() <= now.time() < end.time() and not self.alarm_triggered:
                    self.alarm_triggered = True
                    print(f"Alarma programada para '{title}' debería activarse ahora.")
                    self.start_pomodoro(title, duration, self.timer_label, self.status_label, self.start_button)
            time.sleep(30)  # Verificar las alarmas cada 30 segundos

    
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
        start_time = datetime.strptime(start_time_str, '%H:%M')
        end_time = datetime.strptime(end_time_str, '%H:%M')

        # Calcular la duración en horas
        duration = (end_time - start_time).total_seconds() / 3600

        # Verificar si la nueva alarma se solapa con alguna existente
        for _, existing_start, existing_end in self.alarms:
            if not (end_time <= existing_start or start_time >= existing_end):
                print("Error: La alarma se solapa con otra existente.")
                return  # No agregar la alarma

        self.alarms.append((title, start_time, end_time, duration))
        self.display_alarms()



    def run(self):
        alarm_title_input = ft.TextField(label="Título de la Alarma", width=300)
        alarm_start_input = ft.TextField(label="Hora de Inicio (HH:MM)", width=300)
        alarm_end_input = ft.TextField(label="Hora de Finalización (HH:MM)", width=300)
        add_alarm_button = ft.ElevatedButton("Agregar Alarma", on_click=lambda e: self.add_alarm(alarm_title_input.value, alarm_start_input.value, alarm_end_input.value))

        self.page.add(self.task_name_input, self.task_duration_input, self.start_button, self.timer_label, self.status_label, alarm_title_input, alarm_start_input, alarm_end_input, add_alarm_button)

        alarm_checker_thread = threading.Thread(target=self.check_alarms, daemon=True)
        alarm_checker_thread.start()
        if self.alarm_triggered:
            # Aquí asumimos que tienes una manera de obtener el nombre y la duración de la tarea activada por la alarma
            task_name = "Nombre de la tarea de la alarma"
            task_duration = 1  # Duración en horas, por ejemplo
            self.start_pomodoro(task_name, task_duration, self.timer_label, self.status_label, self.start_button)
            self.alarm_triggered = False


def main(page: ft.Page):
    app = PomodoroApp(page)
    app.run()

ft.app(target=main)

