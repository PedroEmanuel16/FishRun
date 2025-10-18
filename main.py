import math, random
WIDTH, HEIGHT, CELL_SIZE = 640, 480, 48
GRID_COLS, GRID_ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
STATE_MENU, STATE_GAME_OVER, STATE_PLAY = "menu", "gameOver", "play"

def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

class Button:
    def __init__(self, rect, text, callback):
        self.rect, self.text, self.callback, self.is_hovered = rect, text, callback, False
    def draw(self, surface):
        surface.draw.filled_rect(self.rect, (70 if self.is_hovered else 30, 144, 255))
        surface.draw.text(self.text, center=self.rect.center, fontsize=28, color="white")
    def update_hover(self, mouse_x, mouse_y): self.is_hovered = self.rect.collidepoint(mouse_x, mouse_y)
    def click(self):
        try:
            if music_enabled: 
                sounds.click.play()
        except:
            pass
        if callable(self.callback):
            self.callback()

class SpriteCharacter:
    def __init__(self, grid_x, grid_y, color):
        self.grid_x, self.grid_y, self.color = grid_x, grid_y, color
        self.x = self.grid_x * CELL_SIZE
        self.y = self.grid_y * CELL_SIZE
        self.target_x, self.target_y = self.x, self.y
        self.speed, self.health = 200, 3
        self.direction, self.animation_state = "down", "normal"
        self.animation_timer, self.animation_interval, self.animation_phase = 0, 0.4, False

    def get_sprite_name(self): return f"{self.color}_{self.direction}_{self.animation_state}"
    def is_moving(self): return abs(self.x - self.target_x) > 1 or abs(self.y - self.target_y) > 1

    def set_target_cell(self, grid_x, grid_y):
        self.grid_x, self.grid_y = clamp(grid_x, 0, GRID_COLS - 1), clamp(grid_y, 0, GRID_ROWS - 1)
        self.target_x, self.target_y = self.grid_x * CELL_SIZE, self.grid_y * CELL_SIZE

    def update(self, delta_time):
        delta_x, delta_y = self.target_x - self.x, self.target_y - self.y
        distance = math.hypot(delta_x, delta_y)
        if distance > 1:
            move_step = self.speed * delta_time
            move_ratio = min(1, move_step / distance)
            self.x += delta_x * move_ratio
            self.y += delta_y * move_ratio
            if abs(delta_x) > abs(delta_y):
                self.direction = "right" if delta_x > 0 else "left"
            else:
                self.direction = "down" if delta_y > 0 else "up"
        else:
            self.x, self.y = self.target_x, self.target_y

        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_interval:
            self.animation_timer = 0
            self.animation_phase = not self.animation_phase
            self.animation_state = "fishing" if self.animation_phase else "normal"

    def draw(self, surface): surface.blit(self.get_sprite_name(), (int(self.x), int(self.y)))

class Hero(SpriteCharacter):
    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, "blue")
        self.speed, self.score = 280, 0

