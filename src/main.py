"""
BLOB BOOT FASHION JUDGE — Main 2D Game Loop
Run from project root via: python src/main.py
"""

import math
import os
import random
import sys
import pygame

# Ensure local imports inside src/ work regardless of working directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from config import SKIN_TONES, BOOT_TYPES, BOOT_COLORS, STICKY_MATERIALS, QUESTIONS
from audio import Jukebox, load_game_sfx, generate_pop_sound, _resolve_assets_dir
from renderer import DynamicBlobFoot
from judge import evaluate_fit


def _set_windows_app_id():
    """Tells Windows to give this game its own taskbar icon instead of Python's default icon."""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("BlobBoot.FashionJudge.2D.1")
        except Exception:
            pass


def _load_window_icon():
    """Finds and loads icon.ico (supports normal runs and PyInstaller --onefile bundles)."""
    project_root = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
    meipass = getattr(sys, "_MEIPASS", None)

    candidates = []
    if meipass:
        candidates.extend([
            os.path.join(meipass, "assets", "icon.ico"),
            os.path.join(meipass, "icon.ico"),
        ])

    candidates.extend([
        os.path.join(_resolve_assets_dir(), "icon.ico"),
        os.path.join(project_root, "icon.ico"),
        os.path.join(CURRENT_DIR, "icon.ico"),
    ])

    for path in candidates:
        if os.path.isfile(path):
            try:
                icon_surf = pygame.image.load(path)
                pygame.display.set_icon(icon_surf)
                return path
            except Exception as exc:
                print(f"[Window] Could not load icon '{path}': {exc}")
    return None


def draw_rounded_panel(surface, rect, bg_color, border_color=None, border_width=2, radius=18):
    pygame.draw.rect(surface, bg_color, rect, border_radius=radius)
    if border_color:
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)


