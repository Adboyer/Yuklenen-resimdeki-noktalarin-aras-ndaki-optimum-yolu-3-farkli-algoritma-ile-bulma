# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 17:06:05 2024

@author: ASUS
"""

import pygame
import tkinter as tk
from tkinter import filedialog
import numpy as np
from collections import deque
import heapq
from PIL import Image
import pygame.surfarray


pygame.init()
pygame.font.init()
root = tk.Tk()
root.withdraw()


screen_width, screen_height = 1400, 700
button_width, button_height = 450, 55
button_color = (255, 255, 0)
button_hover_color = (255, 255, 150)  
button_text_color = (0, 0, 0)
background_color = (192, 192, 192)
grid_color = (0, 255, 255)
Kirmizi = (255, 0, 0, 80) 
Mavi = (0, 0, 128, 80)  
Sari = (255, 215, 0, 80)  


screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Labirent Oyunu")


font = pygame.font.Font(None, 40)

# Buton tanımlama
button1_rect = pygame.Rect(screen_width - button_width - 10, screen_height // 2 - button_height, button_width, button_height)
button1_text = font.render("Labirent Yükle", True, button_text_color)
button1_text_rect = button1_text.get_rect(center=button1_rect.center)

button4_rect = pygame.Rect(screen_width - button_width - 10, screen_height // 2 + 10, button_width, button_height)
button4_text = font.render("BFS Algoritması ile Çöz", True, button_text_color)
button4_text_rect = button4_text.get_rect(center=button4_rect.center)

button5_rect = pygame.Rect(screen_width - button_width - 10, screen_height // 2 + 70, button_width, button_height)
button5_text = font.render("Greedy BFS Algoritması ile Çöz", True, button_text_color)
button5_text_rect = button5_text.get_rect(center=button5_rect.center)

button6_rect = pygame.Rect(screen_width - button_width - 10, screen_height // 2 + 130, button_width, button_height)
button6_text = font.render("A* Algoritması ile Çöz", True, button_text_color)
button6_text_rect = button6_text.get_rect(center=button6_rect.center)


photo_rect = pygame.Rect(100, 200, 600, 400)
photo = None
show_grid = False
highlighted_squares_red = []
highlighted_squares_blue = []
highlighted_squares_black = []
path_squares = []
path_cost = 0

def buton_cız(button_rect, button_text, button_text_rect, hover=False):
    if hover:
        pygame.draw.rect(screen, button_hover_color, button_rect)
    else:
        pygame.draw.rect(screen, button_color, button_rect)
    screen.blit(button_text, button_text_rect)

def foto_yukle():
    global photo, show_grid, highlighted_squares_red, highlighted_squares_blue, highlighted_squares_black, path_squares, path_cost
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
    if file_path:
        try:
            print(f"Seçilen dosya yolu: {file_path}") 
            img = Image.open(file_path)
            img = img.resize((photo_rect.width, photo_rect.height))  
            photo = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
            show_grid = True
            highlighted_squares_red, highlighted_squares_blue, highlighted_squares_black = renk_degis()
            path_squares = []
            path_cost = 0
            print("Fotoğraf yüklendi.") 
        except Exception as e:
            print(f"Fotoğraf yüklenirken hata oluştu: {e}")

def ızgara_oluşturma():
    for x in range(photo_rect.left, photo_rect.right, 30):
        pygame.draw.line(screen, grid_color, (x, photo_rect.top), (x, photo_rect.bottom), 1)
    for y in range(photo_rect.top, photo_rect.bottom, 30):
        pygame.draw.line(screen, grid_color, (photo_rect.left, y), (photo_rect.right, y), 1)

def vurgulu_kareleri_ciz():
    for square in highlighted_squares_red:
        pygame.draw.rect(screen, Kirmizi, square)
    for square in highlighted_squares_blue:
        pygame.draw.rect(screen, Mavi, square)
    for square in highlighted_squares_black:
        pygame.draw.rect(screen, (0, 0, 0, 128), square)

def yol_kareleri_ciz():
    for square in path_squares:
        pygame.draw.rect(screen, Sari, square)

def renk_degis():
    global photo
    highlighted_squares_red = []
    highlighted_squares_blue = []
    highlighted_squares_black = []
    if photo:
        photo_array = pygame.surfarray.pixels3d(photo)
        red_color = np.array([255, 0, 0])
        blue_color = np.array([0, 0, 255])
        black_color = np.array([0, 0, 0])
        tolerance = 60

        
        mask_red = np.all(np.abs(photo_array - red_color) <= tolerance, axis=-1)
        mask_blue = np.all(np.abs(photo_array - blue_color) <= tolerance, axis=-1)
        mask_black = np.all(np.abs(photo_array - black_color) <= tolerance, axis=-1)

        for y in range(photo_rect.height):
            for x in range(photo_rect.width):
                if mask_red[x, y]:
                    grid_x = (x // 30) * 30
                    grid_y = (y // 30) * 30
                    highlighted_squares_red.append(pygame.Rect(photo_rect.left + grid_x, photo_rect.top + grid_y, 30,30))
                elif mask_blue[x, y]:
                    grid_x = (x // 30) * 30
                    grid_y = (y // 30) * 30
                    highlighted_squares_blue.append(pygame.Rect(photo_rect.left + grid_x, photo_rect.top + grid_y, 30, 30))
                elif mask_black[x, y]:
                    grid_x = (x // 30) * 30
                    grid_y = (y // 30) * 30
                    highlighted_squares_black.append(pygame.Rect(photo_rect.left + grid_x, photo_rect.top + grid_y, 30, 30))

        del photo_array  
    return highlighted_squares_red, highlighted_squares_blue, highlighted_squares_black

def bfs_yol():
    global path_squares, path_cost
    if not highlighted_squares_blue or not highlighted_squares_red:
        return

    start_square = highlighted_squares_blue[0]
    start_pos = (start_square.left, start_square.top)
    queue = deque([(start_pos, [])])
    visited = set()
    visited.add(start_pos)

    red_positions = {(square.left, square.top) for square in highlighted_squares_red}
    black_positions = {(square.left, square.top) for square in highlighted_squares_black}

    directions = [(-30, 0), (30, 0), (0, -30), (0, 30)]

    while queue:
        current_pos, path = queue.popleft()
        if current_pos in red_positions:
            path_squares = [pygame.Rect(x, y, 30, 30) for x, y in path]
            path_cost = len(path)
            for pos in path:
                path_squares.append(pygame.Rect(pos[0], pos[1], 30, 30))
            return

        for direction in directions:
            next_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
            if (next_pos not in visited and
                photo_rect.left <= next_pos[0] < photo_rect.right and
                photo_rect.top <= next_pos[1] < photo_rect.bottom and
                next_pos not in black_positions):
                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))
                # Uğranan her bir kareyi yol listesine ekleyelim
                path.append(next_pos)

def greedy_bfs_yol():
    global path_squares, path_cost
    if not highlighted_squares_blue or not highlighted_squares_red:
        return

    start_square = highlighted_squares_blue[0]
    start_pos = (start_square.left, start_square.top)
    end_square = highlighted_squares_red[0]
    end_pos = (end_square.left, end_square.top)
    
    def a_yıldız(pos):
        return abs(pos[0] - end_pos[0]) + abs(pos[1] - end_pos[1])

    priority_queue = []
    heapq.heappush(priority_queue, (a_yıldız(start_pos), start_pos, []))
    visited = set()
    visited.add(start_pos)
    black_positions = {(square.left, square.top) for square in highlighted_squares_black}
    directions = [(-30, 0), (30, 0), (0, -30), (0, 30)]

    while priority_queue:
        _, current_pos, path = heapq.heappop(priority_queue)
        if current_pos == end_pos:
            path_squares = [pygame.Rect(x, y, 30, 30) for x, y in path]
            path_cost = len(path)
            for pos in path:
                path_squares.append(pygame.Rect(pos[0], pos[1], 30, 30))
            return

        for direction in directions:
            next_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
            if (next_pos not in visited and
                photo_rect.left <= next_pos[0] < photo_rect.right and
                photo_rect.top <= next_pos[1] < photo_rect.bottom and
                next_pos not in black_positions):
                visited.add(next_pos)
                heapq.heappush(priority_queue, (a_yıldız(next_pos), next_pos, path + [next_pos]))
                path.append(next_pos)

def a_star_path():
    global path_squares, path_cost
    if not highlighted_squares_blue or not highlighted_squares_red:
        return
    start_square = highlighted_squares_blue[0]
    start_pos = (start_square.left, start_square.top)
    end_square = highlighted_squares_red[0]
    end_pos = (end_square.left, end_square.top)
    
    def a_yıldız(pos):
        return abs(pos[0] - end_pos[0]) + abs(pos[1] - end_pos[1])
    open_set = []
    heapq.heappush(open_set, (a_yıldız(start_pos), 0, start_pos, []))
    visited = set()
    visited.add(start_pos)
    path_squares = []
    black_positions = {(square.left, square.top) for square in highlighted_squares_black}
    directions = [(-30, 0), (30, 0), (0, -30), (0, 30)]
    while open_set:
        _, g_cost, current_pos, path = heapq.heappop(open_set)        
        if current_pos != start_pos and current_pos != end_pos:
            path_squares.append(pygame.Rect(current_pos[0], current_pos[1], 30, 30))
        if current_pos == end_pos:
            path_squares.extend([pygame.Rect(x, y, 30, 30) for x, y in path])
            path_cost = len(path)
            return
        for direction in directions:
            next_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
            new_g_cost = g_cost + 1  # Each move has a cost of 1
            if (next_pos not in visited and
                photo_rect.left <= next_pos[0] < photo_rect.right and
                photo_rect.top <= next_pos[1] < photo_rect.bottom and
                next_pos not in black_positions):
                visited.add(next_pos)
                f_cost = new_g_cost + a_yıldız(next_pos)
                heapq.heappush(open_set, (f_cost, new_g_cost, next_pos, path + [next_pos]))
running = True
while running:
    screen.fill(background_color)   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button1_rect.collidepoint(event.pos):
                foto_yukle()
            elif button4_rect.collidepoint(event.pos):
                bfs_yol()
            elif button5_rect.collidepoint(event.pos):
                greedy_bfs_yol()
            elif button6_rect.collidepoint(event.pos):
                a_star_path()
    buttons = [(button1_rect, button1_text, button1_text_rect),
               (button4_rect, button4_text, button4_text_rect),
               (button5_rect, button5_text, button5_text_rect),
               (button6_rect, button6_text, button6_text_rect)]
    for button_rect, button_text, button_text_rect in buttons:
        if button_rect.collidepoint(pygame.mouse.get_pos()):
            buton_cız(button_rect, button_text, button_text_rect, True)
        else:
            buton_cız(button_rect, button_text, button_text_rect)
    if photo:
        screen.blit(photo, photo_rect.topleft)
        if show_grid:
            ızgara_oluşturma()
            vurgulu_kareleri_ciz()
            yol_kareleri_ciz()           
            cost_text = font.render(f"Maliyet: {path_cost}", True, button_text_color)
            cost_text_rect = cost_text.get_rect()
            cost_text_rect.centerx = photo_rect.centerx
            cost_text_rect.y = photo_rect.bottom + 15  
            screen.blit(cost_text, cost_text_rect)

    pygame.display.flip()

pygame.quit()
