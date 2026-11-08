import os
import math
from PIL import Image, ImageDraw, ImageFont

PLANS_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plans")
os.makedirs(PLANS_OUTPUT_DIR, exist_ok=True)

REGULAR_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def regular_font(size):
    return ImageFont.truetype(REGULAR_FONT_PATH, size)

def bold_font(size):
    return ImageFont.truetype(BOLD_FONT_PATH, size)

def mono_font(size):
    return ImageFont.truetype(MONO_FONT_PATH, size)

BACKGROUND_COLOR = (250, 251, 253)
GRID_LINE_COLOR = (232, 236, 242)
INK_COLOR = (25, 35, 50)
MUTED_TEXT_COLOR = (90, 105, 125)
DIMENSION_BLUE = (20, 90, 180)
FASTENER_RED = (210, 40, 40)
ACCENT_GREEN = (25, 135, 70)

TIMBER_FILL = (235, 195, 135)
PLINTH_TIMBER_FILL = (185, 135, 75)
PLYWOOD_FILL = (245, 228, 185)
PENOPLEX_FILL = (255, 175, 110)
VAGONKA_FILL = (215, 165, 105)
PAVER_FILL = (195, 202, 212)

def create_blueprint_sheet(title_text, subtitle_text, sheet_number):
    width, height = 2000, 1400
    sheet_image = Image.new("RGB", (width, height), BACKGROUND_COLOR)
    canvas = ImageDraw.Draw(sheet_image)
    for grid_x in range(0, width, 40):
        canvas.line([(grid_x, 0), (grid_x, height)], fill=GRID_LINE_COLOR, width=1)
    for grid_y in range(0, height, 40):
        canvas.line([(0, grid_y), (width, grid_y)], fill=GRID_LINE_COLOR, width=1)
    canvas.rectangle([20, 20, width - 20, height - 20], outline=INK_COLOR, width=4)
    canvas.rectangle([20, 20, width - 20, 115], fill=(30, 45, 70), outline=INK_COLOR, width=3)
    canvas.text((45, 32), title_text, font=bold_font(30), fill=(255, 255, 255))
    canvas.text((45, 75), subtitle_text, font=regular_font(20), fill=(200, 220, 245))
    canvas.rectangle([width - 235, 32, width - 35, 103], fill=(255, 205, 70), outline=INK_COLOR, width=2)
    canvas.text((width - 215, 50), f"ЛИСТ {sheet_number} из 4", font=bold_font(25), fill=INK_COLOR)
    return sheet_image, canvas

def draw_dimension_arrow(canvas, start_x, start_y, end_x, end_y, label_text, normal_x, normal_y, offset_distance=40, color=DIMENSION_BLUE, font_size=18):
    delta_x, delta_y = end_x - start_x, end_y - start_y
    segment_length = math.hypot(delta_x, delta_y)
    if segment_length == 0:
        return
    unit_x, unit_y = delta_x / segment_length, delta_y / segment_length
    shifted_start_x, shifted_start_y = start_x + normal_x * offset_distance, start_y + normal_y * offset_distance
    shifted_end_x, shifted_end_y = end_x + normal_x * offset_distance, end_y + normal_y * offset_distance
    canvas.line([(start_x, start_y), (shifted_start_x + normal_x * 6, shifted_start_y + normal_y * 6)], fill=color, width=2)
    canvas.line([(end_x, end_y), (shifted_end_x + normal_x * 6, shifted_end_y + normal_y * 6)], fill=color, width=2)
    canvas.line([(shifted_start_x, shifted_start_y), (shifted_end_x, shifted_end_y)], fill=color, width=3)
    perp_x, perp_y = -unit_y, unit_x
    arrow_half_width, arrow_length = 6, 13
    canvas.polygon([
        (shifted_start_x, shifted_start_y),
        (shifted_start_x + unit_x * arrow_length + perp_x * arrow_half_width, shifted_start_y + unit_y * arrow_length + perp_y * arrow_half_width),
        (shifted_start_x + unit_x * arrow_length - perp_x * arrow_half_width, shifted_start_y + unit_y * arrow_length - perp_y * arrow_half_width)
    ], fill=color)
    canvas.polygon([
        (shifted_end_x, shifted_end_y),
        (shifted_end_x - unit_x * arrow_length + perp_x * arrow_half_width, shifted_end_y - unit_y * arrow_length + perp_y * arrow_half_width),
        (shifted_end_x - unit_x * arrow_length - perp_x * arrow_half_width, shifted_end_y - unit_y * arrow_length - perp_y * arrow_half_width)
    ], fill=color)
    midpoint_x, midpoint_y = (shifted_start_x + shifted_end_x) / 2, (shifted_start_y + shifted_end_y) / 2
    label_font = bold_font(font_size)
    text_bounds = canvas.textbbox((0, 0), label_text, font=label_font)
    text_width, text_height = text_bounds[2] - text_bounds[0], text_bounds[3] - text_bounds[1]
    padding = 5
    canvas.rectangle([midpoint_x - text_width / 2 - padding, midpoint_y - text_height / 2 - padding, midpoint_x + text_width / 2 + padding, midpoint_y + text_height / 2 + padding], fill=BACKGROUND_COLOR, outline=color, width=1)
    canvas.text((midpoint_x - text_width / 2, midpoint_y - text_height / 2 - 2), label_text, font=label_font, fill=color)

def draw_screw_point(canvas, center_x, center_y, radius=7):
    canvas.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius], fill=FASTENER_RED, outline=(255, 255, 255), width=2)

