"""
2D Procedural Blob Foot Renderer with Spring Physics & Live Contortion Morphing
"""

import math
import pygame


class DynamicBlobFoot:
    """
    Draws the cartoon blob leg & foot and smoothly contorts its geometry
    whenever boot type, skin tone, color, or sticky goo changes.
    """

    def __init__(self):
        self.leg_width = 112.0
        self.leg_top_y = 110.0
        self.foot_length = 245.0
        self.foot_height = 128.0
        self.toe_lift = 0.0
        self.sole_thickness = 0.0
        self.puffiness = 0.0

        # Squish/bounce spring animation
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.vel_x = 0.0
        self.vel_y = 0.0

    def trigger_contort_bounce(self):
        """Triggers an elastic squish-and-stretch impulse when an option changes."""
        self.scale_x = 1.16
        self.scale_y = 0.86

    def update(self, dt, boot_type_name):
        """Smoothly morphs foot proportions to contort to the selected boot."""
        targets = {
            "None (Barefoot)": (112.0, 115.0, 240.0, 125.0, 0.0, 0.0, 0.0),
            "Sneaker":         (114.0, 255.0, 262.0, 122.0, 6.0, 20.0, 4.0),
            "Hiking":          (120.0, 145.0, 260.0, 138.0, 4.0, 18.0, 8.0),
            "Chelsea":         (104.0, 125.0, 250.0, 120.0, 8.0, 10.0, -4.0),
            "Steel-Toe Work":  (124.0, 130.0, 272.0, 146.0, 0.0, 24.0, 12.0),
            "Combat":          (122.0, 95.0,  265.0, 142.0, 5.0, 24.0, 8.0),
            "Cowboy":          (110.0, 82.0,  295.0, 118.0, 26.0, 16.0, -2.0),
            "Go-Go Platform":  (108.0, 75.0,  255.0, 122.0, 10.0, 46.0, 2.0),
            "Fuzzy Yeti":      (148.0, 95.0,  290.0, 165.0, 0.0, 20.0, 24.0),
        }
        t_lw, t_lty, t_fl, t_fh, t_tl, t_st, t_pf = targets.get(
            boot_type_name, targets["None (Barefoot)"]
        )

        lerp_speed = min(1.0, dt * 12.0)
        self.leg_width += (t_lw - self.leg_width) * lerp_speed
        self.leg_top_y += (t_lty - self.leg_top_y) * lerp_speed
        self.foot_length += (t_fl - self.foot_length) * lerp_speed
        self.foot_height += (t_fh - self.foot_height) * lerp_speed
        self.toe_lift += (t_tl - self.toe_lift) * lerp_speed
        self.sole_thickness += (t_st - self.sole_thickness) * lerp_speed
        self.puffiness += (t_pf - self.puffiness) * lerp_speed

        stiffness = 180.0
        damping = 14.0
        force_x = (1.0 - self.scale_x) * stiffness
        force_y = (1.0 - self.scale_y) * stiffness
        self.vel_x = (self.vel_x + force_x * dt) * math.exp(-damping * dt)
        self.vel_y = (self.vel_y + force_y * dt) * math.exp(-damping * dt)
        self.scale_x += self.vel_x * dt
        self.scale_y += self.vel_y * dt

    def _cubic_bezier(self, p0, p1, p2, p3, steps=18):
        """Evaluates a smooth cubic Bezier curve between 4 control points."""
        pts = []
        for i in range(steps + 1):
            t = i / float(steps)
            u = 1.0 - t
            tt = t * t
            uu = u * u
            uuu = uu * u
            ttt = tt * t
            x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
            y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
            pts.append((x, y))
        return pts

    def _build_blob_polygon(self, cx, base_y, lw, top_y, fl, fh, toe_lift, puff):
        """
        Builds a smooth, hand-inked organic Bezier contour matching the
        chunky cartoon blob foot reference image.
        """
        left_x = cx - lw * 0.54
        right_leg_x = cx + lw * 0.46
        ankle_y = base_y - fh
        toe_x = left_x + fl + puff * 0.4

        # Key anchor points around the silhouette
        p_top_left = (left_x, top_y)
        p_top_right = (right_leg_x, top_y)
        p_ankle_start = (right_leg_x, ankle_y - 34.0)
        p_instep_mid = (right_leg_x + (toe_x - right_leg_x) * 0.48, ankle_y + 6.0 - toe_lift * 0.25)
        p_toe_tip = (toe_x, base_y - fh * 0.36 - toe_lift * 0.45)
        p_toe_bottom = (toe_x - 36.0, base_y - toe_lift * 0.15)
        p_heel_bottom = (left_x + 44.0, base_y)
        p_heel_back = (left_x - puff * 0.18, base_y - 48.0)

        pts = [p_top_left, p_top_right, p_ankle_start]

        # 1. Smooth concave ankle bend into top bridge of the foot
        pts.extend(self._cubic_bezier(
            p_ankle_start,
            (right_leg_x, ankle_y + 4.0),
            (right_leg_x + 14.0, ankle_y + 4.0),
            p_instep_mid,
            steps=16
        )[1:])

        # 2. Instep sloping smoothly into the plump rounded toe front
        pts.extend(self._cubic_bezier(
            p_instep_mid,
            (toe_x - 16.0, ankle_y + 8.0 - toe_lift * 0.45),
            (toe_x + 4.0, base_y - fh * 0.72 - toe_lift * 0.5),
            p_toe_tip,
            steps=18
        )[1:])

        # 3. Rounded front toe curving down onto the sole
        pts.extend(self._cubic_bezier(
            p_toe_tip,
            (toe_x + 2.0, base_y - 6.0 - toe_lift * 0.35),
            (toe_x - 14.0, base_y + 2.0 - toe_lift * 0.2),
            p_toe_bottom,
            steps=14
        )[1:])

        # 4. Gently arched cartoon sole from toe back to heel
        mid_sole_x = (p_toe_bottom[0] + p_heel_bottom[0]) * 0.5
        pts.extend(self._cubic_bezier(
            p_toe_bottom,
            (mid_sole_x + 25.0, base_y + 10.0),
            (mid_sole_x - 25.0, base_y + 10.0),
            p_heel_bottom,
            steps=16
        )[1:])

        # 5. Plump rounded heel curving up into the back of the leg
        pts.extend(self._cubic_bezier(
            p_heel_bottom,
            (left_x + 8.0, base_y + 2.0),
            (left_x - 6.0 - puff * 0.2, base_y - 16.0),
            p_heel_back,
            steps=14
        )[1:])

        # 6. Back of leg rising smoothly back to top-left
        pts.extend(self._cubic_bezier(
            p_heel_back,
            (left_x - puff * 0.1, ankle_y),
            (left_x, top_y + 40.0),
            p_top_left,
            steps=14
        )[1:])

        return pts

    def _draw_sole_and_heel(self, stage, cx, base_y, lw, fl, boot_name, toe_lift, sole_thick, outline_col, stroke):
        """Draws a distinct hand-inked outsole & heel block beneath the boot upper."""
        if sole_thick <= 2.0:
            return

        left_x = cx - lw * 0.54
        toe_x = left_x + fl
        st = max(10.0, sole_thick * 0.55)
        heel_h = st + (10.0 if boot_name in ("Cowboy", "Combat", "Hiking", "Steel-Toe Work") else 2.0)

        # Outsole silhouette following the bottom arch of the foot
        p_heel_top = (left_x + 6.0, base_y - 6.0)
        p_toe_top = (toe_x - 8.0, base_y - 6.0 - toe_lift * 0.22)
        p_toe_bot = (toe_x - 10.0, base_y + st - toe_lift * 0.22)
        p_arch_front = (left_x + fl * 0.44, base_y + st + 3.0)
        p_arch_back = (left_x + fl * 0.34, base_y + heel_h)
        p_heel_bot = (left_x + 12.0, base_y + heel_h)

        sole_pts = [p_heel_top]
        sole_pts.extend(self._cubic_bezier(
            p_heel_top,
            (left_x + fl * 0.35, base_y + 4.0),
            (left_x + fl * 0.65, base_y + 4.0),
            p_toe_top,
            steps=14
        )[1:])
        sole_pts.append(p_toe_bot)
        sole_pts.extend(self._cubic_bezier(
            p_toe_bot,
            (left_x + fl * 0.65, base_y + st + 4.0),
            (left_x + fl * 0.52, base_y + st + 3.0),
            p_arch_front,
            steps=10
        )[1:])
        sole_pts.extend([p_arch_back, p_heel_bot, p_heel_top])

        sole_fill = (36, 36, 42)
        if boot_name == "Cowboy":
            sole_fill = (68, 44, 30)
        elif boot_name == "Sneaker":
            sole_fill = (242, 244, 248)

        pygame.draw.polygon(stage, sole_fill, sole_pts)
        pygame.draw.polygon(stage, outline_col, sole_pts, stroke)

        # Foxing pinstripe on sneaker midsole
        if boot_name == "Sneaker":
            pygame.draw.line(
                stage, (60, 65, 80),
                (int(left_x + 12), int(base_y + st * 0.45)),
                (int(toe_x - 14), int(base_y + st * 0.45 - toe_lift * 0.2)),
                3
            )

        # Subtle tread notches along the bottom
        if boot_name in ("Combat", "Hiking", "Steel-Toe Work", "Sneaker"):
            for tx in range(int(left_x + fl * 0.48), int(toe_x - 24), 22):
                ty = int(base_y + st + 1)
                pygame.draw.line(stage, outline_col, (tx, ty - 4), (tx - 3, ty + 4), 4)

    def draw(self, target_surface, center_x, floor_y, skin, boot, color, sticky, time_sec):
        """Renders the contorting blob foot, tailored boot, and hand-inked sticky drips."""
        stage_w, stage_h = 520, 520
        stage = pygame.Surface((stage_w, stage_h), pygame.SRCALPHA)

        cx = 215
        base_y = 426 - self.sole_thickness * 0.35
        outline_col = (42, 34, 28)
        stroke = 7

        # 1. Ground contact shadow
        shadow_rect = pygame.Rect(int(cx - self.leg_width * 0.56), 448, int(self.foot_length * 1.06), 24)
        pygame.draw.ellipse(stage, (18, 20, 28, 125), shadow_rect)

        # 2. Bare Skin Blob Leg & Foot (always drawn underneath)
        skin_pts = self._build_blob_polygon(
            cx, base_y,
            self.leg_width, 72.0,
            self.foot_length, self.foot_height,
            self.toe_lift, self.puffiness
        )
        pygame.draw.polygon(stage, skin["rgb"], skin_pts)
        pygame.draw.polygon(stage, outline_col, skin_pts, stroke)

        boot_name = boot["name"]
        boot_col = color["rgb"]

        # 3. Tailored Hand-Drawn Boot Layer
        if boot_name != "None (Barefoot)":
            boot_lw = self.leg_width + 14.0
            boot_fl = self.foot_length + 12.0
            boot_fh = self.foot_height + 8.0
            cuff_y = self.leg_top_y + 48.0

            # Draw outsole first so the boot upper sits cleanly into the welt
            self._draw_sole_and_heel(
                stage, cx, base_y, boot_lw, boot_fl,
                boot_name, self.toe_lift, self.sole_thickness, outline_col, stroke
            )

            # Main boot upper silhouette
            boot_pts = self._build_blob_polygon(
                cx, base_y,
                boot_lw, cuff_y,
                boot_fl, boot_fh,
                self.toe_lift, self.puffiness + 3.0
            )
            pygame.draw.polygon(stage, boot_col, boot_pts)
            pygame.draw.polygon(stage, outline_col, boot_pts, stroke)

            left_x = cx - boot_lw * 0.54
            right_x = cx + boot_lw * 0.46
            toe_x = left_x + boot_fl + (self.puffiness + 3.0) * 0.4

            # Soft cartoon cel-shade highlight along the top bridge of the boot
            highlight_col = (
                min(255, boot_col[0] + 38),
                min(255, boot_col[1] + 38),
                min(255, boot_col[2] + 38),
                130
            )
            hl_pts = self._cubic_bezier(
                (right_x + 18, base_y - boot_fh + 16),
                (right_x + 55, base_y - boot_fh + 14),
                (toe_x - 45, base_y - boot_fh * 0.68 - self.toe_lift * 0.35),
                (toe_x - 26, base_y - boot_fh * 0.45 - self.toe_lift * 0.4),
                steps=12
            )
            if len(hl_pts) >= 2:
                pygame.draw.lines(stage, highlight_col, False, hl_pts, 6)

            # --- Silhouette-Specific Hand-Drawn Details ---
            if boot_name == "Cowboy":
                # Classic curved western dip at top of shaft + pull straps + toe bug stitch
                mid_x = (left_x + right_x) * 0.5
                dip_pts = [
                    (left_x + 6, cuff_y + 4),
                    (mid_x, cuff_y + 24),
                    (right_x - 6, cuff_y + 4),
                ]
                pygame.draw.lines(stage, outline_col, False, dip_pts, 6)
                # Pull strap loop on side
                strap = pygame.Rect(int(left_x - 6), int(cuff_y + 12), 18, 34)
                pygame.draw.rect(stage, boot_col, strap, border_radius=6)
                pygame.draw.rect(stage, outline_col, strap, 5, border_radius=6)
                # Decorative western stitch swirl on vamp
                stitch_pts = self._cubic_bezier(
                    (right_x + 28, base_y - 48),
                    (right_x + 65, base_y - 72),
                    (toe_x - 55, base_y - 68),
                    (toe_x - 32, base_y - 42),
                    steps=10
                )
                pygame.draw.lines(stage, outline_col, False, stitch_pts, 4)

            elif boot_name in ("Combat", "Hiking", "Steel-Toe Work"):
                # Padded collar at top cuff
                collar = pygame.Rect(int(left_x - 4), int(cuff_y - 6), int(boot_lw + 8), 24)
                pygame.draw.rect(stage, (48, 48, 56), collar, border_radius=10)
                pygame.draw.rect(stage, outline_col, collar, 5, border_radius=10)

                # Front lace tongue & criss-cross laces
                num_laces = 5 if boot_name == "Combat" else 3
                for i in range(num_laces):
                    ly = int(cuff_y + 32 + i * 22)
                    if ly < base_y - 38:
                        lx_start = int(right_x - 24)
                        lx_end = int(right_x + 6)
                        pygame.draw.circle(stage, (210, 215, 225), (lx_start, ly), 4)
                        pygame.draw.line(stage, outline_col, (lx_start, ly), (lx_end, ly - 5), 5)

                if boot_name == "Steel-Toe Work":
                    # Solid filled metallic steel-toe dome with specular sheen & rivets
                    cap_start = (toe_x - 86, base_y - 3)
                    cap_top = (toe_x - 14, base_y - boot_fh * 0.64)
                    cap_tip = (toe_x - 2, base_y - boot_fh * 0.34)
                    cap_bot = (toe_x - 16, base_y - 3)

                    steel_poly = [cap_start]
                    steel_poly.extend(self._cubic_bezier(
                        cap_start,
                        (toe_x - 90, base_y - boot_fh * 0.56),
                        (toe_x - 54, base_y - boot_fh * 0.72),
                        cap_top,
                        steps=14
                    )[1:])
                    steel_poly.extend(self._cubic_bezier(
                        cap_top,
                        (toe_x - 2, base_y - boot_fh * 0.54),
                        (toe_x + 2, base_y - boot_fh * 0.42),
                        cap_tip,
                        steps=10
                    )[1:])
                    steel_poly.extend(self._cubic_bezier(
                        cap_tip,
                        (toe_x, base_y - 12),
                        (toe_x - 8, base_y - 3),
                        cap_bot,
                        steps=10
                    )[1:])
                    steel_poly.append(cap_start)

                    # Brushed steel base fill + dark outline
                    pygame.draw.polygon(stage, (168, 178, 192), steel_poly)
                    pygame.draw.polygon(stage, outline_col, steel_poly, stroke)

                    # Metallic highlight crescent & rivets
                    shine_pts = self._cubic_bezier(
                        (toe_x - 68, base_y - 16),
                        (toe_x - 68, base_y - boot_fh * 0.46),
                        (toe_x - 42, base_y - boot_fh * 0.56),
                        (toe_x - 22, base_y - boot_fh * 0.48),
                        steps=10
                    )
                    pygame.draw.lines(stage, (232, 238, 246), False, shine_pts, 6)
                    for rx, ry in [(toe_x - 74, base_y - 14), (toe_x - 64, base_y - 42), (toe_x - 36, base_y - 58)]:
                        pygame.draw.circle(stage, (85, 92, 104), (int(rx), int(ry)), 4)

            elif boot_name == "Sneaker":
                # 1. White front half (from the middle of the foot all the way to the toe)
                mid_x = left_x + boot_fl * 0.50
                front_white_surf = pygame.Surface((stage_w, stage_h), pygame.SRCALPHA)
                pygame.draw.polygon(front_white_surf, (245, 246, 250), boot_pts)
                # Clip off the back half (heel to middle) so only the front half remains white
                front_white_surf.fill((0, 0, 0, 0), pygame.Rect(0, 0, int(mid_x), stage_h))
                stage.blit(front_white_surf, (0, 0))

                # Redraw crisp outer ink outline over the two-tone upper
                pygame.draw.polygon(stage, outline_col, boot_pts, stroke)

                # Clean curved vertical seam dividing the coloured back half and white front half
                seam_pts = self._cubic_bezier(
                    (mid_x - 6, base_y - boot_fh + 6),
                    (mid_x + 14, base_y - boot_fh * 0.55),
                    (mid_x + 12, base_y - boot_fh * 0.25),
                    (mid_x - 2, base_y - 3),
                    steps=12
                )
                pygame.draw.lines(stage, outline_col, False, seam_pts, 6)

                # 2. Padded low-top sneaker ankle collar
                collar_pts = self._cubic_bezier(
                    (left_x - 2, cuff_y + 4),
                    (cx - 10, cuff_y + 24),
                    (cx + 22, cuff_y + 22),
                    (right_x + 6, cuff_y - 4),
                    steps=12
                )
                pygame.draw.lines(stage, (245, 246, 250), False, collar_pts, 13)
                pygame.draw.lines(stage, outline_col, False, collar_pts, 5)

                # 3. White sneaker tongue sticking up in front of the ankle
                tongue = pygame.Rect(int(right_x - 14), int(cuff_y - 20), 30, 36)
                pygame.draw.rect(stage, (245, 246, 250), tongue, border_radius=10)
                pygame.draw.rect(stage, outline_col, tongue, 5, border_radius=10)

                # 4. Classic criss-cross sneaker laces along the instep bridge
                for i in range(4):
                    lx = int(right_x + 8 + i * 20)
                    ly = int(cuff_y + 14 + i * 11)
                    # Lace bars with bold dark cartoon outline
                    pygame.draw.line(stage, outline_col, (lx - 4, ly + 4), (lx + 18, ly - 10), 11)
                    pygame.draw.line(stage, (248, 249, 252), (lx - 2, ly + 3), (lx + 16, ly - 9), 5)

            elif boot_name == "Chelsea":
                # Classic U-shaped elastic side gore + back pull tab
                gore_rect = pygame.Rect(int(cx - 22), int(cuff_y + 18), 38, 76)
                pygame.draw.rect(stage, (32, 32, 38), gore_rect, border_radius=16)
                pygame.draw.rect(stage, outline_col, gore_rect, 5, border_radius=16)
                tab = pygame.Rect(int(left_x - 4), int(cuff_y - 16), 16, 22)
                pygame.draw.rect(stage, (32, 32, 38), tab, border_radius=5)
                pygame.draw.rect(stage, outline_col, tab, 4, border_radius=5)

            elif boot_name == "Go-Go Platform":
                # Retro knee-high cuff band + oversized shiny buckle
                band = pygame.Rect(int(left_x - 2), int(cuff_y + 14), int(boot_lw + 4), 18)
                pygame.draw.rect(stage, (245, 245, 250), band, border_radius=6)
                pygame.draw.rect(stage, outline_col, band, 4, border_radius=6)
                buckle = pygame.Rect(int(cx - 10), int(cuff_y + 11), 24, 24)
                pygame.draw.rect(stage, (235, 195, 65), buckle, border_radius=5)
                pygame.draw.rect(stage, outline_col, buckle, 4, border_radius=5)

            elif boot_name == "Fuzzy Yeti":
                # Thick cloud-like fur puffs around the top cuff & ankle
                puffs = [
                    (left_x + 8, cuff_y + 6, 22),
                    (left_x + 42, cuff_y + 2, 24),
                    (cx + 12, cuff_y + 4, 23),
                    (right_x - 6, cuff_y + 8, 21),
                ]
                for px, py, pr in puffs:
                    pygame.draw.circle(stage, boot_col, (int(px), int(py)), pr)
                for px, py, pr in puffs:
                    pygame.draw.circle(stage, outline_col, (int(px), int(py)), pr, 5)

        # 4. Hand-Inked Sticky Material Overlay
        sticky_name = sticky["name"]
        if sticky_name != "None (Clean)":
            s_rgb = sticky["rgb"]
            s_rgba = (s_rgb[0], s_rgb[1], s_rgb[2], 235)
            wobble = math.sin(time_sec * 4.2) * 3.5

            left_x = cx - self.leg_width * 0.54
            toe_x = left_x + self.foot_length
            foot_mid_x = left_x + self.foot_length * 0.56

            if sticky_name == "Wet Cement":
                # Jagged hand-drawn concrete block encasing the foot
                c_pts = [
                    (left_x - 12, base_y - 84),
                    (foot_mid_x + 45, base_y - 78),
                    (toe_x + 22, base_y - 64),
                    (toe_x + 26, base_y + 18),
                    (left_x - 16, base_y + 18),
                ]
                pygame.draw.polygon(stage, s_rgba, c_pts)
                pygame.draw.polygon(stage, outline_col, c_pts, 6)
                # Cracks in the dried cement
                pygame.draw.line(stage, outline_col, (left_x + 28, base_y - 80), (left_x + 42, base_y - 42), 4)
                pygame.draw.line(stage, outline_col, (left_x + 42, base_y - 42), (left_x + 34, base_y - 22), 4)

            elif sticky_name == "Bubblegum":
                # Stretchy hand-inked bubblegum wad stuck to sole & stretching down
                gum_pts = self._cubic_bezier(
                    (foot_mid_x - 28, base_y - 44),
                    (foot_mid_x - 10, base_y - 76),
                    (foot_mid_x + 42, base_y - 72),
                    (foot_mid_x + 56, base_y - 36),
                    steps=12
                )
                gum_pts.extend(self._cubic_bezier(
                    (foot_mid_x + 56, base_y - 36),
                    (foot_mid_x + 40, base_y - 6),
                    (foot_mid_x + 26 + wobble, base_y + 28),
                    (foot_mid_x + 12 + wobble, base_y + 28),
                    steps=12
                )[1:])
                gum_pts.extend(self._cubic_bezier(
                    (foot_mid_x + 12 + wobble, base_y + 28),
                    (foot_mid_x + 4, base_y - 4),
                    (foot_mid_x - 22, base_y - 12),
                    (foot_mid_x - 28, base_y - 44),
                    steps=12
                )[1:])
                pygame.draw.polygon(stage, s_rgba, gum_pts)
                pygame.draw.polygon(stage, outline_col, gum_pts, 5)

            else:
                # Viscous hand-outlined goo cap with hanging drips over the vamp
                cap_x = cx - 10
                cap_y = base_y - self.foot_height - 12
                d1 = 58 + wobble * 1.4
                d2 = 42 - wobble * 1.2
                d3 = 52 + wobble * 1.1

                goo_pts = [
                    (cap_x - 24, cap_y + 12),
                    (cap_x + 88, cap_y + 18),
                    (toe_x - 12, base_y - 34),
                    (toe_x - 18, base_y - 6),
                ]
                # Bottom scalloped drips with dark cartoon ink outline
                goo_pts.extend(self._cubic_bezier(
                    (toe_x - 18, base_y - 6),
                    (cap_x + 76, base_y - 4),
                    (cap_x + 74, cap_y + 28 + d3),
                    (cap_x + 62, cap_y + 28 + d3),
                    steps=10
                )[1:])
                goo_pts.extend(self._cubic_bezier(
                    (cap_x + 62, cap_y + 28 + d3),
                    (cap_x + 50, cap_y + 28 + d3),
                    (cap_x + 48, cap_y + 34),
                    (cap_x + 36, cap_y + 34),
                    steps=8
                )[1:])
                goo_pts.extend(self._cubic_bezier(
                    (cap_x + 36, cap_y + 34),
                    (cap_x + 26, cap_y + 34),
                    (cap_x + 26, cap_y + 32 + d1),
                    (cap_x + 14, cap_y + 32 + d1),
                    steps=10
                )[1:])
                goo_pts.extend(self._cubic_bezier(
                    (cap_x + 14, cap_y + 32 + d1),
                    (cap_x + 2, cap_y + 32 + d1),
                    (cap_x + 2, cap_y + 26 + d2),
                    (cap_x - 12, cap_y + 26 + d2),
                    steps=10
                )[1:])
                goo_pts.append((cap_x - 24, cap_y + 12))

                pygame.draw.polygon(stage, s_rgba, goo_pts)
                pygame.draw.polygon(stage, outline_col, goo_pts, 5)
                # Glossy specular highlight on goo
                pygame.draw.arc(
                    stage, (255, 255, 255, 165),
                    (int(cap_x + 24), int(cap_y + 18), 54, 28),
                    0.2, 2.3, 4
                )

        # Apply spring squish-and-stretch transform anchored at floor level
        scaled_w = max(10, int(stage_w * self.scale_x))
        scaled_h = max(10, int(stage_h * self.scale_y))
        transformed = pygame.transform.smoothscale(stage, (scaled_w, scaled_h))

        draw_x = int(center_x - scaled_w * 0.45)
        draw_y = int(floor_y - scaled_h * 0.85)
        target_surface.blit(transformed, (draw_x, draw_y))