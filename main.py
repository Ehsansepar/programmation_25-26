# main.py
import pygame
import time
import random

from config import WIDTH, HEIGHT, FPS
from personnage import Personnage
from monstre import Monstre
from projectil import Projectil

pygame.init()
projectils = []


manger_monstre = 0
tuer_monstre = 0
vie_player = 100

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clean Game")

# background (optionnel)
try:
    bg = pygame.image.load("images/bg_main.png")
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
except Exception:
    bg = None

clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
exit_button_rect = pygame.Rect(WIDTH - 110, 10, 100, 40)

# player + boss
player = Personnage(10, 10, w=80, h=80)
boss = Monstre(200, 200, boss=True)

monsters = []
last_spawn = time.time()
SPAWN_INTERVAL = 1.0  # secondes

running = True
while running:
    now = time.time()

    # spawn simple monster periodically
    if now - last_spawn >= SPAWN_INTERVAL:
        x = random.randrange(0, WIDTH - 50)
        y = random.randrange(0, HEIGHT - 50)
        monsters.append(Monstre(x, y, boss=False))
        last_spawn = now

    # déplacer et nettoyer les projectiles hors écran
    for p in projectils[:]:
        p.move()
        if (p.position["x"] < 0 or p.position["x"] > WIDTH or 
            p.position["y"] < 0 or p.position["y"] > HEIGHT):
            projectils.remove(p)

    # input/events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if exit_button_rect.collidepoint(event.pos):
                running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z: player.direction["up"] = True
            if event.key == pygame.K_s: player.direction["down"] = True
            if event.key == pygame.K_q: player.direction["left"] = True
            if event.key == pygame.K_d: player.direction["right"] = True
            
            # tirer un projectil avec les flèches
            proj_dir = None
            if event.key == pygame.K_UP: proj_dir = "up"
            elif event.key == pygame.K_DOWN: proj_dir = "down"
            elif event.key == pygame.K_LEFT: proj_dir = "left"
            elif event.key == pygame.K_RIGHT: proj_dir = "right"
            
            if proj_dir:
                proj = Projectil(
                    player.position["x"] + player.dimension["w"] // 2,
                    player.position["y"] + player.dimension["h"] // 2,
                    width=50,
                    height=50,
                    color=(255, 255, 0)
                )
                proj.direction[proj_dir] = True
                projectils.append(proj)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_z: player.direction["up"] = False
            if event.key == pygame.K_s: player.direction["down"] = False
            if event.key == pygame.K_q: player.direction["left"] = False
            if event.key == pygame.K_d: player.direction["right"] = False
            if event.key in (pygame.K_END, pygame.K_DELETE): running = False


    # update
    player.move()
    for m in monsters:
        m.move()

    # collision projectile avec monstres
    for proj in list(projectils):
        for m in list(monsters):
            if m.is_boss:
                continue
            # vérifier si projectile touche monstre
            if (proj.position["x"] < m.position["x"] + m.w and
                proj.position["x"] + proj.dimension["w"] > m.position["x"] and
                proj.position["y"] < m.position["y"] + m.h and
                proj.position["y"] + proj.dimension["h"] > m.position["y"]):
                projectils.remove(proj)
                monsters.remove(m)
                tuer_monstre += 1
                screen.fill((0, 255, 0))  # flash verts
                pygame.display.flip()
                pygame.time.delay(100)
                break

    is_hit = False
    p_rect = player.get_rect()
    for m in list(monsters):  
        if m.is_boss:
            continue
        if p_rect.colliderect(m.get_rect()):
            is_hit = True
            monsters.remove(m)      # on enlève le monstre touché
            manger_monstre += 1     # on incrémente le compteur
            vie_player -= 20        # on perd 20 points de vie
            break

    # vérifier si le joueur est mort
    if vie_player <= 0:
        running = False

    # draw
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill((0, 0, 0))

    # si hit, on veut juste un écran rouge basique -> on remplit directement
    if is_hit:
        screen.fill((255, 0, 0))
    else:
        # dessine les sprites normalement
        screen.blit(player.image, (player.position["x"], player.position["y"]))
        screen.blit(boss.image, (boss.position["x"], boss.position["y"]))
        for m in monsters:
            screen.blit(m.image, (m.position["x"], m.position["y"]))
        for p in projectils:
            screen.blit(p.image, (p.position["x"], p.position["y"]))

    # afficher la vie et le nombre de tués
    # font = pygame.font.Font(None, 36)
    
    # Dessiner le bouton EXIT
    pygame.draw.rect(screen, (200, 0, 0), exit_button_rect)
    exit_surf = font.render("EXIT", True, (255, 255, 255))
    screen.blit(exit_surf, (exit_button_rect.x + 20, exit_button_rect.y + 10))

    vie_text = font.render(f"VIE: {vie_player}", True, (255, 0, 0))
    tuer_text = font.render(f"TUER: {tuer_monstre}", True, (255, 255, 255))
    screen.blit(vie_text, (10, 10))
    screen.blit(tuer_text, (10, 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
print(f"Tuer {tuer_monstre} monstres")
print(f"vous faite manger par {manger_monstre} monstres")
if vie_player <= 0:
    print("GAME OVER - Vous etes mort!")

if __name__ == "__main__":
    pass