def generate_sheet_one():
    sheet_image, canvas = create_blueprint_sheet(
        "ПРОЕКТ ЗИМНЕЙ БУДКИ 1150×750 мм (ЗАКРЫТЫЙ ЦОКОЛЬ + ЗАЩИТА ОТ ПОДКОПА)",
        "Каркас: брус 50×50 | Утепление: Пеноплэкс 50 мм | Внутри: фанера 10 мм | Снаружи: вагонка 16 мм | Низ: закрытый цоколь на плитке/сетке",
        1
    )

    canvas.text((60, 138), "1. ВИД СВЕРХУ (РАЗРЕЗ ПО СТЕНАМ + ПЛОЩАДКА ОТ ПОДКОПА)", font=bold_font(24), fill=INK_COLOR)
    scale = 0.58
    origin_x, origin_y = 205, 275
    frame_width, frame_height = int(1250 * scale), int(850 * scale)
    vagonka_px = int(16 * scale)
    beam_px = int(50 * scale)
    plywood_px = int(10 * scale)
    pad_margin = int(200 * scale)

    canvas.rectangle(
        [origin_x - pad_margin, origin_y - pad_margin, origin_x + frame_width + pad_margin, origin_y + frame_height + pad_margin],
        fill=(228, 234, 240),
        outline=MUTED_TEXT_COLOR,
        width=2
    )
    for grid_px in range(origin_x - pad_margin, origin_x + frame_width + pad_margin, int(400 * scale)):
        canvas.line([(grid_px, origin_y - pad_margin), (grid_px, origin_y + frame_height + pad_margin)], fill=(195, 205, 215), width=2)
    for grid_py in range(origin_y - pad_margin, origin_y + frame_height + pad_margin, int(400 * scale)):
        canvas.line([(origin_x - pad_margin, grid_py), (origin_x + frame_width + pad_margin, grid_py)], fill=(195, 205, 215), width=2)
    canvas.text((origin_x - pad_margin + 12, origin_y - pad_margin + 8), "Площадка из плитки / кирпича или стальной сетки (1650 × 1250 мм — выступает на 20 см вокруг будки)", font=bold_font(15), fill=MUTED_TEXT_COLOR)

    canvas.rectangle([origin_x - vagonka_px, origin_y - vagonka_px, origin_x + frame_width + vagonka_px, origin_y + frame_height + vagonka_px], fill=VAGONKA_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([origin_x, origin_y, origin_x + frame_width, origin_y + frame_height], fill=PENOPLEX_FILL, outline=INK_COLOR, width=3)
    canvas.rectangle([origin_x + beam_px, origin_y + beam_px, origin_x + frame_width - beam_px, origin_y + frame_height - beam_px], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([origin_x + beam_px + plywood_px, origin_y + beam_px + plywood_px, origin_x + frame_width - beam_px - plywood_px, origin_y + frame_height - beam_px - plywood_px], fill=(255, 252, 242), outline=INK_COLOR, width=3)

    for stud_x in [0, 375, 700, 1100, 1200]:
        canvas.rectangle([origin_x + int(stud_x * scale), origin_y + frame_height - beam_px, origin_x + int((stud_x + 50) * scale), origin_y + frame_height], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    for stud_x in [0, 400, 800, 1200]:
        canvas.rectangle([origin_x + int(stud_x * scale), origin_y, origin_x + int((stud_x + 50) * scale), origin_y + beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    for stud_y in [400]:
        canvas.rectangle([origin_x, origin_y + int(stud_y * scale), origin_x + beam_px, origin_y + int((stud_y + 50) * scale)], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
        canvas.rectangle([origin_x + frame_width - beam_px, origin_y + int(stud_y * scale), origin_x + frame_width, origin_y + int((stud_y + 50) * scale)], fill=TIMBER_FILL, outline=INK_COLOR, width=2)

    door_left_x, door_right_x = origin_x + int(750 * scale), origin_x + int(1100 * scale)
    canvas.rectangle([door_left_x, origin_y + frame_height - beam_px - plywood_px - 4, door_right_x, origin_y + frame_height + vagonka_px + 4], fill=(228, 234, 240), outline=(228, 234, 240))
    canvas.line([(door_left_x, origin_y + frame_height - beam_px - plywood_px), (door_left_x, origin_y + frame_height + vagonka_px)], fill=INK_COLOR, width=3)
    canvas.line([(door_right_x, origin_y + frame_height - beam_px - plywood_px), (door_right_x, origin_y + frame_height + vagonka_px)], fill=INK_COLOR, width=3)
    for dash_x in range(door_left_x, door_right_x, 16):
        canvas.line([(dash_x, origin_y + frame_height), (min(dash_x + 8, door_right_x), origin_y + frame_height)], fill=FASTENER_RED, width=3)

    canvas.text((origin_x + beam_px + 25, origin_y + beam_px + 38), "ГЛУХОЙ ТЕПЛЫЙ УГОЛ (700 × 750 мм)", font=bold_font(21), fill=ACCENT_GREEN)
    canvas.text((origin_x + beam_px + 25, origin_y + beam_px + 72), "• Ветер из входа сюда НЕ попадает", font=regular_font(18), fill=INK_COLOR)
    canvas.text((origin_x + beam_px + 25, origin_y + beam_px + 100), "• Здесь вместе спят 5 щенят сейчас", font=regular_font(18), fill=INK_COLOR)
    canvas.text((origin_x + beam_px + 25, origin_y + beam_px + 128), "  и 2 средние собаки зимой", font=regular_font(18), fill=INK_COLOR)
    canvas.text((origin_x + beam_px + 25, origin_y + beam_px + 175), "ЧИСТЫЙ РАЗМЕР ВНУТРИ:", font=bold_font(19), fill=INK_COLOR)
    canvas.text((origin_x + beam_px + 25, origin_y + beam_px + 202), "1150 × 750 мм (по каркасу)", font=mono_font(19), fill=DIMENSION_BLUE)
    canvas.text((origin_x + beam_px + 25, origin_y + beam_px + 228), "1130 × 730 мм (по фанере 10 мм)", font=mono_font(18), fill=MUTED_TEXT_COLOR)

    canvas.text((door_left_x + 6, origin_y + frame_height - 110), "ВХОД (ЛАЗ)", font=bold_font(18), fill=FASTENER_RED)
    canvas.text((door_left_x + 6, origin_y + frame_height - 86), "350 × 450 мм", font=bold_font(18), fill=FASTENER_RED)

    draw_dimension_arrow(canvas, origin_x, origin_y, origin_x + frame_width, origin_y, "1250 мм (каркас будки)", 0, -1, offset_distance=42)
    draw_dimension_arrow(canvas, origin_x + beam_px, origin_y + beam_px, origin_x + frame_width - beam_px, origin_y + beam_px, "1150 мм (внутри)", 0, 1, offset_distance=24)
    draw_dimension_arrow(canvas, origin_x, origin_y, origin_x, origin_y + frame_height, "850 мм", -1, 0, offset_distance=62)
    draw_dimension_arrow(canvas, origin_x + frame_width - beam_px, origin_y + beam_px, origin_x + frame_width - beam_px, origin_y + frame_height - beam_px, "750 мм", 1, 0, offset_distance=65)
    draw_dimension_arrow(canvas, origin_x + beam_px, origin_y + frame_height, door_left_x, origin_y + frame_height, "700 мм (теплый угол)", 0, 1, offset_distance=48, color=ACCENT_GREEN)
    draw_dimension_arrow(canvas, door_left_x, origin_y + frame_height, door_right_x, origin_y + frame_height, "350 мм (лаз)", 0, 1, offset_distance=48, color=FASTENER_RED)
    draw_dimension_arrow(canvas, door_right_x, origin_y + frame_height, origin_x + frame_width - beam_px, origin_y + frame_height, "100", 0, 1, offset_distance=48, color=DIMENSION_BLUE)

    canvas.text((1090, 138), "2. БОКОВОЙ РАЗРЕЗ (ЗАКРЫТЫЙ ЦОКОЛЬ + ПЛИТКА)", font=bold_font(24), fill=INK_COLOR)
    section_x, section_y = 1235, 845
    plinth_height = int(50 * scale)
    ply_height = int(10 * scale)
    floor_height = int(50 * scale)
    paver_height = int(35 * scale)

    paver_left = section_x - pad_margin
    paver_right = section_x + frame_height + pad_margin
    paver_top = section_y + ply_height + plinth_height
    canvas.rectangle([paver_left, paver_top, paver_right, paver_top + paver_height], fill=PAVER_FILL, outline=INK_COLOR, width=2)
    for joint_x in range(paver_left + int(250 * scale), paver_right, int(250 * scale)):
        canvas.line([(joint_x, paver_top), (joint_x, paver_top + paver_height)], fill=INK_COLOR, width=2)
    canvas.line([(paver_left - 30, paver_top + paver_height), (paver_right + 30, paver_top + paver_height)], fill=ACCENT_GREEN, width=4)
    canvas.text((paver_left + 15, paver_top + paver_height + 8), "Плитка/кирпич или стальная сетка (+20 см шире будки — защита от подкопа!)", font=bold_font(16), fill=ACCENT_GREEN)

    canvas.rectangle([section_x, section_y + ply_height, section_x + frame_height, paver_top], fill=(235, 220, 195), outline=INK_COLOR, width=2)
    for cross_offset in [0, int(400 * scale), frame_height - beam_px]:
        canvas.rectangle([section_x + cross_offset, section_y + ply_height, section_x + cross_offset + beam_px, paver_top], fill=PLINTH_TIMBER_FILL, outline=INK_COLOR, width=2)
    canvas.text((section_x + 48, section_y + ply_height + 5), "Закрытый цоколь 50×50 по кругу (без щелей для лап!)", font=bold_font(14), fill=INK_COLOR)

    canvas.rectangle([section_x, section_y, section_x + frame_height, section_y + ply_height], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([section_x, section_y - floor_height, section_x + frame_height, section_y], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([section_x, section_y - floor_height, section_x + beam_px, section_y], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([section_x + frame_height - beam_px, section_y - floor_height, section_x + frame_height, section_y], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    floor_top_y = section_y - floor_height - ply_height
    canvas.rectangle([section_x, floor_top_y, section_x + frame_height, section_y - floor_height], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)

    back_wall_height = int(650 * scale)
    front_wall_height = int(750 * scale)
    canvas.rectangle([section_x, floor_top_y - back_wall_height, section_x + beam_px, floor_top_y], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([section_x, floor_top_y - beam_px, section_x + beam_px, floor_top_y], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([section_x, floor_top_y - back_wall_height, section_x + beam_px, floor_top_y - back_wall_height + beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([section_x - vagonka_px, floor_top_y - back_wall_height, section_x, paver_top], fill=VAGONKA_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([section_x + beam_px, floor_top_y - back_wall_height, section_x + beam_px + ply_height, floor_top_y], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)

    canvas.rectangle([section_x + frame_height - beam_px, floor_top_y - front_wall_height, section_x + frame_height, floor_top_y], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([section_x + frame_height - beam_px, floor_top_y - beam_px, section_x + frame_height, floor_top_y], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([section_x + frame_height - beam_px, floor_top_y - front_wall_height, section_x + frame_height, floor_top_y - front_wall_height + beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([section_x + frame_height, floor_top_y - front_wall_height, section_x + frame_height + vagonka_px, paver_top], fill=VAGONKA_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([section_x + frame_height - beam_px - ply_height, floor_top_y - front_wall_height, section_x + frame_height - beam_px, floor_top_y], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)

    canvas.line([(section_x + beam_px, floor_top_y - back_wall_height), (section_x + frame_height - beam_px, floor_top_y - front_wall_height)], fill=INK_COLOR, width=3)

    back_overhang = int(80 * scale)
    front_overhang = int(120 * scale)
    roof_start_x, roof_start_y = section_x - back_overhang, floor_top_y - back_wall_height + int(10 * scale)
    roof_end_x, roof_end_y = section_x + frame_height + front_overhang, floor_top_y - front_wall_height - int(14 * scale)
    canvas.line([(roof_start_x, roof_start_y - 12), (roof_end_x, roof_end_y - 12)], fill=FASTENER_RED, width=8)
    canvas.line([(roof_start_x, roof_start_y - 4), (roof_end_x, roof_end_y - 4)], fill=INK_COLOR, width=4)

    plug_start_x, plug_start_y = section_x + beam_px + ply_height + 4, floor_top_y - back_wall_height
    plug_end_x, plug_end_y = section_x + frame_height - beam_px - ply_height - 4, floor_top_y - front_wall_height
    canvas.polygon([(plug_start_x, plug_start_y), (plug_end_x, plug_end_y), (plug_end_x, plug_end_y + beam_px), (plug_start_x, plug_start_y + beam_px)], fill=PENOPLEX_FILL, outline=INK_COLOR)

    canvas.line([(section_x + 215, plug_start_y + 25), (section_x + 215, plug_start_y + 92)], fill=INK_COLOR, width=2)
    canvas.text((section_x + 70, plug_start_y + 96), "Крыша-пробка (Пеноплэкс 50 мм)", font=bold_font(17), fill=INK_COLOR)
    canvas.text((section_x + 70, plug_start_y + 120), "входит внутрь без щелей!", font=regular_font(16), fill=FASTENER_RED)

    canvas.ellipse([section_x - 15, floor_top_y - back_wall_height - 10, section_x + 7, floor_top_y - back_wall_height + 12], fill=FASTENER_RED, outline=INK_COLOR, width=2)
    canvas.line([(section_x - 8, floor_top_y - back_wall_height - 8), (section_x - 45, floor_top_y - back_wall_height - 65)], fill=FASTENER_RED, width=3)
    canvas.text((section_x - 140, floor_top_y - back_wall_height - 110), "2 ПЕТЛИ СЗАДИ\n(крыша поднимается)", font=bold_font(17), fill=FASTENER_RED)

    draw_dimension_arrow(canvas, section_x, floor_top_y, section_x, floor_top_y - back_wall_height, "650 мм (зад)", -1, 0, offset_distance=70)
    draw_dimension_arrow(canvas, section_x + frame_height, floor_top_y, section_x + frame_height, floor_top_y - front_wall_height, "750 мм (перед)", 1, 0, offset_distance=75)
    draw_dimension_arrow(canvas, section_x, paver_top, section_x + frame_height, paver_top, "850 мм (ширина будки)", 0, 1, offset_distance=75)

    canvas.rectangle([45, 985, 1955, 1360], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    canvas.text((65, 1002), "УСТРОЙСТВО «ТЕРМОС-ПИРОГА» БУДКИ И ЗАЩИТА ОТ ПОДКОПА:", font=bold_font(24), fill=DIMENSION_BLUE)

    legend_entries = [
        (TIMBER_FILL, "Брус 50×50 мм (каркас)"),
        (PENOPLEX_FILL, "Пеноплэкс 50 мм (утеплитель)"),
        (PLYWOOD_FILL, "Фанера 10 мм (внутри и пол)"),
        (VAGONKA_FILL, "Вагонка 16 мм (до низа цоколя)"),
        (PAVER_FILL, "Плитка/сетка от подкопа (+20 см)")
    ]
    legend_x = 65
    for swatch_color, swatch_label in legend_entries:
        canvas.rectangle([legend_x, 1045, legend_x + 34, 1075], fill=swatch_color, outline=INK_COLOR, width=2)
        canvas.text((legend_x + 44, 1047), swatch_label, font=bold_font(17), fill=INK_COLOR)
        legend_x += 375

    assembly_steps = [
        "ШАГ 0 (Основание на земле от подкопа): Выравниваем площадку 165×125 см (на 20 см шире будки с каждой стороны) и укладываем",
        "      тротуарную плитку / старый кирпич ИЛИ металлическую сетку (рабицу/кладочную сетку). Собака не сможет рыть под краем будки!",
        "ШАГ 1 (Дно + закрытый цоколь): Скручиваем раму пола 1250×850 мм с Пеноплэксом 50 мм и фанерой 10 мм с двух сторон, а снизу",
        "      прикручиваем замкнутую рамку-цоколь 50×50 мм без щелей (пропитанную антисептиком/мастикой). Лапа под дно не пролезет!",
        "ШАГ 2–5 (Стенки и откидная крыша): Ставим 4 стенки, утепляем Пеноплэксом 50 мм, обшиваем вагонкой до самого низа цоколя и вешаем крышу на 2 петли."
    ]
    step_y = 1096
    for step_line in assembly_steps:
        canvas.text((65, step_y), step_line, font=regular_font(17), fill=INK_COLOR)
        step_y += 46

    sheet_image.save(os.path.join(PLANS_OUTPUT_DIR, "01_general_view_and_layers.png"))
    return sheet_image

def generate_sheet_two():
    sheet_image, canvas = create_blueprint_sheet(
        "ЧЕРТЕЖИ КАРКАСА ИЗ БРУСА 50×50 ММ — ЩИТЫ №1 (ДНО + ЦОКОЛЬ), №2 (ПЕРЕД), №3 (ЗАД)",
        "Все резы прямые под 90°! Красные точки — саморезы по дереву 4,5×90 мм (вкручиваются сквозь обвязку в торец стойки)",
        2
    )

    scale = 0.48
    beam_px = int(50 * scale)

    canvas.text((55, 138), "ЩИТ №1: РАМА ПОЛА (1250×850) + ЗАКРЫТЫЙ ЦОКОЛЬ СНИЗУ", font=bold_font(22), fill=INK_COLOR)
    floor_x, floor_y = 145, 225
    floor_w, floor_h = int(1250 * scale), int(850 * scale)

    canvas.rectangle([floor_x, floor_y, floor_x + floor_w, floor_y + floor_h], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([floor_x, floor_y, floor_x + floor_w, floor_y + beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.rectangle([floor_x, floor_y + floor_h - beam_px, floor_x + floor_w, floor_y + floor_h], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.text((floor_x + 35, floor_y + 2), "Д-1 / Ц-1: 1250 мм", font=bold_font(15), fill=INK_COLOR)
    canvas.text((floor_x + 35, floor_y + floor_h - beam_px + 2), "Д-1 / Ц-1: 1250 мм", font=bold_font(15), fill=INK_COLOR)

    for joist_offset in [0, 400, 800, 1200]:
        joist_x = floor_x + int(joist_offset * scale)
        canvas.rectangle([joist_x, floor_y + beam_px, joist_x + beam_px, floor_y + floor_h - beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
        draw_screw_point(canvas, joist_x + beam_px // 2, floor_y + beam_px // 2)
        draw_screw_point(canvas, joist_x + beam_px // 2, floor_y + floor_h - beam_px // 2)

    for cell_index, cell_start in enumerate([50, 450, 850]):
        center_x = floor_x + int((cell_start + 175) * scale)
        center_y = floor_y + floor_h // 2
        canvas.text((center_x - 70, center_y - 35), "Пеноплэкс 50 мм", font=bold_font(15), fill=INK_COLOR)
        canvas.text((center_x - 60, center_y - 10), "350 × 750 мм", font=mono_font(16), fill=DIMENSION_BLUE)
        canvas.text((center_x - 50, center_y + 16), f"(Ячейка {cell_index + 1})", font=regular_font(15), fill=INK_COLOR)

    draw_dimension_arrow(canvas, floor_x, floor_y, floor_x + floor_w, floor_y, "1250 мм", 0, -1, offset_distance=35)
    draw_dimension_arrow(canvas, floor_x, floor_y, floor_x, floor_y + floor_h, "850 мм", -1, 0, offset_distance=65)
    draw_dimension_arrow(canvas, floor_x + floor_w, floor_y + beam_px, floor_x + floor_w, floor_y + floor_h - beam_px, "750 мм (4 шт. Д-2)", 1, 0, offset_distance=85)
    draw_dimension_arrow(canvas, floor_x + int(50 * scale), floor_y + floor_h, floor_x + int(400 * scale), floor_y + floor_h, "350 мм", 0, 1, offset_distance=32, color=ACCENT_GREEN)
    draw_dimension_arrow(canvas, floor_x + int(450 * scale), floor_y + floor_h, floor_x + int(800 * scale), floor_y + floor_h, "350 мм", 0, 1, offset_distance=32, color=ACCENT_GREEN)
    draw_dimension_arrow(canvas, floor_x + int(850 * scale), floor_y + floor_h, floor_x + int(1200 * scale), floor_y + floor_h, "350 мм", 0, 1, offset_distance=32, color=ACCENT_GREEN)

    canvas.rectangle([55, 695, 955, 835], fill=(255, 255, 255), outline=INK_COLOR, width=2)
    canvas.text((70, 704), "Детали Щита №1 (Рама пола + Закрытый цоколь снизу):", font=bold_font(18), fill=DIMENSION_BLUE)
    canvas.text((70, 732), "• Рама пола (с утеплителем): Д-1 (1250 мм — 2 шт.) + Д-2 (750 мм — 4 шт.).", font=regular_font(16), fill=INK_COLOR)
    canvas.text((70, 758), "• Закрытый цоколь снизу под черновой фанерой (без щелей для лап и ветра):", font=bold_font(16), fill=FASTENER_RED)
    canvas.text((70, 782), "  Ц-1 продольные (1250 мм — 2 шт.) + Ц-2 поперечные (750 мм — 3 шт., по краям и центру).", font=regular_font(16), fill=INK_COLOR)
    canvas.text((70, 806), "• Фанера 10 мм: 2 листа по 1250 × 850 мм (черновой пол + чистовой пол).", font=regular_font(16), fill=INK_COLOR)

    canvas.text((1045, 138), "ЩИТ №2: ПЕРЕДНЯЯ СТЕНКА С ЛАЗОМ (1250 × 750 мм)", font=bold_font(22), fill=INK_COLOR)
    front_x, front_y = 1145, 225
    front_w, front_h = int(1250 * scale), int(750 * scale)

    canvas.rectangle([front_x, front_y, front_x + front_w, front_y + front_h], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([front_x, front_y, front_x + front_w, front_y + beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.rectangle([front_x, front_y + front_h - beam_px, front_x + front_w, front_y + front_h], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.text((front_x + front_w // 2 - 80, front_y + 2), "П-1: 1250 мм", font=bold_font(16), fill=INK_COLOR)
    canvas.text((front_x + 35, front_y + front_h - beam_px + 2), "П-1: 1250 мм", font=bold_font(16), fill=INK_COLOR)

    for stud_offset in [0, 375, 700, 1100, 1200]:
        stud_x = front_x + int(stud_offset * scale)
        canvas.rectangle([stud_x, front_y + beam_px, stud_x + beam_px, front_y + front_h - beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
        draw_screw_point(canvas, stud_x + beam_px // 2, front_y + beam_px // 2)
        draw_screw_point(canvas, stud_x + beam_px // 2, front_y + front_h - beam_px // 2)

    door_height_px = int(450 * scale)
    door_start_x = front_x + int(750 * scale)
    door_end_x = front_x + int(1100 * scale)
    door_top_y = (front_y + front_h - beam_px) - door_height_px
    canvas.rectangle([door_start_x, door_top_y, door_end_x, front_y + front_h - beam_px], fill=(255, 255, 255), outline=FASTENER_RED, width=3)
    canvas.rectangle([door_start_x, door_top_y - beam_px, door_end_x, door_top_y], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    draw_screw_point(canvas, door_start_x - beam_px // 2, door_top_y - beam_px // 2)
    draw_screw_point(canvas, door_end_x + beam_px // 2, door_top_y - beam_px // 2)
    canvas.text((door_start_x + 25, door_top_y - beam_px + 2), "П-3: 350 мм", font=bold_font(15), fill=INK_COLOR)

    canvas.text((door_start_x + 18, door_top_y + 55), "ОКНО ЛАЗА", font=bold_font(19), fill=FASTENER_RED)
    canvas.text((door_start_x + 12, door_top_y + 82), "350 × 450 мм", font=mono_font(18), fill=FASTENER_RED)
    canvas.text((door_start_x + 8, door_top_y + 112), "(выпиливается", font=regular_font(15), fill=FASTENER_RED)
    canvas.text((door_start_x + 8, door_top_y + 132), "в фанере и вагонке)", font=regular_font(15), fill=FASTENER_RED)

    canvas.text((front_x + int(60 * scale), front_y + int(250 * scale)), "Пеноплэкс\n325×650 мм", font=bold_font(15), fill=INK_COLOR)
    canvas.text((front_x + int(435 * scale), front_y + int(250 * scale)), "Пеноплэкс\n275×650 мм", font=bold_font(15), fill=INK_COLOR)
    canvas.text((door_start_x + 15, front_y + beam_px + 8), "Пеноплэкс\n350×150 мм", font=bold_font(14), fill=INK_COLOR)

    draw_dimension_arrow(canvas, front_x, front_y, front_x + front_w, front_y, "1250 мм", 0, -1, offset_distance=35)
    draw_dimension_arrow(canvas, front_x, front_y, front_x, front_y + front_h, "750 мм (перед)", -1, 0, offset_distance=75)
    draw_dimension_arrow(canvas, front_x + front_w, front_y + beam_px, front_x + front_w, front_y + front_h - beam_px, "650 мм (5 шт. П-2)", 1, 0, offset_distance=85)
    draw_dimension_arrow(canvas, front_x + int(50 * scale), front_y + front_h, front_x + int(375 * scale), front_y + front_h, "325 мм", 0, 1, offset_distance=35, color=ACCENT_GREEN)
    draw_dimension_arrow(canvas, front_x + int(425 * scale), front_y + front_h, front_x + int(700 * scale), front_y + front_h, "275 мм", 0, 1, offset_distance=35, color=ACCENT_GREEN)
    draw_dimension_arrow(canvas, door_start_x, front_y + front_h, door_end_x, front_y + front_h, "350 мм (лаз)", 0, 1, offset_distance=35, color=FASTENER_RED)
    draw_dimension_arrow(canvas, door_end_x + beam_px, front_y + front_h, front_x + front_w - beam_px, front_y + front_h, "50", 0, 1, offset_distance=35, color=DIMENSION_BLUE)

    canvas.text((55, 865), "ЩИТ №3: ЗАДНЯЯ СТЕНКА (1250 × 650 мм — НИЖЕ НА 100 ММ)", font=bold_font(22), fill=INK_COLOR)
    back_x, back_y = 145, 945
    back_w, back_h = int(1250 * scale), int(650 * scale)

    canvas.rectangle([back_x, back_y, back_x + back_w, back_y + back_h], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    canvas.rectangle([back_x, back_y, back_x + back_w, back_y + beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.rectangle([back_x, back_y + back_h - beam_px, back_x + back_w, back_y + back_h], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.text((back_x + back_w // 2 - 80, back_y + 2), "З-1: 1250 мм", font=bold_font(16), fill=INK_COLOR)
    canvas.text((back_x + back_w // 2 - 80, back_y + back_h - beam_px + 2), "З-1: 1250 мм", font=bold_font(16), fill=INK_COLOR)

    for stud_offset in [0, 400, 800, 1200]:
        stud_x = back_x + int(stud_offset * scale)
        canvas.rectangle([stud_x, back_y + beam_px, stud_x + beam_px, back_y + back_h - beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
        draw_screw_point(canvas, stud_x + beam_px // 2, back_y + beam_px // 2)
        draw_screw_point(canvas, stud_x + beam_px // 2, back_y + back_h - beam_px // 2)

    for cell_start in [50, 450, 850]:
        center_x = back_x + int((cell_start + 175) * scale)
        center_y = back_y + back_h // 2
        canvas.text((center_x - 70, center_y - 25), "Пеноплэкс 50 мм", font=bold_font(15), fill=INK_COLOR)
        canvas.text((center_x - 60, center_y), "350 × 550 мм", font=mono_font(16), fill=DIMENSION_BLUE)

    draw_dimension_arrow(canvas, back_x, back_y, back_x + back_w, back_y, "1250 мм", 0, -1, offset_distance=30)
    draw_dimension_arrow(canvas, back_x, back_y, back_x, back_y + back_h, "650 мм (зад)", -1, 0, offset_distance=70)
    draw_dimension_arrow(canvas, back_x + back_w, back_y + beam_px, back_x + back_w, back_y + back_h - beam_px, "550 мм (4 шт. З-2)", 1, 0, offset_distance=85)
    draw_dimension_arrow(canvas, back_x + int(50 * scale), back_y + back_h, back_x + int(400 * scale), back_y + back_h, "350 мм", 0, 1, offset_distance=32, color=ACCENT_GREEN)
    draw_dimension_arrow(canvas, back_x + int(450 * scale), back_y + back_h, back_x + int(800 * scale), back_y + back_h, "350 мм", 0, 1, offset_distance=32, color=ACCENT_GREEN)
    draw_dimension_arrow(canvas, back_x + int(850 * scale), back_y + back_h, back_x + int(1200 * scale), back_y + back_h, "350 мм", 0, 1, offset_distance=32, color=ACCENT_GREEN)

    canvas.rectangle([1045, 695, 1945, 1345], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    canvas.text((1070, 715), "СПЕЦИФИКАЦИЯ ЩИТОВ №2 И №3 + КАК КРУТИТЬ:", font=bold_font(22), fill=DIMENSION_BLUE)
    specification_lines = [
        "Щит №2 (Передняя стенка 1250 × 750 мм):",
        "  • Брус П-1 (верх и низ): 1250 мм — 2 шт.",
        "  • Брус П-2 (стойки вертикальные): 650 мм — 5 шт.",
        "  • Брус П-3 (перемычка над лазом): 350 мм — 1 шт.",
        "  • Фанера 10 мм изнутри: 1150 × 750 мм (вырезать окно 350×450)",
        "",
        "Щит №3 (Задняя стенка 1250 × 650 мм):",
        "  • Брус З-1 (верх и низ): 1250 мм — 2 шт.",
        "  • Брус З-2 (стойки вертикальные): 550 мм — 4 шт.",
        "  • Фанера 10 мм изнутри: 1150 × 650 мм — 1 шт.",
        "",
        "КАК КРУТИТЬ САМОРЕЗЫ (чтобы брус не треснул):",
        "  1. В каждую красную точку крутим саморез 4,5 × 90 мм",
        "     (для надежности — по 2 самореза в каждый торец).",
        "  2. Совет: перед вкручиванием 90-мм самореза просверлите",
        "     первый брусок тонким сверлом 3,5–4 мм — тогда брусок",
        "     никогда не лопнет и притянется намертво!",
        "  3. Дополнительно углы можно усилить металлическими",
        "     уголками 40×40 мм на саморезах 3,5 × 35 мм."
    ]
    spec_y = 755
    for line in specification_lines:
        is_heading = line.startswith("Щит") or line.startswith("КАК")
        canvas.text((1070, spec_y), line, font=bold_font(18) if is_heading else regular_font(18), fill=FASTENER_RED if is_heading else INK_COLOR)
        spec_y += 30

    sheet_image.save(os.path.join(PLANS_OUTPUT_DIR, "02_frame_shields_1_to_3.png"))
    return sheet_image

def generate_sheet_three():
    sheet_image, canvas = create_blueprint_sheet(
        "ЧЕРТЕЖИ КАРКАСА — ЩИТЫ №4, №5 (БОКОВИНЫ) И ЩИТ №6 (ОТКИДНАЯ КРЫША)",
        "Боковины вставляются между Передней и Задней стенкой (ширина 750 мм). Крыша имеет внутреннюю теплую рамку-пробку.",
        3
    )

    scale = 0.56
    beam_px = int(50 * scale)

    canvas.text((55, 138), "ЩИТЫ №4 и №5: БОКОВЫЕ СТЕНКИ (2 ШТ., ШИРИНА 750 ММ)", font=bold_font(22), fill=INK_COLOR)
    side_x, side_bottom_y = 155, 675
    side_w = int(750 * scale)
    side_back_h = int(650 * scale)
    side_front_h = int(750 * scale)

    canvas.polygon([
        (side_x, side_bottom_y),
        (side_x + side_w, side_bottom_y),
        (side_x + side_w, side_bottom_y - side_front_h),
        (side_x, side_bottom_y - side_back_h)
    ], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)

    canvas.rectangle([side_x, side_bottom_y - beam_px, side_x + side_w, side_bottom_y], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.text((side_x + 55, side_bottom_y - beam_px + 3), "Б-1: 750 мм", font=bold_font(16), fill=INK_COLOR)

    canvas.rectangle([side_x, side_bottom_y - beam_px - int(550 * scale), side_x + beam_px, side_bottom_y - beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    middle_stud_x = side_x + int(350 * scale)
    canvas.rectangle([middle_stud_x, side_bottom_y - beam_px - int(600 * scale), middle_stud_x + beam_px, side_bottom_y - beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.rectangle([side_x + side_w - beam_px, side_bottom_y - beam_px - int(650 * scale), side_x + side_w, side_bottom_y - beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=3)

    canvas.polygon([
        (side_x, side_bottom_y - side_back_h),
        (side_x + side_w, side_bottom_y - side_front_h),
        (side_x + side_w, side_bottom_y - side_front_h + beam_px),
        (side_x, side_bottom_y - side_back_h + beam_px)
    ], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.text((side_x + 75, side_bottom_y - side_front_h - 38), "Б-5 (верхний наклонный): 757 мм", font=bold_font(17), fill=DIMENSION_BLUE)

    for screw_x, top_screw_y in [
        (side_x + beam_px // 2, side_bottom_y - side_back_h + beam_px // 2),
        (middle_stud_x + beam_px // 2, side_bottom_y - int(700 * scale) + beam_px // 2),
        (side_x + side_w - beam_px // 2, side_bottom_y - side_front_h + beam_px // 2)
    ]:
        draw_screw_point(canvas, screw_x, top_screw_y)
        draw_screw_point(canvas, screw_x, side_bottom_y - beam_px // 2)

    canvas.text((side_x + beam_px + 18, side_bottom_y - int(360 * scale)), "Пеноплэкс\n300×575 мм", font=bold_font(16), fill=INK_COLOR)
    canvas.text((middle_stud_x + beam_px + 18, side_bottom_y - int(380 * scale)), "Пеноплэкс\n300×625 мм", font=bold_font(16), fill=INK_COLOR)

    draw_dimension_arrow(canvas, side_x, side_bottom_y, side_x + side_w, side_bottom_y, "750 мм (вставляется между Передом и Задом)", 0, 1, offset_distance=65)
    draw_dimension_arrow(canvas, side_x, side_bottom_y, side_x, side_bottom_y - side_back_h, "650 мм (зад)", -1, 0, offset_distance=75)
    draw_dimension_arrow(canvas, side_x + side_w, side_bottom_y, side_x + side_w, side_bottom_y - side_front_h, "750 мм (перед)", 1, 0, offset_distance=80)
    draw_dimension_arrow(canvas, side_x + beam_px, side_bottom_y, middle_stud_x, side_bottom_y, "300 мм", 0, 1, offset_distance=28, color=ACCENT_GREEN)
    draw_dimension_arrow(canvas, middle_stud_x + beam_px, side_bottom_y, side_x + side_w - beam_px, side_bottom_y, "300 мм", 0, 1, offset_distance=28, color=ACCENT_GREEN)

    canvas.rectangle([55, 775, 920, 1345], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    canvas.text((75, 795), "ДЕТАЛИ БОКОВЫХ СТЕНОК (НА ОБЕ СТЕНКИ — 2 ЩИТА):", font=bold_font(20), fill=DIMENSION_BLUE)
    side_wall_notes = [
        "На 1 боковую стенку (умножаем на 2 для Левой и Правой):",
        "  • Брус Б-1 (нижний горизонтальный): 750 мм — 1 шт. (всего 2 шт.)",
        "  • Брус Б-2 (передняя высокая стойка): 650 мм — 1 шт. (всего 2 шт.)",
        "  • Брус Б-4 (средняя стойка): 600 мм — 1 шт. (всего 2 шт.)",
        "  • Брус Б-3 (задняя низкая стойка): 550 мм — 1 шт. (всего 2 шт.)",
        "  • Брус Б-5 (верхний наклонный): 757 мм — 1 шт. (всего 2 шт.)",
        "",
        "ХИТРОСТЬ ДЛЯ НОВИЧКА (чтобы не ловить градусы пилой):",
        "  1. Сначала скрутите на полу прямоугольник из нижнего бруса Б-1",
        "     (750 мм) и трех вертикальных стоек: 650 мм, 600 мм и 550 мм.",
        "  2. Приложите сверху длинный брусок Б-5 по верхушкам стоек,",
        "     проведите карандашом линию скоса прямо по месту и отпилите!",
        "  3. Внутренняя фанера 10 мм на боковину: лист шириной 750 мм,",
        "     высота слева 650 мм, справа 750 мм (косой рез по прямой линии)."
    ]
    note_y = 835
    for line in side_wall_notes:
        is_heading = line.startswith("На 1") or line.startswith("ХИТРОСТЬ")
        canvas.text((75, note_y), line, font=bold_font(17) if is_heading else regular_font(17), fill=FASTENER_RED if line.startswith("ХИТРОСТЬ") else INK_COLOR)
        note_y += 34

    canvas.text((975, 138), "ЩИТ №6: ОТКИДНАЯ УТЕПЛЕННАЯ КРЫША (ВИД СНИЗУ)", font=bold_font(22), fill=INK_COLOR)
    roof_x, roof_y = 1075, 225
    roof_scale = 0.52
    roof_w, roof_h = int(1450 * roof_scale), int(1050 * roof_scale)
    plug_w, plug_h = int(1120 * roof_scale), int(720 * roof_scale)
    roof_beam_px = int(50 * roof_scale)

    canvas.rectangle([roof_x, roof_y, roof_x + roof_w, roof_y + roof_h], fill=PLYWOOD_FILL, outline=INK_COLOR, width=3)

    plug_x = roof_x + int(165 * roof_scale)
    plug_y = roof_y + int(145 * roof_scale)
    canvas.rectangle([plug_x, plug_y, plug_x + plug_w, plug_y + plug_h], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)

    canvas.rectangle([plug_x, plug_y, plug_x + plug_w, plug_y + roof_beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.rectangle([plug_x, plug_y + plug_h - roof_beam_px, plug_x + plug_w, plug_y + plug_h], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.text((plug_x + plug_w // 2 - 75, plug_y + 2), "К-1: 1120 мм", font=bold_font(15), fill=INK_COLOR)
    canvas.text((plug_x + plug_w // 2 - 75, plug_y + plug_h - roof_beam_px + 2), "К-1: 1120 мм", font=bold_font(15), fill=INK_COLOR)

    for cross_offset in [0, 355, 715, 1070]:
        cross_x = plug_x + int(cross_offset * roof_scale)
        canvas.rectangle([cross_x, plug_y + roof_beam_px, cross_x + roof_beam_px, plug_y + plug_h - roof_beam_px], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
        draw_screw_point(canvas, cross_x + roof_beam_px // 2, plug_y + roof_beam_px // 2)
        draw_screw_point(canvas, cross_x + roof_beam_px // 2, plug_y + plug_h - roof_beam_px // 2)

    for cell_start in [50, 405, 765]:
        center_x = plug_x + int((cell_start + 150) * roof_scale)
        center_y = plug_y + plug_h // 2
        canvas.text((center_x - 65, center_y - 25), "Пеноплэкс 50 мм", font=bold_font(15), fill=INK_COLOR)
        canvas.text((center_x - 55, center_y), "305 × 620 мм", font=mono_font(15), fill=DIMENSION_BLUE)

    for hinge_x in [plug_x + 60, plug_x + plug_w - 110]:
        canvas.rectangle([hinge_x, roof_y + int(65 * roof_scale), hinge_x + 50, roof_y + int(105 * roof_scale)], fill=FASTENER_RED, outline=INK_COLOR, width=2)
    canvas.text((roof_x + roof_w // 2 - 170, roof_y + 12), "ЗАДНИЙ КРАЙ (сюда крутим 2 петли к задней стенке)", font=bold_font(16), fill=FASTENER_RED)
    canvas.text((roof_x + roof_w // 2 - 150, roof_y + roof_h - 32), "ПЕРЕДНИЙ КОЗЫРЕК НАД ВХОДОМ (свес 185 мм)", font=bold_font(16), fill=DIMENSION_BLUE)

    draw_dimension_arrow(canvas, roof_x, roof_y, roof_x + roof_w, roof_y, "1450 мм (верхний лист крыши с козырьками)", 0, -1, offset_distance=35)
    draw_dimension_arrow(canvas, roof_x + roof_w, roof_y, roof_x + roof_w, roof_y + roof_h, "1050 мм", 1, 0, offset_distance=65)
    draw_dimension_arrow(canvas, plug_x, plug_y + plug_h, plug_x + plug_w, plug_y + plug_h, "1120 мм (теплая рамка-пробка)", 0, 1, offset_distance=35, color=ACCENT_GREEN)
    draw_dimension_arrow(canvas, plug_x, plug_y, plug_x, plug_y + plug_h, "720 мм", -1, 0, offset_distance=55, color=ACCENT_GREEN)

    canvas.rectangle([975, 835, 1945, 1345], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    canvas.text((1000, 855), "ДЕТАЛИ ОТКИДНОЙ КРЫШИ (ЩИТ №6):", font=bold_font(20), fill=DIMENSION_BLUE)
    roof_notes = [
        "• Верхний лист крыши (фанера 10 мм или ОСБ): 1450 × 1050 мм",
        "  (собирается из 1 цельной полосы 1450×675 + добор 1450×375,",
        "   сверху полностью накрывается сплошным куском рубероида",
        "   или гибкой черепицей с загибом по краям).",
        "• Брус теплой рамки К-1 (продольный): 1120 мм — 2 шт.",
        "• Брус теплой рамки К-2 (поперечный): 620 мм — 4 шт.",
        "• Пеноплэкс 50 мм внутрь крыши: 3 куска по 305 × 620 мм.",
        "• Подшивка теплой рамки снизу (фанера 10 мм): 1120 × 720 мм.",
        "",
        "ПОЧЕМУ ТАКАЯ КРЫША ЛУЧШЕ ОБЫЧНОЙ ПЛОСКОЙ:",
        "  Рамка 1120 × 720 мм меньше внутреннего размера будки",
        "  (1130 × 730 мм) ровно на 5 мм с каждой стороны.",
        "  Когда крыша опускается, теплая рамка плотно заходит",
        "  внутрь коробки будки как пробка и полностью перекрывает",
        "  мостик холода под крышей!"
    ]
    roof_note_y = 892
    for line in roof_notes:
        is_heading = line.startswith("ПОЧЕМУ")
        canvas.text((1000, roof_note_y), line, font=bold_font(17) if is_heading else regular_font(17), fill=FASTENER_RED if is_heading else INK_COLOR)
        roof_note_y += 29

    sheet_image.save(os.path.join(PLANS_OUTPUT_DIR, "03_frame_shields_4_to_6.png"))
    return sheet_image

def generate_sheet_four():
    sheet_image, canvas = create_blueprint_sheet(
        "КАРТА РАСКРОЯ МАТЕРИАЛОВ (ФАНЕРА 1525×1525, ПЕНОПЛЭКС, 12 БРУСКОВ)",
        "Как расчертить магазинные листы карандашом перед распилом, чтобы хватило ровно 4 листов фанеры и 1 пачки Пеноплэкса",
        4
    )

    canvas.text((55, 136), "1. РАСКРОЙ 4 ЛИСТОВ ФАНЕРЫ 10 ММ (СТАНДАРТНЫЙ ЛИСТ 1525 × 1525 ММ):", font=bold_font(23), fill=INK_COLOR)

    plywood_scale = 0.255
    plywood_layouts = [
        ("ЛИСТ ФАНЕРЫ №1 (Чистовой пол + Левая боковина)", [
            (0, 0, 1250, 850, PLYWOOD_FILL, "ЧИСТОВОЙ ПОЛ\n1250 × 850 мм"),
            (0, 850, 750, 675, (220, 240, 215), "ЛЕВАЯ БОКОВИНА\n(внутри)\n750 × 675..750 мм"),
            (750, 850, 775, 675, (235, 235, 235), "Остаток\n775 × 675 мм\n(на полосу крыши)"),
            (1250, 0, 275, 850, (240, 240, 240), "Остаток\n275×850")
        ]),
        ("ЛИСТ ФАНЕРЫ №2 (Черновой пол + Правая боковина)", [
            (0, 0, 1250, 850, PLYWOOD_FILL, "ЧЕРНОВОЙ ПОЛ\n(снизу под раму)\n1250 × 850 мм"),
            (0, 850, 750, 675, (220, 240, 215), "ПРАВАЯ БОКОВИНА\n(внутри)\n750 × 675..750 мм"),
            (750, 850, 775, 675, (235, 235, 235), "Остаток\n775 × 675 мм"),
            (1250, 0, 275, 850, (240, 240, 240), "Остаток\n275×850")
        ]),
        ("ЛИСТ ФАНЕРЫ №3 (Передняя и Задняя стенки внутри)", [
            (0, 0, 1150, 750, PLYWOOD_FILL, "ПЕРЕДНЯЯ СТЕНКА (внутри)\n1150 × 750 мм\n(вырезать лаз 350×450)"),
            (0, 750, 1150, 650, (220, 240, 215), "ЗАДНЯЯ СТЕНКА (внутри)\n1150 × 650 мм"),
            (1150, 0, 375, 1450, (255, 235, 200), "ДОБОР\nКРЫШИ\n375×1450")
        ]),
        ("ЛИСТ ФАНЕРЫ №4 (Верх крыши + Подшивка крыши снизу)", [
            (0, 0, 1450, 675, (255, 235, 200), "ОСНОВНАЯ ЧАСТЬ ВЕРХА КРЫШИ\n1450 × 675 мм\n(+ добор 375×1450 с Листа №3 = 1450×1050)"),
            (0, 675, 1120, 720, PLYWOOD_FILL, "ПОДШИВКА ТЕПЛОЙ ПРОБКИ КРЫШИ\n1120 × 720 мм")
        ])
    ]

    for sheet_index, (sheet_title, rectangles) in enumerate(plywood_layouts):
        base_x = 55 + sheet_index * 480
        base_y = 198
        sheet_px = int(1525 * plywood_scale)
        canvas.text((base_x, base_y - 26), sheet_title, font=bold_font(14), fill=DIMENSION_BLUE)
        canvas.rectangle([base_x, base_y, base_x + sheet_px, base_y + sheet_px], fill=(245, 245, 245), outline=INK_COLOR, width=3)
        for rect_x, rect_y, rect_w, rect_h, fill_color, rect_label in rectangles:
            x1 = base_x + int(rect_x * plywood_scale)
            y1 = base_y + int(rect_y * plywood_scale)
            x2 = base_x + int((rect_x + rect_w) * plywood_scale)
            y2 = base_y + int((rect_y + rect_h) * plywood_scale)
            canvas.rectangle([x1, y1, x2, y2], fill=fill_color, outline=INK_COLOR, width=2)
            canvas.text((x1 + 8, y1 + 10), rect_label, font=bold_font(13), fill=INK_COLOR)
        canvas.text((base_x + sheet_px // 2 - 55, base_y + sheet_px + 6), "1525 × 1525 мм", font=mono_font(14), fill=MUTED_TEXT_COLOR)

    canvas.text((55, 625), "2. КАРТА РАСПИЛА БРУСА 50×50 ММ (12 ШТУК ПО 3000 ММ — ВКЛЮЧАЯ ЗАКРЫТЫЙ ЦОКОЛЬ):", font=bold_font(22), fill=INK_COLOR)

    three_meter_bars = [
        ("Брус 3м №1", [(1250, "Д-1 (Дно): 1250"), (1250, "Д-1 (Дно): 1250"), (350, "П-3: 350")]),
        ("Брус 3м №2", [(1250, "П-1 (Перед): 1250"), (1250, "П-1 (Перед): 1250")]),
        ("Брус 3м №3", [(1250, "З-1 (Зад): 1250"), (1250, "З-1 (Зад): 1250")]),
        ("Брус 3м №4", [(750, "Д-2: 750"), (750, "Д-2: 750"), (750, "Д-2: 750"), (750, "Д-2: 750")]),
        ("Брус 3м №5", [(750, "Б-1 (Бок): 750"), (750, "Б-1 (Бок): 750"), (757, "Б-5 (Скос): 757"), (650, "П-2: 650")]),
        ("Брус 3м №6", [(650, "П-2: 650"), (650, "П-2: 650"), (650, "П-2: 650"), (650, "П-2: 650")]),
        ("Брус 3м №7", [(650, "Б-2: 650"), (650, "Б-2: 650"), (600, "Б-4: 600"), (600, "Б-4: 600")]),
        ("Брус 3м №8", [(550, "З-2: 550"), (550, "З-2: 550"), (550, "З-2: 550"), (550, "З-2: 550"), (550, "Б-3: 550")]),
        ("Брус №9 (Цоколь)", [(1250, "Ц-1 (Цоколь): 1250"), (1250, "Ц-1 (Цоколь): 1250"), (500, "Запас")]),
        ("Брус №10 (Цоколь)", [(750, "Ц-2 (Цоколь): 750"), (750, "Ц-2 (Цоколь): 750"), (750, "Ц-2 (Цоколь): 750"), (550, "Б-3: 550")]),
        ("Брус №11 (Крыша)", [(1120, "К-1 (Крыша): 1120"), (1120, "К-1 (Крыша): 1120"), (620, "К-2: 620")]),
        ("Брус №12 (Крыша)", [(620, "К-2: 620"), (620, "К-2: 620"), (620, "К-2: 620"), (1140, "Запас")])
    ]

    bar_scale = 0.25
    for bar_index, (bar_name, bar_cuts) in enumerate(three_meter_bars):
        column_index = bar_index // 6
        row_index = bar_index % 6
        label_x = 55 + column_index * 960
        bar_y = 670 + row_index * 48
        canvas.text((label_x, bar_y + 6), bar_name, font=bold_font(15), fill=INK_COLOR)
        bar_start_x = label_x + 185
        canvas.rectangle([bar_start_x, bar_y, bar_start_x + int(3000 * bar_scale), bar_y + 34], fill=(235, 235, 235), outline=INK_COLOR, width=2)
        current_x = bar_start_x
        for cut_length, cut_label in bar_cuts:
            cut_width = int(cut_length * bar_scale)
            is_remainder = "Остаток" in cut_label or "Запас" in cut_label
            canvas.rectangle([current_x, bar_y, current_x + cut_width, bar_y + 34], fill=(240, 240, 240) if is_remainder else TIMBER_FILL, outline=INK_COLOR, width=2)
            canvas.text((current_x + 5, bar_y + 8), cut_label, font=bold_font(13) if not is_remainder else regular_font(13), fill=INK_COLOR)
            current_x += cut_width

    canvas.rectangle([55, 975, 1945, 1360], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    canvas.text((75, 992), "3. ИТОГОВАЯ ЗАКУПОЧНАЯ ВЕДОМОСТЬ (ЧТО ЗАКАЗАТЬ В ТЕЛЕХАНАХ / НА 21VEK.BY):", font=bold_font(23), fill=DIMENSION_BLUE)

    shopping_left_column = [
        "1. Брус 50×50 мм (сухой строганный или обрезной):",
        "   • 12 штук по 3 метра (всего 36 пог. м) — каркас + крыша + закрытый цоколь.",
        "2. Фанера 10 мм (стандартные листы 1525 × 1525 мм):",
        "   • 4 листа (хватает на черновой пол, чистовой пол, 4 стенки изнутри и крышу).",
        "3. Утеплитель ПЕНОПЛЭКС КОМФОРТ 50 мм (листы 1185 × 585 мм):",
        "   • Ровно 1 упаковка (7 или 8 листов, ~5 м²): 3 куска в пол (350×750),",
        "     3 куска в заднюю стенку (350×550), 3 в переднюю, 4 в боковины, 3 в крышу.",
        "4. Вагонка деревянная (для наружной обшивки 4 стен до низа цоколя):",
        "   • Площадь стен снаружи = 3,8 м² (берем с запасом 4,4 м² — например,",
        "     2 пачки евровагонки длиной 2,0–2,5 м или обшивку на Заводской, 1)."
    ]

    shopping_right_column = [
        "5. Основание против подкопа (на площадку 165 × 125 см под будку):",
        "   • 12 тротуарных плиток 40×40 см (или старый кирпич) ИЛИ кусок сварной сетки 2×1,5 м.",
        "6. Деревянный уголок (40×40 мм) или Наличник (с завода ТЗСИ):",
        "   • 4 планки по 2,0–2,2 м (на 4 внешних угла будки и рамку вокруг лаза).",
        "7. Кровля на крышу (1450 × 1050 мм = 1,55 м²) + Крепеж:",
        "   • 1 пачка гибкой черепицы (~3 м²) ИЛИ кусок рубероида / профлиста 1,6×1,2 м.",
        "   • Саморезы желтые 4,5 × 90 мм (для бруса 50×50) — 1 пачка (100–120 шт.).",
        "   • Саморезы желтые 3,5 × 35 мм (для фанеры и уголков) — 1 пачка (250–300 шт.).",
        "   • Саморезы тонкие 3,0 × 30 мм или гвоздики (для вагонки) — 200 шт.",
        "   • 2 крепкие дверные петли + 1 баллон монтажной пены + пропитка для дерева/цоколя."
    ]

    left_y = 1035
    for line in shopping_left_column:
        is_numbered = line[0].isdigit()
        canvas.text((75, left_y), line, font=bold_font(17) if is_numbered else regular_font(17), fill=INK_COLOR)
        left_y += 31

    right_y = 1035
    for line in shopping_right_column:
        is_numbered = line[0].isdigit()
        canvas.text((1015, right_y), line, font=bold_font(17) if is_numbered else regular_font(17), fill=INK_COLOR)
        right_y += 31

    sheet_image.save(os.path.join(PLANS_OUTPUT_DIR, "04_cutlist_plywood_and_penoplex.png"))
    return sheet_image

def generate_all():
    sheet_one = generate_sheet_one()
    sheet_two = generate_sheet_two()
    sheet_three = generate_sheet_three()
    sheet_four = generate_sheet_four()
    sheet_one.save(
        os.path.join(PLANS_OUTPUT_DIR, "doghouse_blueprints_telekhany.pdf"),
        "PDF",
        resolution=150.0,
        save_all=True,
        append_images=[sheet_two, sheet_three, sheet_four]
    )

if __name__ == "__main__":
    generate_all()