class Enemy(SpriteCharacter):
    def __init__(self, grid_x, grid_y, patrol_radius=2):
        super().__init__(grid_x, grid_y, "red")
        self.center_x, self.center_y = grid_x, grid_y
        self.patrol_radius = patrol_radius
        self.move_timer = random.uniform(1, 2)
        self.behavior_state = "patrol"

    def update(self, delta_time, hero=None, occupied_cells=None):
        if hero:
            distance_to_hero = math.hypot(hero.x - self.x, hero.y - self.y)
            if distance_to_hero < CELL_SIZE * 2:
                self.behavior_state = "chase"
            elif distance_to_hero > CELL_SIZE * 3:
                self.behavior_state = "patrol"

        if self.behavior_state == "chase" and hero:
            target_x, target_y = int(hero.x // CELL_SIZE), int(hero.y // CELL_SIZE)
            if (target_x, target_y) not in occupied_cells:
                self.set_target_cell(target_x, target_y)
        else:
            self.move_timer -= delta_time
            if self.move_timer <= 0:
                self.move_timer = random.uniform(1, 2)
                for _ in range(10):
                    new_x = clamp(self.center_x + random.randint(-self.patrol_radius, self.patrol_radius), 0, GRID_COLS - 1)
                    new_y = clamp(self.center_y + random.randint(-self.patrol_radius, self.patrol_radius), 0, GRID_ROWS - 1)
                    if (new_x, new_y) not in occupied_cells:
                        self.set_target_cell(new_x, new_y)
                        break
        super().update(delta_time)

game_state, music_enabled, hero, enemy_list, button_list, last_delta = STATE_MENU, True, None, [], [], 0.016

def start_game():
    global game_state, hero, enemy_list
    hero = Hero(GRID_COLS // 2, GRID_ROWS // 2)
    enemy_list, occupied_cells = [], set()
    for _ in range(7):
        while True:
            grid_x, grid_y = random.randint(1, GRID_COLS - 2), random.randint(1, GRID_ROWS - 2)
            if (grid_x, grid_y) not in occupied_cells and math.hypot(grid_x - hero.grid_x, grid_y - hero.grid_y) >= 3:
                occupied_cells.add((grid_x, grid_y))
                enemy_list.append(Enemy(grid_x, grid_y))
                break
    game_state = STATE_PLAY
    try:
        if music_enabled: music.stop(); music.play("game")
    except: pass

def toggle_music():
    global music_enabled
    music_enabled = not music_enabled
    for button in button_list:
        if "Música e Sons:" in button.text:
            button.text = f"Música e Sons: {'Ativado' if music_enabled else 'Desativado'}"
    try: music.unpause() if music_enabled else music.pause()
    except: pass

def quit_game(): exit()

def make_game_over():
    global button_list
    button_list = [Button(Rect(WIDTH // 2 - 150, HEIGHT // 2 - 80, 300, 50), "Voltar ao Menu", back_to_menu)]

def make_menu():
    global button_list
    if music_enabled: music.play("menu")
    base_x, base_y, button_w, button_h, spacing = WIDTH // 2 - 150, HEIGHT // 2 - 80, 300, 50, 65
    button_list = [
        Button(Rect(base_x, base_y, button_w, button_h), "Começar Jogo", start_game),
        Button(Rect(base_x, base_y + spacing, button_w, button_h), f"Música e Sons: {'Ativado' if music_enabled else 'Desativado'}", toggle_music),
        Button(Rect(base_x, base_y + spacing * 2, button_w, button_h), "Sair", quit_game)
    ]
make_menu()

def back_to_menu(): make_menu(); globals()["game_state"] = STATE_MENU

def update(delta_time):
    global last_delta; last_delta = delta_time
    if game_state == STATE_PLAY:
        handle_input(); hero.update(delta_time)
        occupied_cells = {(int(enemy.grid_x), int(enemy.grid_y)) for enemy in enemy_list}
        for enemy in enemy_list: enemy.update(delta_time, hero, occupied_cells)
        check_collisions()

def handle_input():
    if hero.is_moving(): return
    grid_x, grid_y = hero.grid_x, hero.grid_y
    if keyboard.left: hero.set_target_cell(grid_x - 1, grid_y)
    elif keyboard.right: hero.set_target_cell(grid_x + 1, grid_y)
    elif keyboard.up: hero.set_target_cell(grid_x, grid_y - 1)
    elif keyboard.down: hero.set_target_cell(grid_x, grid_y + 1)

def check_collisions():
    hero_rect = Rect(int(hero.x) + 6, int(hero.y) + 6, CELL_SIZE - 12, CELL_SIZE - 12)
    for enemy in enemy_list:
        enemy_rect = Rect(int(enemy.x) + 6, int(enemy.y) + 6, CELL_SIZE - 12, CELL_SIZE - 12)
        if hero_rect.colliderect(enemy_rect):
            hero.health -= 1
            if hero.health <= 0:
                globals()["game_state"] = STATE_GAME_OVER; make_game_over()
                try:
                    if music_enabled:
                        music.stop(); 
                        music.play("game_over")
                except: pass
            break

def draw():
    screen.clear(); screen.blit("homebg", (0, 0))
    if game_state == STATE_MENU:
        screen.draw.text("FishRun", midtop=(WIDTH // 2, 40), fontsize=48, color="white")
        [button.draw(screen) for button in button_list]
        screen.draw.text("Use as teclas para se mover. Fuja dos peixinhos.", midbottom=(WIDTH // 2, HEIGHT - 29), fontsize=20, color="blue")
    elif game_state == STATE_GAME_OVER:
        screen.draw.text("Você Perdeu", midtop=(WIDTH // 2, 40), fontsize=48, color="white")
        [button.draw(screen) for button in button_list]
    else:
        screen.blit("gamebg", (0, 0))
        [enemy.draw(screen) for enemy in enemy_list]
        hero.draw(screen)

def on_mouse_down(pos):
    if game_state in (STATE_MENU, STATE_GAME_OVER):
        for button in button_list:
            if button.rect.collidepoint(pos): button.click()

def on_mouse_move(pos):
    if game_state == STATE_MENU:
        for button in button_list: button.update_hover(*pos)