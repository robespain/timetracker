
import os
import json
import time
from datetime import datetime
from functools import partial
import threading
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from sheets_service import SheetsService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set window size for testing on desktop
Window.size = (360, 640)

class BreakTrackerApp(App):
    def build(self):
        # Initialize Google Sheets service
        try:
            self.sheets_service = SheetsService()
            print("Google Sheets service initialized successfully")
        except Exception as e:
            print(f"Failed to load Google Sheets services: {str(e)}")
            self.sheets_service = None
        
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # App title
        title = Label(
            text='Control de Horas de Descanso', 
            font_size=24, 
            size_hint=(1, 0.2)
        )
        self.main_layout.add_widget(title)
        
        # Timer display
        self.timer_display = Label(
            text='00:00:00',
            font_size=40,
            size_hint=(1, 0.3)
        )
        self.main_layout.add_widget(self.timer_display)
        
        # Buttons
        self.start_btn = Button(
            text='Empezar Descanso',
            size_hint=(1, 0.2),
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.start_btn.bind(on_release=self.start_break)
        self.main_layout.add_widget(self.start_btn)
        
        self.end_btn = Button(
            text='Terminar Descanso',
            size_hint=(1, 0.2),
            background_color=(0.9, 0.3, 0.3, 1)
        )
        self.end_btn.bind(on_release=self.show_reason_popup)
        self.end_btn.disabled = True
        self.main_layout.add_widget(self.end_btn)
        
        # Status message
        self.status_msg = Label(
            text='',
            size_hint=(1, 0.1)
        )
        self.main_layout.add_widget(self.status_msg)
        
        # Timer variables
        self.start_time = None
        self.timer_event = None
        
        return self.main_layout
    
    def start_break(self, instance):
        if not self.sheets_service:
            self.show_status('Error: Google Sheets service not available', 'error')
            return
        
        self.start_time = datetime.now()
        self.start_date_str = self.start_time.strftime('%d/%m/%Y')
        self.start_time_str = self.start_time.strftime('%H:%M:%S')
        
        # Start the timer
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        
        # Update UI
        self.start_btn.disabled = True
        self.end_btn.disabled = False
        self.show_status('Break started!', 'success')
    
    def update_timer(self, dt):
        if self.start_time:
            current_time = datetime.now()
            diff = current_time - self.start_time
            total_seconds = int(diff.total_seconds())
            
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            self.timer_display.text = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    
    def show_reason_popup(self, instance):
        # Create popup for entering break reason
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='Por favor, introduzca el motivo de su descanso:'))
        
        self.reason_input = TextInput(multiline=True, height=100)
        content.add_widget(self.reason_input)
        
        buttons = BoxLayout(size_hint=(1, 0.3), spacing=10)
        
        cancel_btn = Button(text='Cancelar')
        submit_btn = Button(text='Enviar')
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(submit_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title='Motivo de Descanso',
            content=content,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )
        
        cancel_btn.bind(on_release=popup.dismiss)
        submit_btn.bind(on_release=partial(self.end_break, popup))
        
        popup.open()
    
    def end_break(self, popup, instance):
        reason = self.reason_input.text.strip()
        
        if not reason:
            self.show_status('Por favor, introduce un motivo para el descanso', 'warning')
            return
        
        if not self.sheets_service:
            self.show_status('Error: Google Sheets service not available', 'error')
            popup.dismiss()
            return
        
        # Get current time for end time
        end_time = datetime.now()
        end_time_str = end_time.strftime('%H:%M:%S')
        
        # Log to Google Sheets in a separate thread to avoid blocking UI
        threading.Thread(
            target=self.log_break_to_sheets,
            args=(self.start_date_str, self.start_time_str, end_time_str, reason)
        ).start()
        
        # Stop timer and reset UI
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        
        self.timer_display.text = '00:00:00'
        self.start_btn.disabled = False
        self.end_btn.disabled = True
        self.show_status('Procesando registro de descanso...', 'info')
        
        popup.dismiss()
    
    def log_break_to_sheets(self, date, start_time, end_time, reason):
        try:
            self.sheets_service.log_break(
                date=date,
                start_time=start_time,
                end_time=end_time,
                reason=reason
            )
            # Use Clock.schedule_once to update UI from the main thread
            Clock.schedule_once(lambda dt: self.show_status('¡Hora de descanso logueada con exito!', 'success'), 0)
        except Exception as e:
            print(f"Error logging break: {str(e)}")
            Clock.schedule_once(lambda dt: self.show_status(f'Error: {str(e)}', 'error'), 0)
    
    def show_status(self, message, status_type):
        self.status_msg.text = message
        if status_type == 'success':
            self.status_msg.color = (0, 1, 0, 1)  # Green
        elif status_type == 'error':
            self.status_msg.color = (1, 0, 0, 1)  # Red
        elif status_type == 'warning':
            self.status_msg.color = (1, 0.8, 0, 1)  # Orange
        else:
            self.status_msg.color = (0, 0.7, 1, 1)  # Blue for info

if __name__ == '__main__':
    BreakTrackerApp().run())