def wrap_text(text, font, max_width):
    """Wraps a string into multiple lines to fit inside a UI panel."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def main():
    _set_windows_app_id()
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    _load_window_icon()

    WIDTH, HEIGHT = 1100, 680
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("BLOB BOOT FASHION JUDGE // 2D Edition")
    clock = pygame.time.Clock()

    # Load Fonts
    font_title = pygame.font.SysFont("segoeui", 30, bold=True)
    font_sub = pygame.font.SysFont("segoeui", 17)
    font_option = pygame.font.SysFont("segoeui", 26, bold=True)
    font_btn = pygame.font.SysFont("segoeui", 20, bold=True)
    font_tier = pygame.font.SysFont("segoeui", 32, bold=True)
    font_score = pygame.font.SysFont("segoeui", 46, bold=True)
    font_body = pygame.font.SysFont("segoeui", 19)

    # Load Custom SFX Assets from assets/ folder
    game_sfx = load_game_sfx()
    drumroll_snd = game_sfx.get("drumroll")
    cymbal_snd = game_sfx.get("cymbal")
    pop_snd = generate_pop_sound()

    # Start Background Jukebox (reads assets/music/, shuffles all songs before looping)
    jukebox = Jukebox(volume=0.25)
    jukebox.play_next()

    # Game State Variables
    state = "QUESTION"  # "QUESTION" -> "DRUMROLL" -> "RESULTS"
    current_step = 0
    selections = [0, 1, 0, 0]
    drumroll_timer = 0.0
    drumroll_duration = 2.45
    verdict_data = None

    blob_foot = DynamicBlobFoot()
    elapsed_time = 0.0

    # UI Button Rects
    btn_prev_opt = pygame.Rect(610, 310, 64, 64)
    btn_next_opt = pygame.Rect(976, 310, 64, 64)
    btn_back_step = pygame.Rect(610, 520, 160, 56)
    btn_confirm = pygame.Rect(790, 520, 250, 56)
    btn_play_again = pygame.Rect(660, 565, 320, 58)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        elapsed_time += dt
        jukebox.update()

        cur_skin = SKIN_TONES[selections[0]]
        cur_boot = BOOT_TYPES[selections[1]]
        cur_color = BOOT_COLORS[selections[2]]
        cur_sticky = STICKY_MATERIALS[selections[3]]
        is_barefoot = (cur_boot["name"] == "None (Barefoot)")

        blob_foot.update(dt, cur_boot["name"])

        def advance_step():
            nonlocal current_step, state, drumroll_timer, verdict_data
            if current_step == 1 and is_barefoot:
                # Skip Step 2 (Boot Color) when barefoot!
                current_step = 3
                blob_foot.trigger_contort_bounce()
                if pop_snd:
                    pop_snd.play()
            elif current_step < 3:
                current_step += 1
                blob_foot.trigger_contort_bounce()
                if pop_snd:
                    pop_snd.play()
            else:
                # Start Drumroll SFX
                state = "DRUMROLL"
                drumroll_timer = 0.0
                verdict_data = evaluate_fit(cur_skin, cur_boot, cur_color, cur_sticky)
                jukebox.set_ducked(True)
                if drumroll_snd:
                    drumroll_snd.play()

        def go_back_step():
            nonlocal current_step
            if current_step == 3 and is_barefoot:
                # Skip back over Boot Color directly to Boot Type
                current_step = 1
                blob_foot.trigger_contort_bounce()
                if pop_snd:
                    pop_snd.play()
            elif current_step > 0:
                current_step -= 1
                blob_foot.trigger_contort_bounce()
                if pop_snd:
                    pop_snd.play()

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_m:
                    jukebox.toggle_mute()
                elif event.key == pygame.K_n:
                    jukebox.play_next()
                elif state == "QUESTION":
                    opts_len = len(QUESTIONS[current_step]["options"])
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        selections[current_step] = (selections[current_step] - 1) % opts_len
                        blob_foot.trigger_contort_bounce()
                        if pop_snd:
                            pop_snd.play()
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        selections[current_step] = (selections[current_step] + 1) % opts_len
                        blob_foot.trigger_contort_bounce()
                        if pop_snd:
                            pop_snd.play()
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        advance_step()
                    elif event.key == pygame.K_BACKSPACE and current_step > 0:
                        go_back_step()

                elif state == "RESULTS":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                        state = "QUESTION"
                        current_step = 0
                        blob_foot.trigger_contort_bounce()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if state == "QUESTION":
                    opts_len = len(QUESTIONS[current_step]["options"])
                    if btn_prev_opt.collidepoint(mx, my):
                        selections[current_step] = (selections[current_step] - 1) % opts_len
                        blob_foot.trigger_contort_bounce()
                        if pop_snd:
                            pop_snd.play()
                    elif btn_next_opt.collidepoint(mx, my):
                        selections[current_step] = (selections[current_step] + 1) % opts_len
                        blob_foot.trigger_contort_bounce()
                        if pop_snd:
                            pop_snd.play()
                    elif btn_back_step.collidepoint(mx, my) and current_step > 0:
                        go_back_step()
                    elif btn_confirm.collidepoint(mx, my):
                        advance_step()

                elif state == "RESULTS":
                    if btn_play_again.collidepoint(mx, my):
                        state = "QUESTION"
                        current_step = 0
                        blob_foot.trigger_contort_bounce()
                        if pop_snd:
                            pop_snd.play()

        # --- STATE UPDATES ---
        shake_x, shake_y = 0, 0
        if state == "DRUMROLL":
            drumroll_timer += dt
            intensity = min(14.0, (drumroll_timer / drumroll_duration) * 14.0)
            shake_x = int(random.uniform(-intensity, intensity))
            shake_y = int(random.uniform(-intensity, intensity))
            
            if drumroll_timer >= drumroll_duration:
                state = "RESULTS"
                blob_foot.trigger_contort_bounce()
                jukebox.set_ducked(False)
                if cymbal_snd:
                    cymbal_snd.play()

        # ======================================================================
        # RENDERING
        # ======================================================================
        screen.fill((18, 20, 28))

        # Subtle Jukebox Status Bar at Top-Right
        if jukebox.status_note:
            jb_txt = font_sub.render(
                f"♪ JUKEBOX ERROR: {jukebox.status_note}",
                True, (245, 110, 110)
            )
        elif jukebox.tracks:
            status_prefix = "MUTED" if jukebox.muted else "♪ JUKEBOX"
            track_label = jukebox.current_track or "Loading..."
            jb_txt = font_sub.render(
                f"{status_prefix}: {track_label}   [N: Skip | M: Mute]",
                True, (145, 152, 175)
            )
        else:
            jb_txt = font_sub.render(
                f"♪ JUKEBOX: No supported tracks in {jukebox.music_dir}",
                True, (145, 152, 175)
            )
        screen.blit(jb_txt, (WIDTH - jb_txt.get_width() - 38, 10))

        # Left Runway Stage Panel
        stage_rect = pygame.Rect(36 + shake_x, 36 + shake_y, 520, 608)
        draw_rounded_panel(screen, stage_rect, (28, 31, 44), (62, 68, 92), 2, 24)

        # Runway Spotlight Pedestal
        pygame.draw.ellipse(screen, (42, 47, 66), (95 + shake_x, 495 + shake_y, 400, 74))
        pygame.draw.ellipse(screen, (212, 175, 55), (95 + shake_x, 495 + shake_y, 400, 74), 3)

        # Draw Live Contorting Blob Foot on Stage
        blob_foot.draw(
            screen,
            center_x=295 + shake_x,
            floor_y=520 + shake_y,
            skin=cur_skin,
            boot=cur_boot,
            color=cur_color,
            sticky=cur_sticky,
            time_sec=elapsed_time,
        )

        # Stage Caption Pill (omit boot color if barefoot)
        boot_label = "Barefoot" if is_barefoot else f"{cur_color['name']} {cur_boot['name']}"
        caption_txt = font_sub.render(
            f"{cur_skin['name']}  •  {boot_label}  •  {cur_sticky['name']}",
            True, (200, 205, 220)
        )
        screen.blit(caption_txt, (stage_rect.centerx - caption_txt.get_width() // 2, 595 + shake_y))

        # Right Interactive Panel
        right_rect = pygame.Rect(580, 36, 484, 608)
        draw_rounded_panel(screen, right_rect, (26, 29, 40), (58, 64, 86), 2, 24)

        # --- VIEW 1: ONE QUESTION AT A TIME ---
        if state == "QUESTION":
            q_info = QUESTIONS[current_step]
            options_list = q_info["options"]
            selected_item = options_list[selections[current_step]]

            # Dynamic step count (3 steps when barefoot, 4 steps with boots)
            visible_steps = [0, 1, 3] if is_barefoot else [0, 1, 2, 3]
            display_step_num = visible_steps.index(current_step) + 1
            total_steps_num = len(visible_steps)

            for idx_dot, step_id in enumerate(visible_steps):
                dot_col = (212, 175, 55) if step_id <= current_step else (60, 65, 85)
                pygame.draw.circle(screen, dot_col, (625 + idx_dot * 26, 75), 7)

            # Adjust step header dynamically when barefoot skips color
            raw_title = q_info["title"]
            if is_barefoot and current_step == 3:
                raw_title = "STEP 3 OF 3: CHOOSE STICKY MATERIAL"
            elif is_barefoot:
                raw_title = raw_title.replace("OF 4:", "OF 3:")

            title_lines = wrap_text(raw_title, font_title, 425)
            for idx, line in enumerate(title_lines):
                title_surf = font_title.render(line, True, (248, 245, 238))
                screen.blit(title_surf, (610, 96 + idx * 34))

            sub_start_y = 96 + len(title_lines) * 34 + 10
            sub_lines = wrap_text(q_info["subtitle"], font_sub, 425)
            for idx, line in enumerate(sub_lines):
                s_surf = font_sub.render(line, True, (165, 172, 192))
                screen.blit(s_surf, (610, sub_start_y + idx * 24))

            card_rect = pygame.Rect(610, 240, 430, 195)
            draw_rounded_panel(screen, card_rect, (36, 40, 56), (212, 175, 55), 2, 20)

            if "rgb" in selected_item and selected_item["name"] != "None (Clean)":
                swatch_col = selected_item["rgb"]
                pygame.draw.circle(screen, swatch_col, (card_rect.centerx, 282), 20)
                pygame.draw.circle(screen, (255, 255, 255), (card_rect.centerx, 282), 20, 2)

            opt_name_surf = font_option.render(selected_item["name"], True, (255, 255, 255))
            screen.blit(opt_name_surf, (card_rect.centerx - opt_name_surf.get_width() // 2, 326))

            idx_surf = font_sub.render(
                f"Option {selections[current_step] + 1} of {len(options_list)}   (Use ◄ / ► keys or click)",
                True, (155, 162, 185)
            )
            screen.blit(idx_surf, (card_rect.centerx - idx_surf.get_width() // 2, 382))

            draw_rounded_panel(screen, btn_prev_opt, (48, 53, 74), (110, 118, 150), 2, 14)
            draw_rounded_panel(screen, btn_next_opt, (48, 53, 74), (110, 118, 150), 2, 14)
            l_arr = font_option.render("◄", True, (255, 255, 255))
            r_arr = font_option.render("►", True, (255, 255, 255))
            screen.blit(l_arr, (btn_prev_opt.centerx - l_arr.get_width() // 2, btn_prev_opt.centery - l_arr.get_height() // 2))
            screen.blit(r_arr, (btn_next_opt.centerx - r_arr.get_width() // 2, btn_next_opt.centery - r_arr.get_height() // 2))

            if current_step > 0:
                draw_rounded_panel(screen, btn_back_step, (45, 50, 68), (95, 102, 130), 2, 14)
                b_txt = font_btn.render("← BACK", True, (220, 225, 238))
                screen.blit(b_txt, (btn_back_step.centerx - b_txt.get_width() // 2, btn_back_step.centery - b_txt.get_height() // 2))

            is_final_step = (display_step_num == total_steps_num)
            confirm_bg = (212, 175, 55) if is_final_step else (66, 135, 245)
            confirm_fg = (18, 20, 28) if is_final_step else (255, 255, 255)
            confirm_label = "JUDGE MY FIT! ★" if is_final_step else "NEXT QUESTION →"

            draw_rounded_panel(screen, btn_confirm, confirm_bg, None, 0, 14)
            c_txt = font_btn.render(confirm_label, True, confirm_fg)
            screen.blit(c_txt, (btn_confirm.centerx - c_txt.get_width() // 2, btn_confirm.centery - c_txt.get_height() // 2))

        # --- VIEW 2: DRUMROLL SUSPENSE SEQUENCE ---
        elif state == "DRUMROLL":
            pulse = 0.5 + 0.5 * math.sin(elapsed_time * 18.0)
            drum_col = (255, int(180 + 75 * pulse), 60)

            d_title = font_tier.render("DRUMROLL PLEASE...", True, drum_col)
            screen.blit(d_title, (right_rect.centerx - d_title.get_width() // 2, 230))

            d_sub = font_body.render("The Fashion Judge is calculating your fate...", True, (200, 205, 222))
            screen.blit(d_sub, (right_rect.centerx - d_sub.get_width() // 2, 290))

            bar_w = 380
            progress = min(1.0, drumroll_timer / drumroll_duration)
            pygame.draw.rect(screen, (45, 50, 68), (right_rect.centerx - bar_w // 2, 345, bar_w, 22), border_radius=11)
            pygame.draw.rect(screen, (212, 175, 55), (right_rect.centerx - bar_w // 2, 345, int(bar_w * progress), 22), border_radius=11)

        # --- VIEW 3: FINAL 4-40 TIER-LIST RESULTS ---
        elif state == "RESULTS" and verdict_data:
            breakdown, total_score, combo_name, tier_title, roast_text = verdict_data

            hdr_lines = wrap_text(f"COMBO: {combo_name.upper()}", font_sub, 425)
            for i, line in enumerate(hdr_lines[:2]):
                hdr = font_sub.render(line, True, (212, 175, 55))
                screen.blit(hdr, (610, 56 + i * 22))

            score_y = 56 + len(hdr_lines[:2]) * 22 + 4
            score_surf = font_score.render(f"{total_score} / 40", True, (255, 255, 255))
            screen.blit(score_surf, (610, score_y))

            tier_y = score_y + 56
            tier_lines = wrap_text(tier_title, font_btn, 425)
            for i, line in enumerate(tier_lines[:2]):
                t_surf = font_btn.render(line, True, (110, 235, 175))
                screen.blit(t_surf, (610, tier_y + i * 26))

            bar_start_y = 228
            for idx, (cat_name, pts) in enumerate(breakdown):
                row_y = bar_start_y + idx * 44
                lbl = font_sub.render(f"{cat_name}: {pts}/10", True, (220, 225, 238))
                screen.blit(lbl, (610, row_y))

                bar_bg = pygame.Rect(830, row_y + 4, 200, 14)
                bar_fg = pygame.Rect(830, row_y + 4, int(200 * (pts / 10.0)), 14)
                pygame.draw.rect(screen, (48, 53, 72), bar_bg, border_radius=7)
                pygame.draw.rect(screen, (212, 175, 55), bar_fg, border_radius=7)

            roast_box = pygame.Rect(610, 412, 425, 132)
            draw_rounded_panel(screen, roast_box, (36, 40, 56), (80, 88, 118), 1, 16)

            r_lines = wrap_text(f"\"{roast_text}\"", font_sub, 395)
            for i, line in enumerate(r_lines[:4]):
                r_surf = font_sub.render(line, True, (240, 242, 248))
                screen.blit(r_surf, (625, 426 + i * 26))

            draw_rounded_panel(screen, btn_play_again, (212, 175, 55), None, 0, 16)
            pa_txt = font_btn.render("BUILD ANOTHER FIT ↻", True, (18, 20, 28))
            screen.blit(pa_txt, (btn_play_again.centerx - pa_txt.get_width() // 2, btn_play_again.centery - pa_txt.get_height() // 2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()