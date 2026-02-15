#!/usr/bin/env python3
"""
CaptScreen - Простая программа записи экрана для Windows
Запись: нажмите Enter для старта/остановки
Таймер: укажите длительность в минутах при запуске (0 = без ограничений)
"""

import cv2
import mss
import numpy as np
import time
import threading
import sys
from datetime import datetime

class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.paused = False
        self.writer = None
        self.start_time = None
        self.duration = 0  # в секундах, 0 = без ограничений
        self.output_file = None
        
    def get_output_filename(self):
        """Генерирует имя файла на основе текущего времени"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"recording_{timestamp}.mp4"
    
    def start_recording(self, duration_minutes=0):
        """Начинает запись экрана"""
        if self.recording:
            print("Запись уже идет!")
            return
            
        self.duration = duration_minutes * 60 if duration_minutes > 0 else 0
        self.output_file = self.get_output_filename()
        
        # Получаем размеры экрана
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Основной монитор
            self.width = monitor["width"]
            self.height = monitor["height"]
        
        # Создаем видео writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(
            self.output_file, 
            fourcc, 
            20.0,  # FPS
            (self.width, self.height)
        )
        
        self.recording = True
        self.start_time = time.time()
        
        print(f"\n{'='*50}")
        print(f"НАЧАЛО ЗАПИСИ: {self.output_file}")
        if self.duration > 0:
            print(f"Длительность: {duration_minutes} минут(ы)")
            print(f"Окончание в: {datetime.fromtimestamp(self.start_time + self.duration).strftime('%H:%M:%S')}")
        else:
            print("Нажмите Enter для остановки записи")
        print(f"{'='*50}\n")
        
        # Запускаем запись в отдельном потоке
        record_thread = threading.Thread(target=self._record_loop)
        record_thread.daemon = True
        record_thread.start()
        
    def _record_loop(self):
        """Основной цикл захвата экрана"""
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            
            while self.recording:
                # Проверяем таймер
                if self.duration > 0:
                    elapsed = time.time() - self.start_time
                    if elapsed >= self.duration:
                        print(f"\nТаймер истек! Запись остановлена.")
                        self.stop_recording()
                        break
                
                # Захватываем кадр
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                
                # Конвертируем BGRA -> BGR для OpenCV
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Записываем кадр
                if self.writer is not None:
                    self.writer.write(frame)
                
                # Показываем время записи
                if self.duration > 0:
                    remaining = self.duration - (time.time() - self.start_time)
                    mins, secs = divmod(int(remaining), 60)
                    print(f"\rОсталось: {mins:02d}:{secs:02d}", end="", flush=True)
                else:
                    elapsed = time.time() - self.start_time
                    mins, secs = divmod(int(elapsed), 60)
                    print(f"\rЗапись: {mins:02d}:{secs:02d}", end="", flush=True)
                
                # Небольшая задержка для стабильности
                time.sleep(0.05)
    
    def stop_recording(self):
        """Останавливает запись"""
        if not self.recording:
            return
            
        self.recording = False
        
        if self.writer:
            self.writer.release()
            self.writer = None
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        mins, secs = divmod(int(elapsed), 60)
        
        print(f"\n\n{'='*50}")
        print(f"ЗАПИСЬ ОСТАНОВЛЕНА")
        print(f"Файл: {self.output_file}")
        print(f"Длительность: {mins:02d}:{secs:02d}")
        print(f"{'='*50}\n")


def main():
    print("\n" + "="*50)
    print("   CaptCam - Запись экрана")
    print("="*50)
    
    recorder = ScreenRecorder()
    
    # Запрашиваем длительность
    print("\nВведите длительность записи в минутах (0 = без ограничений):")
    try:
        duration_input = input(">>> ").strip()
        duration = int(duration_input) if duration_input else 0
    except ValueError:
        duration = 0
        print("Неверный ввод, запись без ограничений по времени")
    
    print("\nНажмите Enter для начала записи...")
    input()
    
    recorder.start_recording(duration)
    
    # Ждем Enter для остановки (если нет таймера)
    if duration == 0:
        input()  # Ждем нажатия Enter
        recorder.stop_recording()
    else:
        # Ждем пока запись не закончится по таймеру
        while recorder.recording:
            time.sleep(0.1)
    
    print("\nНажмите Enter для выхода...")
    input()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")