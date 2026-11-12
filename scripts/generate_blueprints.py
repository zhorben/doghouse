import os
import json
import math
from decimal import Decimal
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
OSB_FILL = (232, 210, 155)
PENOPLEX_FILL = (255, 175, 110)
VAGONKA_FILL = (215, 165, 105)
MESH_COLOR = (110, 125, 145)


def compute_doghouse_engineering_model(variant_key="main_50mm"):
    is_budget = (variant_key == "budget_30mm")

    frame_length = 1250
    frame_width = 850
    beam_size = 40 if is_budget else 50
    foam_thickness = 30 if is_budget else 50

    front_wall_height = 750
    back_wall_height = 650
    height_drop = front_wall_height - back_wall_height

    floor_plywood_thick = 10
    subfloor_plywood_thick = 4
    inner_back_plywood_thick = 10
    inner_wall_plywood_thick = 4
    outer_cladding_thick = 16

    interior_frame_length = frame_length - 2 * beam_size
    interior_frame_width = frame_width - 2 * beam_size
    clean_room_length = interior_frame_length - 2 * inner_wall_plywood_thick
    clean_room_width = interior_frame_width - inner_back_plywood_thick - inner_wall_plywood_thick

    outer_total_length = frame_length + 2 * outer_cladding_thick
    outer_total_width = frame_width + 2 * outer_cladding_thick

    door_width = 350
    door_height = 450
    door_right_inner_offset = 100
    warm_corner_length = interior_frame_length - door_width - door_right_inner_offset

    assert warm_corner_length + door_width + door_right_inner_offset == interior_frame_length

    side_wall_width = frame_width - 2 * beam_size
    assert side_wall_width == interior_frame_width

    slope_radians = math.atan2(height_drop, side_wall_width)
    slope_degrees = math.degrees(slope_radians)
    acute_angle_deg = 90.0 - slope_degrees
    obtuse_angle_deg = 90.0 + slope_degrees

    assert abs((acute_angle_deg + obtuse_angle_deg) - 180.0) < 1e-9

    bevel_offset_exact_mm = beam_size * math.tan(slope_radians)
    bevel_offset_rounded_mm = round(bevel_offset_exact_mm, 1)
    sloped_beam_length = round(math.hypot(side_wall_width, height_drop))

    def side_wall_total_height_at(x_pos):
        return back_wall_height + (height_drop * (x_pos / side_wall_width))

    def side_stud_height_at(x_pos):
        return (back_wall_height - 2 * beam_size) + (height_drop * (x_pos / side_wall_width))

    back_stud_x0, back_stud_x1 = 0, beam_size
    mid_stud_x0 = (side_wall_width - beam_size) // 2
    mid_stud_x1 = mid_stud_x0 + beam_size
    front_stud_x0, front_stud_x1 = side_wall_width - beam_size, side_wall_width

    stud_b3_left = round(side_stud_height_at(back_stud_x0), 1)
    stud_b3_right = round(side_stud_height_at(back_stud_x1), 1)
    stud_b4_left = round(side_stud_height_at(mid_stud_x0), 1)
    stud_b4_right = round(side_stud_height_at(mid_stud_x1), 1)
    stud_b2_left = round(side_stud_height_at(front_stud_x0), 1)
    stud_b2_right = round(side_stud_height_at(front_stud_x1), 1)

    assert abs((stud_b3_right - stud_b3_left) - bevel_offset_exact_mm) < 0.15
    assert abs((stud_b4_right - stud_b4_left) - bevel_offset_exact_mm) < 0.15
    assert abs((stud_b2_right - stud_b2_left) - bevel_offset_exact_mm) < 0.15
    assert abs(stud_b3_left - (back_wall_height - 2 * beam_size)) < 1e-9
    assert abs(stud_b2_right - (front_wall_height - 2 * beam_size)) < 1e-9

    side_cell_1_width = mid_stud_x0 - back_stud_x1
    side_cell_2_width = front_stud_x0 - mid_stud_x1
    assert back_stud_x1 + side_cell_1_width + beam_size + side_cell_2_width + beam_size == side_wall_width

    floor_joist_count = 4
    floor_cell_count = floor_joist_count - 1
    floor_inner_span = frame_length - floor_joist_count * beam_size
    floor_cell_width = floor_inner_span // floor_cell_count
    floor_cell_remainder = floor_inner_span % floor_cell_count
    floor_cell_widths = [
        floor_cell_width + (1 if i < floor_cell_remainder else 0)
        for i in range(floor_cell_count)
    ]
    assert sum(floor_cell_widths) + floor_joist_count * beam_size == frame_length

    front_stud_height = front_wall_height - 2 * beam_size
    back_stud_height = back_wall_height - 2 * beam_size

    front_right_cell_width = door_right_inner_offset - beam_size
    front_left_span = warm_corner_length - 2 * beam_size
    front_cell_1_width = front_left_span // 2 + 25
    front_cell_2_width = front_left_span - front_cell_1_width
    assert (
        beam_size + front_cell_1_width + beam_size + front_cell_2_width +
        beam_size + door_width + beam_size + front_right_cell_width + beam_size
    ) == frame_length

    front_above_door_foam_h = front_stud_height - door_height - beam_size
    assert front_above_door_foam_h + beam_size + door_height == front_stud_height

    roof_length = 1450
    roof_width = 1050
    roof_plug_clearance = 5
    roof_plug_length = clean_room_length - 2 * roof_plug_clearance
    roof_plug_width = clean_room_width - 2 * roof_plug_clearance
    roof_plug_cross_len = roof_plug_width - 2 * beam_size

    roof_cross_count = 4
    roof_cell_count = 3
    roof_inner_span = roof_plug_length - roof_cross_count * beam_size
    roof_cell_w_base = roof_inner_span // roof_cell_count
    roof_cell_rem = roof_inner_span % roof_cell_count
    roof_cell_widths = [
        roof_cell_w_base + (1 if i < roof_cell_rem else 0)
        for i in range(roof_cell_count)
    ]
    assert sum(roof_cell_widths) + roof_cross_count * beam_size == roof_plug_length

    timber_parts = [
        {"code": "Д-1", "name": "Рама пола (продольные)", "length": frame_length, "qty": 2, "angle_left": 90.0, "angle_right": 90.0},
        {"code": "Д-2", "name": "Рама пола (поперечные)", "length": interior_frame_width, "qty": 4, "angle_left": 90.0, "angle_right": 90.0},
        {"code": "Ц-1", "name": "Закрытый цоколь (продольные)", "length": frame_length, "qty": 2, "angle_left": 90.0, "angle_right": 90.0},
        {"code": "Ц-2", "name": "Закрытый цоколь (поперечные)", "length": interior_frame_width, "qty": 3, "angle_left": 90.0, "angle_right": 90.0},
        {"code": "П-1", "name": "Передняя стенка (верх и низ)", "length": frame_length, "qty": 2, "angle_left": 90.0, "angle_right": 90.0},
        {"code": "П-2", "name": "Передняя стенка (стойки)", "length": front_stud_height, "qty": 5, "angle_left": 90.0, "angle_right": 90.0},
        {"code": "П-3", "name": "Перемычка над лазом", "length": door_width, "qty": 1, "angle_left": 90.0, "angle_right": 90.0},
        {"code": "З-1", "name": "Задняя стенка (верх и низ)", "length": frame_length, "qty": 2, "angle_left": 90.0, "angle_right": 90.0},
        {"code": "З-2", "name": "Задняя стенка (стойки)", "length": back_stud_height, "qty": 4, "angle_left": 90.0, "angle_right": 90.0},
        {"code": "Б-1", "name": "Боковины (нижний брус)", "length": side_wall_width, "qty": 2, "angle_left": 90.0, "angle_right": 90.0},
        {"code": "Б-2", "name": f"Боковины (передняя стойка {stud_b2_left}..{stud_b2_right})", "length": round(stud_b2_right), "qty": 2, "angle_left": 90.0, "angle_right": round(acute_angle_deg, 1)},
        {"code": "Б-4", "name": f"Боковины (средняя стойка {stud_b4_left}..{stud_b4_right})", "length": round(stud_b4_right), "qty": 2, "angle_left": 90.0, "angle_right": round(acute_angle_deg, 1)},
        {"code": "Б-3", "name": f"Боковины (задняя стойка {stud_b3_left}..{stud_b3_right})", "length": round(stud_b3_right), "qty": 2, "angle_left": 90.0, "angle_right": round(acute_angle_deg, 1)},
        {"code": "Б-5", "name": "Боковины (верхний наклонный брус)", "length": sloped_beam_length, "qty": 2, "angle_left": round(obtuse_angle_deg, 1), "angle_right": round(acute_angle_deg, 1)},
        {"code": "К-1", "name": "Рамка крыши (продольные)", "length": roof_plug_length, "qty": 2, "angle_left": 90.0, "angle_right": 90.0},
        {"code": "К-2", "name": "Рамка крыши (поперечные)", "length": roof_plug_cross_len, "qty": 4, "angle_left": 90.0, "angle_right": 90.0},
    ]

    total_timber_pieces = sum(p["qty"] for p in timber_parts)
    straight_90_pieces = sum(p["qty"] for p in timber_parts if p["angle_left"] == 90.0 and p["angle_right"] == 90.0)
    angled_pieces = total_timber_pieces - straight_90_pieces
    assert total_timber_pieces == 41
    assert straight_90_pieces == 33
    assert angled_pieces == 8

    all_individual_cuts = []
    for part in timber_parts:
        for _ in range(part["qty"]):
            all_individual_cuts.append((part["length"], f"{part['code']}: {part['length']}"))
    all_individual_cuts.sort(key=lambda x: x[0], reverse=True)

    bar_stock_length = 3000
    packed_bars = []
    for cut_len, cut_lbl in all_individual_cuts:
        placed = False
        for bar in packed_bars:
            used = sum(c[0] for c in bar)
            if used + cut_len <= bar_stock_length:
                bar.append((cut_len, cut_lbl))
                placed = True
                break
        if not placed:
            packed_bars.append([(cut_len, cut_lbl)])

    for bar in packed_bars:
        assert sum(c[0] for c in bar) <= bar_stock_length

    num_3m_bars = len(packed_bars)
    total_linear_meters = num_3m_bars * 3
    timber_volume_m3 = round(total_linear_meters * (beam_size / 1000.0) * (beam_size / 1000.0), 4)

    if is_budget:
        bom_items = [
            {"num": 1, "title": f"Брус {beam_size}×{beam_size} мм в Телеханском лесхозе ({num_3m_bars} шт. по 3 м = {timber_volume_m3:.3f} м³)", "note": "Цех переработки в Телеханах: +375 (1645) 21-4-81, отдел сбыта 21-2-45.", "price": Decimal("22.00")},
            {"num": 2, "title": "Фанера 10 мм (1 лист 1525×1525, Код ОМА 2.114680)", "note": f"Чистовой пол ({frame_length}×{frame_width}) + задняя стенка внутри ({interior_frame_length}×{back_wall_height}).", "price": Decimal("35.44")},
            {"num": 3, "title": "Фанера 4 мм (2 листа 1525×1525, Код ОМА 2.116157 по 17,17 р.)", "note": "Черновой пол снизу, передняя и обе боковые стенки внутри.", "price": Decimal("34.34")},
            {"num": 4, "title": "Плита ОСБ-3 влагостойкая 9 мм (1 лист 2500×1250, Код ОМА 2.217093)", "note": f"Цельный верх крыши ({roof_length}×{roof_width}) + цельная подшивка крыши ({roof_plug_length}×{roof_plug_width}).", "price": Decimal("28.29")},
            {"num": 5, "title": "Утеплитель ТЕХНОПЛЕКС XPS 30 мм (7 листов, Код ОМА 2.255057 по 5,09 р.)", "note": "Экструдированный пенополистирол 30 мм в пол, все 4 стены и крышу (как в видео 7PO74wVwbDE).", "price": Decimal("35.63")},
            {"num": 6, "title": "Вагонка сорт С / 2 сорт (3,8 м², Код ОМА 2.444227 / завод ТЗСИ)", "note": "Наружная обшивка всех 4 стен до самого низа закрытого цоколя.", "price": Decimal("74.00")},
            {"num": 7, "title": "Наличник деревянный 13×74 мм 2 сорт (ТЗСИ Заводская, 1: 9 м по 2,21 р.)", "note": "Скручивается Г-образно на 4 внешних угла будки и рамку вокруг лаза.", "price": Decimal("19.89")},
            {"num": 8, "title": "Рубероид кровельный РКПО-350 15 м² (Код ОМА 2.175257)", "note": "Кровля крыши в 2 слоя + полосы гидроизоляции снизу под закрытый цоколь.", "price": Decimal("31.11")},
            {"num": 9, "title": "Сетка стальная кладочная 0,5×2,0 м от подкопа (3 карты в грунт)", "note": "Ковер 200×150 см под будку — когти упираются в стальные прутья, подрыть невозможно.", "price": Decimal("30.00")},
            {"num": 10, "title": "Пропитка фанеры/бруса (PentaStyle 2л, Код 2.418074) + Аквалазурь (Код 2.460152) + крепеж", "note": "Биозащита бруса и изнанки/торцов фанеры (12,76 р.), лазурь вагонки (18,34 р.), саморезы, 2 петли, пена.", "price": Decimal("52.00")},
        ]
    else:
        bom_items = [
            {"num": 1, "title": f"Брус {beam_size}×{beam_size} мм в Телеханском лесхозе ({num_3m_bars} шт. по 3 м = {timber_volume_m3:.3f} м³)", "note": "Цех переработки в Телеханах: +375 (1645) 21-4-81, отдел сбыта 21-2-45.", "price": Decimal("30.00")},
            {"num": 2, "title": "Фанера 10 мм (1 лист 1525×1525, Код ОМА 2.114680)", "note": f"Чистовой пол ({frame_length}×{frame_width}) + задняя стенка внутри ({interior_frame_length}×{back_wall_height}).", "price": Decimal("35.44")},
            {"num": 3, "title": "Фанера 4 мм (2 листа 1525×1525, Код ОМА 2.116157 по 17,17 р.)", "note": "Черновой пол снизу, передняя и обе боковые стенки внутри.", "price": Decimal("34.34")},
            {"num": 4, "title": "Плита ОСБ-3 влагостойкая 9 мм (1 лист 2500×1250, Код ОМА 2.217093)", "note": f"Цельный верх крыши ({roof_length}×{roof_width}) + цельная подшивка крыши ({roof_plug_length}×{roof_plug_width}).", "price": Decimal("28.29")},
            {"num": 5, "title": "Утеплитель ТЕХНОПЛЕКС XPS 50 мм (7 листов, Код ОМА 2.255059 по 9,73 р.)", "note": "Экструдированный пенополистирол 50 мм в пол, все 4 стены и крышу.", "price": Decimal("68.11")},
            {"num": 6, "title": "Вагонка сорт С / 2 сорт (3,8 м², Код ОМА 2.444227 / завод ТЗСИ)", "note": "Наружная обшивка всех 4 стен до самого низа закрытого цоколя.", "price": Decimal("74.00")},
            {"num": 7, "title": "Наличник деревянный 13×74 мм 2 сорт (ТЗСИ Заводская, 1: 9 м по 2,21 р.)", "note": "Скручивается Г-образно на 4 внешних угла будки и рамку вокруг лаза.", "price": Decimal("19.89")},
            {"num": 8, "title": "Черепица рулонная Технониколь МИНИ 2,5 м² (Код ОМА 2.252623)", "note": "1,52 м² идет на крышу, а остаток 0,98 м² режем на полосы под низ цоколя!", "price": Decimal("40.99")},
            {"num": 9, "title": "Сетка стальная кладочная 0,5×2,0 м от подкопа (3 карты в грунт)", "note": "Ковер 200×150 см под будку — когти упираются в стальные прутья, подрыть невозможно.", "price": Decimal("30.00")},
            {"num": 10, "title": "Пропитка фанеры/бруса (PentaStyle 2л, Код 2.418074) + Аквалазурь (Код 2.460152) + крепеж", "note": "Биозащита бруса и изнанки/торцов фанеры (12,76 р.), лазурь вагонки (18,34 р.), саморезы, 2 петли, пена.", "price": Decimal("54.00")},
        ]

    total_cost_byn = sum(item["price"] for item in bom_items)

    return {
        "variant_key": variant_key,
        "is_budget": is_budget,
        "frame_length": frame_length,
        "frame_width": frame_width,
        "beam_size": beam_size,
        "foam_thickness": foam_thickness,
        "front_wall_height": front_wall_height,
        "back_wall_height": back_wall_height,
        "height_drop": height_drop,
        "interior_frame_length": interior_frame_length,
        "interior_frame_width": interior_frame_width,
        "clean_room_length": clean_room_length,
        "clean_room_width": clean_room_width,
        "outer_total_length": outer_total_length,
        "outer_total_width": outer_total_width,
        "door_width": door_width,
        "door_height": door_height,
        "door_right_inner_offset": door_right_inner_offset,
        "warm_corner_length": warm_corner_length,
        "side_wall_width": side_wall_width,
        "slope_degrees": round(slope_degrees, 2),
        "acute_angle_deg": round(acute_angle_deg, 1),
        "obtuse_angle_deg": round(obtuse_angle_deg, 1),
        "bevel_offset_exact_mm": round(bevel_offset_exact_mm, 2),
        "bevel_offset_rounded_mm": bevel_offset_rounded_mm,
        "sloped_beam_length": sloped_beam_length,
        "stud_b3_left": stud_b3_left,
        "stud_b3_right": stud_b3_right,
        "stud_b4_left": stud_b4_left,
        "stud_b4_right": stud_b4_right,
        "stud_b2_left": stud_b2_left,
        "stud_b2_right": stud_b2_right,
        "mid_stud_x0": mid_stud_x0,
        "side_cell_1_width": side_cell_1_width,
        "side_cell_2_width": side_cell_2_width,
        "floor_cell_widths": floor_cell_widths,
        "front_stud_height": front_stud_height,
        "back_stud_height": back_stud_height,
        "front_cell_1_width": front_cell_1_width,
        "front_cell_2_width": front_cell_2_width,
        "front_right_cell_width": front_right_cell_width,
        "front_above_door_foam_h": front_above_door_foam_h,
        "roof_length": roof_length,
        "roof_width": roof_width,
        "roof_plug_length": roof_plug_length,
        "roof_plug_width": roof_plug_width,
        "roof_plug_cross_len": roof_plug_cross_len,
        "roof_cell_widths": roof_cell_widths,
        "timber_parts": timber_parts,
        "total_timber_pieces": total_timber_pieces,
        "straight_90_pieces": straight_90_pieces,
        "angled_pieces": angled_pieces,
        "packed_bars": packed_bars,
        "num_3m_bars": num_3m_bars,
        "total_linear_meters": total_linear_meters,
        "timber_volume_m3": timber_volume_m3,
        "bom_items": [
            {**it, "price": str(it["price"])} for it in bom_items
        ],
        "total_cost_byn": str(total_cost_byn)
    }


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
    canvas.text((45, 32), title_text, font=bold_font(29), fill=(255, 255, 255))
    canvas.text((45, 75), subtitle_text, font=regular_font(19), fill=(200, 220, 245))
    canvas.rectangle([width - 235, 32, width - 35, 103], fill=(255, 205, 70), outline=INK_COLOR, width=2)
    canvas.text((width - 215, 50), f"ЛИСТ {sheet_number} из 6", font=bold_font(25), fill=INK_COLOR)
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


def generate_sheet_six(m):
    B = m["beam_size"]
    FL = m["frame_length"]
    FW = m["frame_width"]
    IW = m["interior_frame_width"]
    diag_floor = round(math.hypot(FL, FW))
    cell_w = m["floor_cell_widths"][0]
    screw_main = "4,5×75 мм" if m["is_budget"] else "4,5×90 мм"

    sheet_image, canvas = create_blueprint_sheet(
        f"ШПАРГАЛКА НОВИЧКА: КАК ИМЕННО СКЛАДЫВАТЬ И СКРУЧИВАТЬ БРУСКИ {B}×{B} ММ",
        "Два вида стыка (угловой «Г» и перемычка «Т»), разметка 2 дырочек под саморезы и сборка первой рамки за 5 шагов",
        6
    )

    canvas.rectangle([45, 135, 965, 700], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    canvas.text((65, 150), "1. ДВА ВИДА СТЫКА В РАМКЕ: УГОЛ «Г» И ПЕРЕМЫЧКА «Т»", font=bold_font(19), fill=DIMENSION_BLUE)
    canvas.text((65, 180), "Длинный брус Д-1 накрывает торцы коротких брусков Д-2 сверху!", font=bold_font(16), fill=FASTENER_RED)

    bx, by = 110, 290
    beam_w = 780
    beam_h = 82

    canvas.rectangle([bx, by, bx + beam_w, by + beam_h], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.text((bx + 210, by + 28), f"Длинный брус Д-1 ({FL} мм)", font=bold_font(19), fill=INK_COLOR)

    canvas.rectangle([bx, by + beam_h, bx + beam_h, by + beam_h + 265], fill=PLINTH_TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.text((bx + 8, by + beam_h + 80), f"Крайний\nбрус Д-2\n({IW} мм)", font=bold_font(14), fill=INK_COLOR)

    canvas.line([(bx - 20, by), (bx - 20, by + beam_h + 130)], fill=ACCENT_GREEN, width=3)
    canvas.text((bx + beam_h + 14, by + beam_h + 18), "1) УГОЛ РАМКИ (буква «Г»):", font=bold_font(16), fill=ACCENT_GREEN)
    canvas.text((bx + beam_h + 14, by + beam_h + 44), "Края брусков ВРОВЕНЬ", font=regular_font(15), fill=INK_COLOR)
    canvas.text((bx + beam_h + 14, by + beam_h + 66), "(проведите пальцем сбоку —", font=regular_font(15), fill=INK_COLOR)
    canvas.text((bx + beam_h + 14, by + beam_h + 88), "ступеньки быть не должно!)", font=regular_font(15), fill=INK_COLOR)

    mx = bx + 445
    canvas.rectangle([mx, by + beam_h, mx + beam_h, by + beam_h + 265], fill=PLINTH_TIMBER_FILL, outline=INK_COLOR, width=3)
    canvas.text((mx + 8, by + beam_h + 80), f"Средний\nбрус Д-2\n({IW} мм)", font=bold_font(14), fill=INK_COLOR)
    canvas.text((mx + beam_h + 14, by + beam_h + 18), "2) ПЕРЕМЫЧКА (буква «Т»):", font=bold_font(16), fill=DIMENSION_BLUE)
    canvas.text((mx + beam_h + 14, by + beam_h + 44), f"Отмерили {cell_w} мм от угла,", font=regular_font(15), fill=INK_COLOR)
    canvas.text((mx + beam_h + 14, by + beam_h + 66), "провели черту карандашом", font=regular_font(15), fill=INK_COLOR)
    canvas.text((mx + beam_h + 14, by + beam_h + 88), "и приставили брус к черте!", font=regular_font(15), fill=INK_COLOR)

    canvas.line([(mx, by), (mx, by + beam_h + 25)], fill=ACCENT_GREEN, width=4)
    canvas.text((mx - 45, by - 26), f"Черта карандашом ({cell_w} мм)", font=bold_font(14), fill=ACCENT_GREEN)

    for jx in [bx, mx]:
        for dx_s in [23, 59]:
            sx = jx + dx_s
            canvas.line([(sx, by - 26), (sx, by + beam_h + 72)], fill=FASTENER_RED, width=5)
            canvas.rectangle([sx - 8, by - 30, sx + 8, by - 24], fill=FASTENER_RED, outline=INK_COLOR, width=1)

    canvas.text((bx, by - 64), f"В каждый торец крутим по 2 самореза {screw_main} сверху насквозь!", font=bold_font(15), fill=FASTENER_RED)

    canvas.rectangle([1005, 135, 1955, 700], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    canvas.text((1025, 150), f"2. КУДА ИМЕННО СВЕРЛИТЬ (ВИД НА ГРАНЬ БРУСА {B}×{B} ММ):", font=bold_font(19), fill=DIMENSION_BLUE)
    canvas.text((1025, 180), "Ставим 2 точки по диагонали (по 15 мм от краев), чтобы шурупы не столкнулись:", font=regular_font(15), fill=INK_COLOR)

    gx, gy = 1065, 265
    gw = 460
    gh = 155
    canvas.rectangle([gx + 155, gy, gx + 155 + gh, gy + gh], fill=(248, 238, 220), outline=INK_COLOR, width=2)
    canvas.rectangle([gx, gy, gx + gw, gy + gh], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    for yy in range(gy, gy + gh, 14):
        canvas.line([(gx + 155, yy), (gx + 155, min(yy + 8, gy + gh))], fill=DIMENSION_BLUE, width=3)
        canvas.line([(gx + 155 + gh, yy), (gx + 155 + gh, min(yy + 8, gy + gh))], fill=DIMENSION_BLUE, width=3)

    canvas.text((gx + 15, gy + 55), "Брус Д-1\n(сверху)", font=bold_font(16), fill=INK_COLOR)
    canvas.text((gx + 95, gy + gh + 14), f"Пунктир — торец бруса Д-2 снизу (квадрат {B}×{B} мм)", font=bold_font(15), fill=DIMENSION_BLUE)

    p1x, p1y = gx + 155 + 46, gy + 46
    p2x, p2y = gx + 155 + gh - 46, gy + gh - 46
    for px, py in [(p1x, p1y), (p2x, p2y)]:
        canvas.ellipse([px - 10, py - 10, px + 10, py + 10], fill=FASTENER_RED, outline=(255, 255, 255), width=2)

    canvas.line([(p1x + 12, p1y), (gx + gw + 15, p1y)], fill=FASTENER_RED, width=2)
    canvas.line([(p2x + 12, p2y), (gx + gw + 15, p2y)], fill=FASTENER_RED, width=2)
    canvas.text((gx + gw + 22, p1y - 12), "Дырочка №1 (сверло 3,5–4 мм)", font=bold_font(15), fill=FASTENER_RED)
    canvas.text((gx + gw + 22, p2y - 12), "Дырочка №2 (после диагоналей!)", font=bold_font(15), fill=FASTENER_RED)

    canvas.text((1025, 495), "ПОЧЕМУ СНАЧАЛА КРУТИМ 1-Й САМОРЕЗ, А ПОТОМ МЕРЯЕМ ДИАГОНАЛИ:", font=bold_font(16), fill=ACCENT_GREEN)
    canvas.text((1025, 526), "• Пока в каждом из 4 углов закручено только по 1 саморезу, он работает как", font=regular_font(15), fill=INK_COLOR)
    canvas.text((1025, 552), f"  шарнир — рамку легко чуть-чуть подтолкнуть рукой, чтобы обе диагонали", font=regular_font(15), fill=INK_COLOR)
    canvas.text((1025, 578), f"  накрест стали абсолютно одинаковыми ({diag_floor} мм и {diag_floor} мм)!", font=regular_font(15), fill=INK_COLOR)
    canvas.text((1025, 608), "• Как только диагонали совпали — сверлим дырочку №2 и закручиваем второй", font=regular_font(15), fill=INK_COLOR)
    canvas.text((1025, 634), "  саморез в каждый угол: теперь углы 90° заблокированы намертво!", font=regular_font(15), fill=INK_COLOR)

    canvas.rectangle([45, 725, 1955, 1360], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    canvas.text((65, 742), "3. ПОШАГОВЫЙ КОМИКС: КАК ВЫ СОБИРАЕТЕ ПЕРВУЮ РАМКУ ПОЛА ЗА 5 ПРОСТЫХ ШАГОВ", font=bold_font(21), fill=DIMENSION_BLUE)

    steps_comic = [
        ("ШАГ А: Сложили коробку", [
            f"Кладем на лист ОСБ 2 длинных",
            f"бруса Д-1 ({FL}) и между ними",
            f"по краям 2 коротких Д-2 ({IW}).",
            "На всех 4 углах ровняем края",
            "пальцем вровень (буква «Г»)."
        ]),
        ("ШАГ Б: По 1 шурупу в угол", [
            "В каждом из 4 углов сверлим",
            "1 дырочку сквозь Д-1, наживляем",
            f"саморез {screw_main}, дедушка",
            "прижимает угол ногой —",
            "стягиваем 4 угла по 1 шурупу."
        ]),
        ("ШАГ В: Ровняем диагонали", [
            "Меряем рулеткой накрест от",
            "угла до угла. Должно быть",
            f"{diag_floor} мм и {diag_floor} мм. Если одна",
            "длиннее — легко толкаем этот",
            "угол рукой, пока не совпадут!"
        ]),
        ("ШАГ Г: 2-й шуруп в углы", [
            "Когда диагонали равны, сверлим",
            "и крутим в каждый из 4 углов",
            f"ВТОРОЙ саморез {screw_main}",
            "по диагонали от первого.",
            "Углы 90° зажаты намертво!"
        ]),
        ("ШАГ Д: Ставим перемычки", [
            "Отмеряем рулеткой от углов",
            f"по {cell_w} мм внутрь, ставим черту,",
            "вставляем 2 средних бруса Д-2",
            "(вот тут стык буквой «Т»!) и",
            "прикручиваем их по 2 шурупа."
        ])
    ]

    for idx, (st_title, st_lines) in enumerate(steps_comic):
        cx0 = 65 + idx * 376
        cy0 = 790
        canvas.rectangle([cx0, cy0, cx0 + 358, cy0 + 545], fill=(248, 250, 253), outline=DIMENSION_BLUE, width=2)
        canvas.rectangle([cx0, cy0, cx0 + 358, cy0 + 48], fill=DIMENSION_BLUE)
        canvas.text((cx0 + 14, cy0 + 12), st_title, font=bold_font(17), fill=(255, 255, 255))

        ix, iy = cx0 + 50, cy0 + 72
        iw, ih = 258, 165
        if idx == 0:
            canvas.rectangle([ix, iy, ix + iw, iy + 22], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
            canvas.rectangle([ix, iy + ih - 22, ix + iw, iy + ih], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
            canvas.rectangle([ix, iy + 22, ix + 22, iy + ih - 22], fill=PLINTH_TIMBER_FILL, outline=INK_COLOR, width=2)
            canvas.rectangle([ix + iw - 22, iy + 22, ix + iw, iy + ih - 22], fill=PLINTH_TIMBER_FILL, outline=INK_COLOR, width=2)
        elif idx == 1:
            canvas.rectangle([ix, iy, ix + iw, iy + 22], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
            canvas.rectangle([ix, iy + ih - 22, ix + iw, iy + ih], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
            canvas.rectangle([ix, iy + 22, ix + 22, iy + ih - 22], fill=PLINTH_TIMBER_FILL, outline=INK_COLOR, width=2)
            canvas.rectangle([ix + iw - 22, iy + 22, ix + iw, iy + ih - 22], fill=PLINTH_TIMBER_FILL, outline=INK_COLOR, width=2)
            for sx_i, sy_i in [(ix + 11, iy + 11), (ix + iw - 11, iy + 11), (ix + 11, iy + ih - 11), (ix + iw - 11, iy + ih - 11)]:
                canvas.ellipse([sx_i - 5, sy_i - 5, sx_i + 5, sy_i + 5], fill=FASTENER_RED)
        elif idx == 2:
            canvas.rectangle([ix, iy, ix + iw, iy + ih], outline=INK_COLOR, width=3)
            canvas.line([(ix, iy), (ix + iw, iy + ih)], fill=ACCENT_GREEN, width=3)
            canvas.line([(ix + iw, iy), (ix, iy + ih)], fill=ACCENT_GREEN, width=3)
            canvas.text((ix + 65, iy + ih // 2 - 12), f"{diag_floor} = {diag_floor}", font=bold_font(17), fill=ACCENT_GREEN)
        elif idx == 3:
            canvas.rectangle([ix, iy, ix + iw, iy + 22], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
            canvas.rectangle([ix, iy + ih - 22, ix + iw, iy + ih], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
            canvas.rectangle([ix, iy + 22, ix + 22, iy + ih - 22], fill=PLINTH_TIMBER_FILL, outline=INK_COLOR, width=2)
            canvas.rectangle([ix + iw - 22, iy + 22, ix + iw, iy + ih - 22], fill=PLINTH_TIMBER_FILL, outline=INK_COLOR, width=2)
            for sx_i, sy_i in [
                (ix + 7, iy + 7), (ix + 15, iy + 15),
                (ix + iw - 15, iy + 7), (ix + iw - 7, iy + 15),
                (ix + 7, iy + ih - 15), (ix + 15, iy + ih - 7),
                (ix + iw - 15, iy + ih - 15), (ix + iw - 7, iy + ih - 7)
            ]:
                canvas.ellipse([sx_i - 4, sy_i - 4, sx_i + 4, sy_i + 4], fill=FASTENER_RED)
        elif idx == 4:
            canvas.rectangle([ix, iy, ix + iw, iy + 22], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
            canvas.rectangle([ix, iy + ih - 22, ix + iw, iy + ih], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
            for bx_i in [0, 82, 158, iw - 22]:
                canvas.rectangle([ix + bx_i, iy + 22, ix + bx_i + 22, iy + ih - 22], fill=PLINTH_TIMBER_FILL, outline=INK_COLOR, width=2)
                canvas.ellipse([ix + bx_i + 7, iy + 7, ix + bx_i + 15, iy + 15], fill=FASTENER_RED)
                canvas.ellipse([ix + bx_i + 7, iy + ih - 15, ix + bx_i + 15, iy + ih - 7], fill=FASTENER_RED)

        ty = cy0 + 265
        for tl in st_lines:
            canvas.text((cx0 + 16, ty), tl, font=regular_font(16), fill=INK_COLOR)
            ty += 36

    sheet_image.save(os.path.join(PLANS_OUTPUT_DIR, "06_beginner_screwing_guide.png"))
    return sheet_image


def render_all_sheets_and_readme(m):
    B = m["beam_size"]
    FL = m["frame_length"]
    FW = m["frame_width"]
    IL = m["interior_frame_length"]
    IW = m["interior_frame_width"]
    CL = m["clean_room_length"]
    CW = m["clean_room_width"]
    FH = m["front_wall_height"]
    BH = m["back_wall_height"]
    is_budget = m["is_budget"]
    outer_label = "Вагонка 16 мм"
    roof_cov_label = "Рубероид РКПО-350 в 2 слоя" if is_budget else "Мягкая черепица Технониколь"

    s1_img, d1 = create_blueprint_sheet(
        f"ПРОЕКТ ЗИМНЕЙ БУДКИ {IL}×{IW} мм ({'БЮДЖЕТ 30 ММ' if is_budget else 'ОСНОВНОЙ 50 ММ'} — {m['total_cost_byn']} BYN)",
        f"Брус {B}×{B} (лесхоз) | Техноплекс {m['foam_thickness']} мм | Пол: фанера 10, стены: 4 мм | Снаружи: {outer_label} + наличник ТЗСИ | Сетка от подкопа",
        1
    )
    d1.text((60, 138), "1. ВИД СВЕРХУ (СТАЛЬНАЯ СЕТКА В ГРУНТЕ ОТ ПОДКОПА + СЛОИ СТЕН)", font=bold_font(23), fill=INK_COLOR)
    scale = 0.56
    ox, oy = 225, 290
    fw, fh = int(FL * scale), int(FW * scale)
    vag_px = int(16 * scale)
    b_px = int(B * scale)
    ply_px = int(6 * scale)
    mm_x, mm_y = int(250 * scale), int(225 * scale)

    m_left, m_top, m_right, m_bot = ox - mm_x, oy - mm_y, ox + fw + mm_x, oy + fh + mm_y
    d1.rectangle([m_left, m_top, m_right, m_bot], fill=(238, 243, 248), outline=MESH_COLOR, width=3)
    for gx in range(m_left, m_right, int(75 * scale)):
        d1.line([(gx, m_top), (gx, m_bot)], fill=(205, 214, 224), width=1)
    for gy in range(m_top, m_bot, int(75 * scale)):
        d1.line([(m_left, gy), (m_right, gy)], fill=(205, 214, 224), width=1)
    d1.text((m_left + 12, m_top + 8), "Стальная кладочная сетка в земле: 3 карты 0,5×2,0 м (площадь 2000×1500 мм)", font=bold_font(15), fill=INK_COLOR)
    d1.text((m_left + 12, m_bot - 26), "Сетка работает без плитки: когти упираются в стальные прутья, подрыть будку невозможно!", font=bold_font(14), fill=ACCENT_GREEN)

    d1.rectangle([ox - vag_px, oy - vag_px, ox + fw + vag_px, oy + fh + vag_px], fill=VAGONKA_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([ox, oy, ox + fw, oy + fh], fill=PENOPLEX_FILL, outline=INK_COLOR, width=3)
    d1.rectangle([ox + b_px, oy + b_px, ox + fw - b_px, oy + fh - b_px], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([ox + b_px + ply_px, oy + b_px + ply_px, ox + fw - b_px - ply_px, oy + fh - b_px - ply_px], fill=(255, 252, 242), outline=INK_COLOR, width=3)

    door_x_left_mm = B + m["warm_corner_length"]
    door_x_right_mm = door_x_left_mm + m["door_width"]
    front_stud_positions = [0, B + m["front_cell_1_width"], door_x_left_mm - B, door_x_right_mm, FL - B]
    for sx in front_stud_positions:
        d1.rectangle([ox + int(sx * scale), oy + fh - b_px, ox + int((sx + B) * scale), oy + fh], fill=TIMBER_FILL, outline=INK_COLOR, width=2)

    bx_cur = 0
    for cw in m["floor_cell_widths"]:
        d1.rectangle([ox + int(bx_cur * scale), oy, ox + int((bx_cur + B) * scale), oy + b_px], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
        bx_cur += B + cw
    d1.rectangle([ox + int(bx_cur * scale), oy, ox + int((bx_cur + B) * scale), oy + b_px], fill=TIMBER_FILL, outline=INK_COLOR, width=2)

    mid_sy = B + m["mid_stud_x0"]
    d1.rectangle([ox, oy + int(mid_sy * scale), ox + b_px, oy + int((mid_sy + B) * scale)], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([ox + fw - b_px, oy + int(mid_sy * scale), ox + fw, oy + int((mid_sy + B) * scale)], fill=TIMBER_FILL, outline=INK_COLOR, width=2)

    dlx, drx = ox + int(door_x_left_mm * scale), ox + int(door_x_right_mm * scale)
    d1.rectangle([dlx, oy + fh - b_px - ply_px - 4, drx, oy + fh + vag_px + 4], fill=(238, 243, 248), outline=(238, 243, 248))
    d1.line([(dlx, oy + fh - b_px - ply_px), (dlx, oy + fh + vag_px)], fill=INK_COLOR, width=3)
    d1.line([(drx, oy + fh - b_px - ply_px), (drx, oy + fh + vag_px)], fill=INK_COLOR, width=3)
    for dash_x in range(dlx, drx, 16):
        d1.line([(dash_x, oy + fh), (min(dash_x + 8, drx), oy + fh)], fill=FASTENER_RED, width=3)

    d1.text((ox + b_px + 22, oy + b_px + 34), f"ГЛУХОЙ ТЕПЛЫЙ УГОЛ ({m['warm_corner_length']} × {IW} мм)", font=bold_font(20), fill=ACCENT_GREEN)
    d1.text((ox + b_px + 22, oy + b_px + 66), "• Ветер из входа сюда НЕ попадает", font=regular_font(17), fill=INK_COLOR)
    d1.text((ox + b_px + 22, oy + b_px + 92), "• Все размеры вычислены Python-моделью", font=regular_font(17), fill=INK_COLOR)
    d1.text((ox + b_px + 22, oy + b_px + 145), "ЧИСТЫЙ РАЗМЕР ВНУТРИ:", font=bold_font(18), fill=INK_COLOR)
    d1.text((ox + b_px + 22, oy + b_px + 172), f"{IL} × {IW} мм (по каркасу {B}×{B})", font=mono_font(18), fill=DIMENSION_BLUE)
    d1.text((ox + b_px + 22, oy + b_px + 198), f"{CL} × {CW} мм (по внутренней фанере)", font=mono_font(17), fill=MUTED_TEXT_COLOR)
    d1.text((dlx + 6, oy + fh - 102), "ВХОД (ЛАЗ)", font=bold_font(17), fill=FASTENER_RED)
    d1.text((dlx + 6, oy + fh - 80), f"{m['door_width']} × {m['door_height']} мм", font=bold_font(17), fill=FASTENER_RED)

    draw_dimension_arrow(d1, ox, oy, ox + fw, oy, f"{FL} мм (каркас будки)", 0, -1, offset_distance=42)
    draw_dimension_arrow(d1, ox + b_px, oy + b_px, ox + fw - b_px, oy + b_px, f"{IL} мм (внутри)", 0, 1, offset_distance=22)
    draw_dimension_arrow(d1, ox, oy, ox, oy + fh, f"{FW} мм", -1, 0, offset_distance=65)
    draw_dimension_arrow(d1, ox + fw - b_px, oy + b_px, ox + fw - b_px, oy + fh - b_px, f"{IW} мм", 1, 0, offset_distance=65)
    draw_dimension_arrow(d1, ox + b_px, oy + fh, dlx, oy + fh, f"{m['warm_corner_length']} мм (угол)", 0, 1, offset_distance=48, color=ACCENT_GREEN)
    draw_dimension_arrow(d1, dlx, oy + fh, drx, oy + fh, f"{m['door_width']} мм (лаз)", 0, 1, offset_distance=48, color=FASTENER_RED)
    draw_dimension_arrow(d1, drx, oy + fh, ox + fw - b_px, oy + fh, f"{m['door_right_inner_offset']}", 0, 1, offset_distance=48, color=DIMENSION_BLUE)

    d1.text((1090, 138), f"2. БОКОВОЙ РАЗРЕЗ (УКЛОН {m['slope_degrees']}° + ГИДРОИЗОЛЯЦИЯ ЦОКОЛЯ)", font=bold_font(22), fill=INK_COLOR)
    sx0, sy0 = 1235, 855
    plinth_h = int(B * scale)
    ply_h = int(8 * scale)
    floor_h = int(B * scale)
    paver_top = sy0 + ply_h + plinth_h
    ground_y = paver_top + 6
    ml_s, mr_s = sx0 - mm_y, sx0 + fh + mm_y

    d1.rectangle([sx0 - 4, paver_top, sx0 + fh + 4, ground_y], fill=(45, 45, 50), outline=INK_COLOR, width=1)
    d1.line([(ml_s - 25, ground_y), (mr_s + 25, ground_y)], fill=ACCENT_GREEN, width=4)
    for dm in range(ml_s, mr_s, 14):
        d1.line([(dm, ground_y + 6), (min(dm + 9, mr_s), ground_y + 6)], fill=MESH_COLOR, width=4)
    d1.text((ml_s - 10, ground_y + 14), "Стальная сетка в грунте + битумная гидроизоляция (из остатка рулона крыши) под цоколем", font=bold_font(14), fill=ACCENT_GREEN)

    d1.rectangle([sx0, sy0 + ply_h, sx0 + fh, paver_top], fill=(235, 220, 195), outline=INK_COLOR, width=2)
    for co in [0, int((FW - B) // 2 * scale), fh - b_px]:
        d1.rectangle([sx0 + co, sy0 + ply_h, sx0 + co + b_px, paver_top], fill=PLINTH_TIMBER_FILL, outline=INK_COLOR, width=2)
    d1.text((sx0 + 38, sy0 + ply_h + 4), f"Закрытый цоколь {B}×{B} по кругу (без щелей для лап!)", font=bold_font(14), fill=INK_COLOR)

    d1.rectangle([sx0, sy0, sx0 + fh, sy0 + ply_h], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([sx0, sy0 - floor_h, sx0 + fh, sy0], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([sx0, sy0 - floor_h, sx0 + b_px, sy0], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([sx0 + fh - b_px, sy0 - floor_h, sx0 + fh, sy0], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    fl_top = sy0 - floor_h - ply_h
    d1.rectangle([sx0, fl_top, sx0 + fh, sy0 - floor_h], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)

    hb_px, hf_px = int(BH * scale), int(FH * scale)
    d1.rectangle([sx0, fl_top - hb_px, sx0 + b_px, fl_top], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([sx0, fl_top - b_px, sx0 + b_px, fl_top], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([sx0, fl_top - hb_px, sx0 + b_px, fl_top - hb_px + b_px], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([sx0 - vag_px, fl_top - hb_px, sx0, paver_top], fill=VAGONKA_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([sx0 + b_px, fl_top - hb_px, sx0 + b_px + ply_h, fl_top], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)

    d1.rectangle([sx0 + fh - b_px, fl_top - hf_px, sx0 + fh, fl_top], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([sx0 + fh - b_px, fl_top - b_px, sx0 + fh, fl_top], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([sx0 + fh - b_px, fl_top - hf_px, sx0 + fh, fl_top - hf_px + b_px], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([sx0 + fh, fl_top - hf_px, sx0 + fh + vag_px, paver_top], fill=VAGONKA_FILL, outline=INK_COLOR, width=2)
    d1.rectangle([sx0 + fh - b_px - ply_h, fl_top - hf_px, sx0 + fh - b_px, fl_top], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)
    d1.line([(sx0 + b_px, fl_top - hb_px), (sx0 + fh - b_px, fl_top - hf_px)], fill=INK_COLOR, width=3)

    ov_b, ov_f = int(80 * scale), int(120 * scale)
    rx1, ry1 = sx0 - ov_b, fl_top - hb_px + int(10 * scale)
    rx2, ry2 = sx0 + fh + ov_f, fl_top - hf_px - int(14 * scale)
    d1.line([(rx1, ry1 - 12), (rx2, ry2 - 12)], fill=FASTENER_RED, width=8)
    d1.line([(rx1, ry1 - 4), (rx2, ry2 - 4)], fill=INK_COLOR, width=4)

    px1, py1 = sx0 + b_px + ply_h + 4, fl_top - hb_px
    px2, py2 = sx0 + fh - b_px - ply_h - 4, fl_top - hf_px
    d1.polygon([(px1, py1), (px2, py2), (px2, py2 + b_px), (px1, py1 + b_px)], fill=PENOPLEX_FILL, outline=INK_COLOR)
    d1.line([(sx0 + 215, py1 + 25), (sx0 + 215, py1 + 92)], fill=INK_COLOR, width=2)
    d1.text((sx0 + 48, py1 + 96), f"Цельный ОСБ-3 9 мм + {roof_cov_label}", font=bold_font(15), fill=INK_COLOR)
    d1.text((sx0 + 48, py1 + 120), f"+ теплая пробка Техноплекс {m['foam_thickness']} мм ({m['roof_plug_length']}×{m['roof_plug_width']})", font=regular_font(15), fill=FASTENER_RED)

    d1.ellipse([sx0 - 15, fl_top - hb_px - 10, sx0 + 7, fl_top - hb_px + 12], fill=FASTENER_RED, outline=INK_COLOR, width=2)
    d1.line([(sx0 - 8, fl_top - hb_px - 8), (sx0 - 45, fl_top - hb_px - 65)], fill=FASTENER_RED, width=3)
    d1.text((sx0 - 140, fl_top - hb_px - 110), "2 ПЕТЛИ СЗАДИ\n(крыша поднимается)", font=bold_font(17), fill=FASTENER_RED)

    draw_dimension_arrow(d1, sx0, fl_top, sx0, fl_top - hb_px, f"{BH} мм (зад)", -1, 0, offset_distance=70)
    draw_dimension_arrow(d1, sx0 + fh, fl_top, sx0 + fh, fl_top - hf_px, f"{FH} мм (перед)", 1, 0, offset_distance=75)
    draw_dimension_arrow(d1, sx0, paver_top, sx0 + fh, paver_top, f"{FW} мм (ширина будки)", 0, 1, offset_distance=75)

    d1.rectangle([45, 985, 1955, 1360], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    d1.text((65, 1002), "УТВЕРЖДЕННАЯ КОНСТРУКЦИЯ (ВСЕ РАЗМЕРЫ РАССЧИТАНЫ И ПРОВЕРЕНЫ PYTHON-СКРИПТОМ):", font=bold_font(22), fill=DIMENSION_BLUE)

    legend_entries = [
        (TIMBER_FILL, f"Брус {B}×{B} мм (каркас)"),
        (PENOPLEX_FILL, f"Техноплекс {m['foam_thickness']} мм"),
        (PLYWOOD_FILL, "Фанера 10 / 4 мм + ОСБ 9"),
        (VAGONKA_FILL, f"{outer_label} + наличник ТЗСИ"),
        ((205, 214, 224), "Стальная сетка от подкопа")
    ]
    lx = 65
    for sc, sl in legend_entries:
        d1.rectangle([lx, 1045, lx + 34, 1075], fill=sc, outline=INK_COLOR, width=2)
        d1.text((lx + 44, 1047), sl, font=bold_font(17), fill=INK_COLOR)
        lx += 375

    steps_1 = [
        "ШАГ 0 (Основание БЕЗ плитки): Укладываем на выровненную землю 3 карты стальной кладочной сетки 0,5×2,0 м (площадь 200×150 см,",
        "      присыпаем 2–3 см песка). Сетка не дает собаке рыть яму — будка никогда не просядет!",
        f"ШАГ 1 (Дно + гидроизоляция цоколя): Скручиваем раму пола {FL}×{FW} мм из бруса {B}×{B}, снизу крепим закрытый цоколь {B}×{B} мм.",
        "      К нижней грани цоколя прибиваем полоски битумной гидроизоляции (бесплатный остаток от рулона крыши!) — дерево не намокнет!",
        f"ШАГ 2–5 (Пропитка и сборка): Пропитываем брус, черновой пол и изнанку/торцы фанеры биозащитой PentaStyle (внутри к щенкам не мазать!),",
        f"      утепляем Техноплексом {m['foam_thickness']} мм (сучки вагонки запениваем изнутри), снаружи красим аквалазурью и вешаем крышу из ОСБ-3 на 2 петли."
    ]
    sy_t = 1094
    for st in steps_1:
        d1.text((65, sy_t), st, font=regular_font(16), fill=INK_COLOR)
        sy_t += 40
    s1_img.save(os.path.join(PLANS_OUTPUT_DIR, "01_general_view_and_layers.png"))

    s2_img, d2 = create_blueprint_sheet(
        f"ЧЕРТЕЖИ КАРКАСА ИЗ БРУСА {B}×{B} ММ — ЩИТЫ №1 (ДНО + ЦОКОЛЬ), №2 (ПЕРЕД), №3 (ЗАД)",
        "Все 27 брусков на этом листе пилятся строго под 90°! Красные точки — саморезы по дереву (сквозь обвязку в торец стойки)",
        2
    )
    sc2 = 0.48
    b2 = int(B * sc2)
    d2.text((55, 138), f"ЩИТ №1: РАМА ПОЛА ({FL}×{FW}) + ЗАКРЫТЫЙ ЦОКОЛЬ СНИЗУ", font=bold_font(22), fill=INK_COLOR)
    fx, fy = 145, 225
    fw2, fh2 = int(FL * sc2), int(FW * sc2)
    d2.rectangle([fx, fy, fx + fw2, fy + fh2], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    d2.rectangle([fx, fy, fx + fw2, fy + b2], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d2.rectangle([fx, fy + fh2 - b2, fx + fw2, fy + fh2], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d2.text((fx + 35, fy + 2), f"Д-1 / Ц-1: {FL} мм (90°)", font=bold_font(15), fill=INK_COLOR)
    d2.text((fx + 35, fy + fh2 - b2 + 2), f"Д-1 / Ц-1: {FL} мм (90°)", font=bold_font(15), fill=INK_COLOR)

    cur_jx = 0
    for idx_c, cw in enumerate(m["floor_cell_widths"]):
        px = fx + int(cur_jx * sc2)
        d2.rectangle([px, fy + b2, px + b2, fy + fh2 - b2], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
        draw_screw_point(d2, px + b2 // 2, fy + b2 // 2)
        draw_screw_point(d2, px + b2 // 2, fy + fh2 - b2 // 2)
        cx = fx + int((cur_jx + B + cw / 2) * sc2)
        cy = fy + fh2 // 2
        d2.text((cx - 70, cy - 35), f"Техноплекс {m['foam_thickness']}", font=bold_font(15), fill=INK_COLOR)
        d2.text((cx - 60, cy - 10), f"{cw} × {IW} мм", font=mono_font(16), fill=DIMENSION_BLUE)
        d2.text((cx - 50, cy + 16), f"(Ячейка {idx_c + 1})", font=regular_font(15), fill=INK_COLOR)
        draw_dimension_arrow(d2, fx + int((cur_jx + B) * sc2), fy + fh2, fx + int((cur_jx + B + cw) * sc2), fy + fh2, f"{cw} мм", 0, 1, offset_distance=32, color=ACCENT_GREEN)
        cur_jx += B + cw
    px_last = fx + int(cur_jx * sc2)
    d2.rectangle([px_last, fy + b2, px_last + b2, fy + fh2 - b2], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    draw_screw_point(d2, px_last + b2 // 2, fy + b2 // 2)
    draw_screw_point(d2, px_last + b2 // 2, fy + fh2 - b2 // 2)

    draw_dimension_arrow(d2, fx, fy, fx + fw2, fy, f"{FL} мм", 0, -1, offset_distance=35)
    draw_dimension_arrow(d2, fx, fy, fx, fy + fh2, f"{FW} мм", -1, 0, offset_distance=65)
    draw_dimension_arrow(d2, fx + fw2, fy + b2, fx + fw2, fy + fh2 - b2, f"{IW} мм (4 шт. Д-2)", 1, 0, offset_distance=85)

    d2.rectangle([55, 695, 955, 835], fill=(255, 255, 255), outline=INK_COLOR, width=2)
    d2.text((70, 704), f"Детали Щита №1 (Рама пола + Закрытый цоколь из бруса {B}×{B} мм — все углы 90°):", font=bold_font(17), fill=DIMENSION_BLUE)
    d2.text((70, 732), f"• Рама пола: Д-1 ({FL} мм — 2 шт.) + Д-2 ({IW} мм — 4 шт.).", font=regular_font(16), fill=INK_COLOR)
    d2.text((70, 758), "• Закрытый цоколь снизу (подбивается полосами битумной гидроизоляции от остатка крыши):", font=bold_font(15), fill=FASTENER_RED)
    d2.text((70, 782), f"  Ц-1 продольные ({FL} мм — 2 шт.) + Ц-2 поперечные ({IW} мм — 3 шт., по краям и центру).", font=regular_font(16), fill=INK_COLOR)
    d2.text((70, 806), f"• Фанера пола: сверху чистовая 10 мм ({FL}×{FW}), снизу черновая 4 мм ({FL}×{FW}).", font=regular_font(16), fill=INK_COLOR)

    d2.text((1045, 138), f"ЩИТ №2: ПЕРЕДНЯЯ СТЕНКА С ЛАЗОМ ({FL} × {FH} мм)", font=bold_font(22), fill=INK_COLOR)
    wx, wy = 1145, 225
    ww, wh = int(FL * sc2), int(FH * sc2)
    d2.rectangle([wx, wy, wx + ww, wy + wh], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    d2.rectangle([wx, wy, wx + ww, wy + b2], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d2.rectangle([wx, wy + wh - b2, wx + ww, wy + wh], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d2.text((wx + ww // 2 - 90, wy + 2), f"П-1: {FL} мм (90°)", font=bold_font(16), fill=INK_COLOR)
    d2.text((wx + 35, wy + wh - b2 + 2), f"П-1: {FL} мм (90°)", font=bold_font(16), fill=INK_COLOR)

    for sx in front_stud_positions:
        px = wx + int(sx * sc2)
        d2.rectangle([px, wy + b2, px + b2, wy + wh - b2], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
        draw_screw_point(d2, px + b2 // 2, wy + b2 // 2)
        draw_screw_point(d2, px + b2 // 2, wy + wh - b2 // 2)

    laz_h_px = int(m["door_height"] * sc2)
    lxs = wx + int(door_x_left_mm * sc2)
    lxe = wx + int(door_x_right_mm * sc2)
    lyt = (wy + wh - b2) - laz_h_px
    d2.rectangle([lxs, lyt, lxe, wy + wh - b2], fill=(255, 255, 255), outline=FASTENER_RED, width=3)
    d2.rectangle([lxs, lyt - b2, lxe, lyt], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    draw_screw_point(d2, lxs - b2 // 2, lyt - b2 // 2)
    draw_screw_point(d2, lxe + b2 // 2, lyt - b2 // 2)
    d2.text((lxs + 20, lyt - b2 + 2), f"П-3: {m['door_width']} мм", font=bold_font(15), fill=INK_COLOR)
    d2.text((lxs + 18, lyt + 55), "ОКНО ЛАЗА", font=bold_font(19), fill=FASTENER_RED)
    d2.text((lxs + 12, lyt + 82), f"{m['door_width']} × {m['door_height']} мм", font=mono_font(18), fill=FASTENER_RED)
    d2.text((wx + int((B + 10) * sc2), wy + int(250 * sc2)), f"Техноплекс\n{m['front_cell_1_width']}×{m['front_stud_height']} мм", font=bold_font(15), fill=INK_COLOR)
    d2.text((wx + int((2 * B + m['front_cell_1_width'] + 10) * sc2), wy + int(250 * sc2)), f"Техноплекс\n{m['front_cell_2_width']}×{m['front_stud_height']} мм", font=bold_font(15), fill=INK_COLOR)
    d2.text((lxs + 15, wy + b2 + 8), f"Техноплекс\n{m['door_width']}×{m['front_above_door_foam_h']} мм", font=bold_font(14), fill=INK_COLOR)

    draw_dimension_arrow(d2, wx, wy, wx + ww, wy, f"{FL} мм", 0, -1, offset_distance=35)
    draw_dimension_arrow(d2, wx, wy, wx, wy + wh, f"{FH} мм (перед)", -1, 0, offset_distance=75)
    draw_dimension_arrow(d2, wx + ww, wy + b2, wx + ww, wy + wh - b2, f"{m['front_stud_height']} мм (5 шт. П-2)", 1, 0, offset_distance=85)
    draw_dimension_arrow(d2, wx + int(B * sc2), wy + wh, wx + int((B + m["front_cell_1_width"]) * sc2), wy + wh, f"{m['front_cell_1_width']} мм", 0, 1, offset_distance=35, color=ACCENT_GREEN)
    draw_dimension_arrow(d2, wx + int((2 * B + m["front_cell_1_width"]) * sc2), wy + wh, wx + int((door_x_left_mm - B) * sc2), wy + wh, f"{m['front_cell_2_width']} мм", 0, 1, offset_distance=35, color=ACCENT_GREEN)
    draw_dimension_arrow(d2, lxs, wy + wh, lxe, wy + wh, f"{m['door_width']} мм (лаз)", 0, 1, offset_distance=35, color=FASTENER_RED)
    draw_dimension_arrow(d2, lxe + b2, wy + wh, wx + ww - b2, wy + wh, f"{m['front_right_cell_width']}", 0, 1, offset_distance=35, color=DIMENSION_BLUE)

    d2.text((55, 865), f"ЩИТ №3: ЗАДНЯЯ СТЕНКА ({FL} × {BH} мм — НИЖЕ НА {m['height_drop']} ММ)", font=bold_font(22), fill=INK_COLOR)
    bx, by = 145, 945
    bw, bh = int(FL * sc2), int(BH * sc2)
    d2.rectangle([bx, by, bx + bw, by + bh], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    d2.rectangle([bx, by, bx + bw, by + b2], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d2.rectangle([bx, by + bh - b2, bx + bw, by + bh], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d2.text((bx + bw // 2 - 90, by + 2), f"З-1: {FL} мм (90°)", font=bold_font(16), fill=INK_COLOR)
    d2.text((bx + bw // 2 - 90, by + bh - b2 + 2), f"З-1: {FL} мм (90°)", font=bold_font(16), fill=INK_COLOR)

    cur_bx = 0
    for cw in m["floor_cell_widths"]:
        px = bx + int(cur_bx * sc2)
        d2.rectangle([px, by + b2, px + b2, by + bh - b2], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
        draw_screw_point(d2, px + b2 // 2, by + b2 // 2)
        draw_screw_point(d2, px + b2 // 2, by + bh - b2 // 2)
        cx = bx + int((cur_bx + B + cw / 2) * sc2)
        cy = by + bh // 2
        d2.text((cx - 70, cy - 25), f"Техноплекс {m['foam_thickness']}", font=bold_font(15), fill=INK_COLOR)
        d2.text((cx - 60, cy), f"{cw} × {m['back_stud_height']} мм", font=mono_font(16), fill=DIMENSION_BLUE)
        draw_dimension_arrow(d2, bx + int((cur_bx + B) * sc2), by + bh, bx + int((cur_bx + B + cw) * sc2), by + bh, f"{cw} мм", 0, 1, offset_distance=32, color=ACCENT_GREEN)
        cur_bx += B + cw
    px_b_last = bx + int(cur_bx * sc2)
    d2.rectangle([px_b_last, by + b2, px_b_last + b2, by + bh - b2], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    draw_screw_point(d2, px_b_last + b2 // 2, by + b2 // 2)
    draw_screw_point(d2, px_b_last + b2 // 2, by + bh - b2 // 2)

    draw_dimension_arrow(d2, bx, by, bx + bw, by, f"{FL} мм", 0, -1, offset_distance=30)
    draw_dimension_arrow(d2, bx, by, bx, by + bh, f"{BH} мм (зад)", -1, 0, offset_distance=70)
    draw_dimension_arrow(d2, bx + bw, by + b2, bx + bw, by + bh - b2, f"{m['back_stud_height']} мм (4 шт. З-2)", 1, 0, offset_distance=85)

    d2.rectangle([1045, 695, 1945, 1345], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    d2.text((1070, 715), "СПЕЦИФИКАЦИЯ ЩИТОВ №2 И №3 (АВТОРАСЧЕТ PYTHON):", font=bold_font(21), fill=DIMENSION_BLUE)
    spec23 = [
        f"Щит №2 (Передняя стенка {FL} × {FH} мм — все торцы 90°):",
        f"  • Брус П-1 (верх и низ): {FL} мм — 2 шт.",
        f"  • Брус П-2 (стойки вертикальные): {m['front_stud_height']} мм — 5 шт.",
        f"  • Брус П-3 (перемычка над лазом): {m['door_width']} мм — 1 шт.",
        f"  • Фанера 4 мм изнутри: {IL} × {FH} мм (вырезать окно {m['door_width']}×{m['door_height']})",
        "",
        f"Щит №3 (Задняя стенка {FL} × {BH} мм — все торцы 90°):",
        f"  • Брус З-1 (верх и низ): {FL} мм — 2 шт.",
        f"  • Брус З-2 (стойки вертикальные): {m['back_stud_height']} мм — 4 шт.",
        f"  • Фанера 10 мм изнутри: {IL} × {BH} мм — 1 шт.",
        "",
        "КАК КРУТИТЬ САМОРЕЗЫ (чтобы брус не треснул):",
        f"  1. В каждую красную точку крутим саморез {'4,5 × 75 мм' if is_budget else '4,5 × 90 мм'}",
        "     (для надежности — по 2 самореза в каждый торец).",
        "  2. Совет: перед вкручиванием длинного самореза просверлите",
        "     первый брусок тонким сверлом 3,5–4 мм — тогда брусок",
        "     никогда не лопнет и притянется намертво!",
        "  3. Наружные углы и лаз закрываем деревянным наличником",
        "     13×74 мм (с завода ТЗСИ) на саморезах 3,0 × 30 мм."
    ]
    sy_p = 755
    for line in spec23:
        is_hdr = line.startswith("Щит") or line.startswith("КАК")
        d2.text((1070, sy_p), line, font=bold_font(18) if is_hdr else regular_font(18), fill=FASTENER_RED if is_hdr else INK_COLOR)
        sy_p += 30
    s2_img.save(os.path.join(PLANS_OUTPUT_DIR, "02_frame_shields_1_to_3.png"))

    s3_img, d3 = create_blueprint_sheet(
        f"ЧЕРТЕЖИ КАРКАСА — ЩИТЫ №4, №5 (БОКОВИНЫ {IW} ММ) И ЩИТ №6 (КРЫША)",
        f"Угол наклона крыши = {m['slope_degrees']}° (торцы боковых стоек и Б-5: {m['acute_angle_deg']}° / {m['obtuse_angle_deg']}°, сдвиг по линейке = {m['bevel_offset_rounded_mm']} мм)",
        3
    )
    sc3 = 0.56
    b3 = int(B * sc3)
    d3.text((55, 138), f"ЩИТЫ №4 и №5: БОКОВЫЕ СТЕНКИ (2 ШТ., ШИРИНА {IW} ММ)", font=bold_font(22), fill=INK_COLOR)
    sx, sy_bot = 155, 675
    sw = int(IW * sc3)
    sh_back, sh_front = int(BH * sc3), int(FH * sc3)

    d3.polygon([(sx, sy_bot), (sx + sw, sy_bot), (sx + sw, sy_bot - sh_front), (sx, sy_bot - sh_back)], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    d3.rectangle([sx, sy_bot - b3, sx + sw, sy_bot], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d3.text((sx + 55, sy_bot - b3 + 3), f"Б-1: {IW} мм (торцы 90°)", font=bold_font(16), fill=INK_COLOR)

    d3.polygon([
        (sx, sy_bot - b3),
        (sx + b3, sy_bot - b3),
        (sx + b3, sy_bot - b3 - int(m["stud_b3_right"] * sc3)),
        (sx, sy_bot - b3 - int(m["stud_b3_left"] * sc3))
    ], fill=TIMBER_FILL, outline=INK_COLOR, width=3)

    msx = sx + int(m["mid_stud_x0"] * sc3)
    d3.polygon([
        (msx, sy_bot - b3),
        (msx + b3, sy_bot - b3),
        (msx + b3, sy_bot - b3 - int(m["stud_b4_right"] * sc3)),
        (msx, sy_bot - b3 - int(m["stud_b4_left"] * sc3))
    ], fill=TIMBER_FILL, outline=INK_COLOR, width=3)

    d3.polygon([
        (sx + sw - b3, sy_bot - b3),
        (sx + sw, sy_bot - b3),
        (sx + sw, sy_bot - b3 - int(m["stud_b2_right"] * sc3)),
        (sx + sw - b3, sy_bot - b3 - int(m["stud_b2_left"] * sc3))
    ], fill=TIMBER_FILL, outline=INK_COLOR, width=3)

    d3.polygon([(sx, sy_bot - sh_back), (sx + sw, sy_bot - sh_front), (sx + sw, sy_bot - sh_front + b3), (sx, sy_bot - sh_back + b3)], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d3.text((sx + 25, sy_bot - sh_front - 56), f"Б-5 (наклон {m['slope_degrees']}°): {m['sloped_beam_length']} мм (торцы {m['acute_angle_deg']}° / {m['obtuse_angle_deg']}°)", font=bold_font(17), fill=DIMENSION_BLUE)
    d3.text((sx + 8, sy_bot - sh_back - 26), f"{m['obtuse_angle_deg']}°", font=bold_font(16), fill=FASTENER_RED)
    d3.text((sx + sw - 56, sy_bot - sh_front - 26), f"{m['acute_angle_deg']}°", font=bold_font(16), fill=FASTENER_RED)
    d3.text((sx + 8, sy_bot - b3 - 24), "90°", font=bold_font(15), fill=ACCENT_GREEN)
    d3.text((sx + sw - 42, sy_bot - b3 - 24), "90°", font=bold_font(15), fill=ACCENT_GREEN)

    for screw_x, top_screw_y in [
        (sx + b3 // 2, sy_bot - sh_back + b3 // 2),
        (msx + b3 // 2, sy_bot - int(((BH + FH) / 2) * sc3) + b3 // 2),
        (sx + sw - b3 // 2, sy_bot - sh_front + b3 // 2)
    ]:
        draw_screw_point(d3, screw_x, top_screw_y)
        draw_screw_point(d3, screw_x, sy_bot - b3 // 2)

    d3.text((sx + b3 + 16, sy_bot - int(360 * sc3)), f"Техноплекс\n{m['side_cell_1_width']}×{round(m['stud_b4_left'])} мм", font=bold_font(15), fill=INK_COLOR)
    d3.text((msx + b3 + 16, sy_bot - int(380 * sc3)), f"Техноплекс\n{m['side_cell_2_width']}×{round(m['stud_b2_left'])} мм", font=bold_font(15), fill=INK_COLOR)

    draw_dimension_arrow(d3, sx, sy_bot, sx + sw, sy_bot, f"{IW} мм (вставляется между Передом и Задом)", 0, 1, offset_distance=65)
    draw_dimension_arrow(d3, sx, sy_bot, sx, sy_bot - sh_back, f"{BH} мм (зад)", -1, 0, offset_distance=75)
    draw_dimension_arrow(d3, sx + sw, sy_bot, sx + sw, sy_bot - sh_front, f"{FH} мм (перед)", 1, 0, offset_distance=80)
    draw_dimension_arrow(d3, sx + b3, sy_bot, msx, sy_bot, f"{m['side_cell_1_width']} мм", 0, 1, offset_distance=28, color=ACCENT_GREEN)
    draw_dimension_arrow(d3, msx + b3, sy_bot, sx + sw - b3, sy_bot, f"{m['side_cell_2_width']} мм", 0, 1, offset_distance=28, color=ACCENT_GREEN)

    d3.rectangle([55, 775, 920, 1345], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    d3.text((75, 795), "ТОЧНЫЕ ВЫСОТЫ СТОЕК БОКОВИН (РАСЧЕТ PYTHON ПО X):", font=bold_font(19), fill=DIMENSION_BLUE)
    side_notes = [
        "На 1 боковую стенку (умножаем на 2 для Левой и Правой):",
        f"  • Брус Б-1 (нижний, 90°): {IW} мм — 1 шт. (всего 2 шт.)",
        f"  • Стойка Б-3 (задняя, x=0..{B}): слева {m['stud_b3_left']} -> справа {m['stud_b3_right']} мм (2 шт.)",
        f"  • Стойка Б-4 (средняя, x={m['mid_stud_x0']}..{m['mid_stud_x0']+B}): слева {m['stud_b4_left']} -> справа {m['stud_b4_right']} мм (2 шт.)",
        f"  • Стойка Б-2 (передняя, x={IW-B}..{IW}): слева {m['stud_b2_left']} -> справа {m['stud_b2_right']} мм (2 шт.)",
        f"  • Брус Б-5 (верхний наклонный {m['slope_degrees']}°): {m['sloped_beam_length']} мм — 1 шт. (всего 2 шт.)",
        "",
        f"ПРАВИЛО РУЛЕТКИ (разница краев каждой стойки = {m['bevel_offset_rounded_mm']} мм):",
        "  • Так как крыша поднимается от Задней стенки (слева) к Передней (справа),",
        f"    у каждой стойки правая грань ровно на {m['bevel_offset_rounded_mm']} мм выше левой грани!",
        "  • На задней стойке Б-3 левый край = ровно высоте стойки задней стены",
        f"    ({m['stud_b3_left']} мм), а правый край поднимается до {m['stud_b3_right']} мм.",
        "  • На передней стойке Б-2 правый край = ровно высоте стойки передней",
        f"    стены ({m['stud_b2_right']} мм), а левый край опускается до {m['stud_b2_left']} мм."
    ]
    ny = 835
    for l in side_notes:
        is_h = l.startswith("На 1") or l.startswith("ПРАВИЛО")
        d3.text((75, ny), l, font=bold_font(16) if is_h else regular_font(16), fill=FASTENER_RED if l.startswith("ПРАВИЛО") else INK_COLOR)
        ny += 34

    d3.text((975, 138), "ЩИТ №6: ОТКИДНАЯ КРЫША (ЦЕЛЬНЫЙ ОСБ-3 9 ММ)", font=bold_font(21), fill=INK_COLOR)
    rx0, ry0 = 1075, 225
    rsc = 0.52
    rw, rh = int(m["roof_length"] * rsc), int(m["roof_width"] * rsc)
    pw, ph = int(m["roof_plug_length"] * rsc), int(m["roof_plug_width"] * rsc)
    br = int(B * rsc)

    d3.rectangle([rx0, ry0, rx0 + rw, ry0 + rh], fill=OSB_FILL, outline=INK_COLOR, width=3)
    px0 = rx0 + (rw - pw) // 2
    py0 = ry0 + int(145 * rsc)
    d3.rectangle([px0, py0, px0 + pw, py0 + ph], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    d3.rectangle([px0, py0, px0 + pw, py0 + br], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d3.rectangle([px0, py0 + ph - br, px0 + pw, py0 + ph], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d3.text((px0 + pw // 2 - 85, py0 + 2), f"К-1: {m['roof_plug_length']} мм (90°)", font=bold_font(15), fill=INK_COLOR)
    d3.text((px0 + pw // 2 - 85, py0 + ph - br + 2), f"К-1: {m['roof_plug_length']} мм (90°)", font=bold_font(15), fill=INK_COLOR)

    cur_rx = 0
    for rcw in m["roof_cell_widths"]:
        rpx = px0 + int(cur_rx * rsc)
        d3.rectangle([rpx, py0 + br, rpx + br, py0 + ph - br], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
        draw_screw_point(d3, rpx + br // 2, py0 + br // 2)
        draw_screw_point(d3, rpx + br // 2, py0 + ph - br // 2)
        cx = px0 + int((cur_rx + B + rcw / 2) * rsc)
        cy = py0 + ph // 2
        d3.text((cx - 65, cy - 25), f"Техноплекс {m['foam_thickness']}", font=bold_font(15), fill=INK_COLOR)
        d3.text((cx - 55, cy), f"{rcw} × {m['roof_plug_cross_len']} мм", font=mono_font(15), fill=DIMENSION_BLUE)
        cur_rx += B + rcw
    rpx_last = px0 + int(cur_rx * rsc)
    d3.rectangle([rpx_last, py0 + br, rpx_last + br, py0 + ph - br], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    draw_screw_point(d3, rpx_last + br // 2, py0 + br // 2)
    draw_screw_point(d3, rpx_last + br // 2, py0 + ph - br // 2)

    for hx in [px0 + 60, px0 + pw - 110]:
        d3.rectangle([hx, ry0 + int(65 * rsc), hx + 50, ry0 + int(105 * rsc)], fill=FASTENER_RED, outline=INK_COLOR, width=2)
    d3.text((rx0 + rw // 2 - 170, ry0 + 12), "ЗАДНИЙ КРАЙ (сюда крутим 2 петли к задней стенке)", font=bold_font(16), fill=FASTENER_RED)
    d3.text((rx0 + rw // 2 - 150, ry0 + rh - 32), "ПЕРЕДНИЙ КОЗЫРЕК НАД ВХОДОМ", font=bold_font(16), fill=DIMENSION_BLUE)

    draw_dimension_arrow(d3, rx0, ry0, rx0 + rw, ry0, f"{m['roof_length']} мм (цельный лист ОСБ-3 9 мм)", 0, -1, offset_distance=35)
    draw_dimension_arrow(d3, rx0 + rw, ry0, rx0 + rw, ry0 + rh, f"{m['roof_width']} мм", 1, 0, offset_distance=65)
    draw_dimension_arrow(d3, px0, py0 + ph, px0 + pw, py0 + ph, f"{m['roof_plug_length']} мм (теплая рамка-пробка)", 0, 1, offset_distance=35, color=ACCENT_GREEN)
    draw_dimension_arrow(d3, px0, py0, px0, py0 + ph, f"{m['roof_plug_width']} мм", -1, 0, offset_distance=55, color=ACCENT_GREEN)

    d3.rectangle([975, 835, 1945, 1345], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    d3.text((1000, 855), "ДЕТАЛИ ОТКИДНОЙ КРЫШИ (ЩИТ №6 — ВСЕ УГЛЫ 90°):", font=bold_font(20), fill=DIMENSION_BLUE)
    r_notes = [
        f"• Верхний лист крыши: ЦЕЛЬНЫЙ кусок ОСБ-3 9 мм {m['roof_length']} × {m['roof_width']} мм.",
        f"• Кровля сверху: {roof_cov_label}.",
        f"• Брус теплой рамки К-1 (продольный, 90°): {m['roof_plug_length']} мм — 2 шт.",
        f"• Брус теплой рамки К-2 (поперечный, 90°): {m['roof_plug_cross_len']} мм — 4 шт.",
        f"• Техноплекс {m['foam_thickness']} мм внутрь крыши: 3 куска ({', '.join(str(w) for w in m['roof_cell_widths'])}) × {m['roof_plug_cross_len']} мм.",
        f"• Подшивка теплой рамки снизу (ОСБ-3 9 мм): {m['roof_plug_length']} × {m['roof_plug_width']} мм.",
        "",
        "ПОЧЕМУ ТАКАЯ КРЫША ЛУЧШЕ ОБЫЧНОЙ ПЛОСКОЙ:",
        f"  Рамка {m['roof_plug_length']} × {m['roof_plug_width']} мм меньше чистого размера комнаты",
        f"  ({CL} × {CW} мм) ровно на 5 мм с каждой стороны.",
        "  Когда крыша опускается, теплая рамка плотно заходит",
        "  внутрь коробки будки как пробка и полностью перекрывает",
        "  мостик холода под крышей!"
    ]
    ry_n = 892
    for l in r_notes:
        is_h = l.startswith("ПОЧЕМУ")
        d3.text((1000, ry_n), l, font=bold_font(17) if is_h else regular_font(17), fill=FASTENER_RED if is_h else INK_COLOR)
        ry_n += 29
    s3_img.save(os.path.join(PLANS_OUTPUT_DIR, "03_frame_shields_4_to_6.png"))

    s4_img, d4 = create_blueprint_sheet(
        f"КАРТА РАСКРОЯ ЛИСТОВ И {m['num_3m_bars']} БРУСКОВ (СМЕТА {m['total_cost_byn']} BYN)",
        "Автоматическая 1D/2D раскладка Python: каждая деталь проверяется assert-условиями без наложений и перерасхода",
        4
    )
    d4.text((55, 136), "1. РАСКРОЙ ФАНЕРЫ (1 ЛИСТ 10 ММ + 2 ЛИСТА 4 ММ) И 1 ЛИСТА ОСБ-3 9 ММ (2500×1250):", font=bold_font(21), fill=INK_COLOR)

    psc = 0.24
    ply_layouts = [
        ("ФАНЕРА 10 мм — ЛИСТ №1 (35,44 BYN)", 1525, 1525, [
            (0, 0, FL, FW, PLYWOOD_FILL, f"ЧИСТОВОЙ ПОЛ (10 мм)\n{FL} × {FW} мм\n(углы 90°)"),
            (0, FW, IL, BH, (220, 240, 215), f"ЗАДНЯЯ СТЕНКА (10 мм)\n{IL} × {BH} мм\n(углы 90°)"),
            (FL, 0, 1525 - FL, 1525, (240, 240, 240), "Остаток")
        ]),
        ("ФАНЕРА 4 мм — ЛИСТ №2 (17,17 BYN)", 1525, 1525, [
            (0, 0, FL, FW, PLYWOOD_FILL, f"ЧЕРНОВОЙ ПОЛ (4 мм)\n{FL} × {FW} мм\n(снизу под раму пола)"),
            (0, FW, IW, 1525 - FW, (220, 240, 215), f"ЛЕВАЯ БОКОВИНА (4 мм)\n{IW} × {BH}..{FH} мм"),
            (IW, FW, 1525 - IW, 1525 - FW, (240, 240, 240), "Остаток"),
            (FL, 0, 1525 - FL, FW, (240, 240, 240), "Остаток")
        ]),
        ("ФАНЕРА 4 мм — ЛИСТ №3 (17,17 BYN)", 1525, 1525, [
            (0, 0, IL, FH, PLYWOOD_FILL, f"ПЕРЕДНЯЯ СТЕНКА (4 мм)\n{IL} × {FH} мм\n(вырезать лаз {m['door_width']}×{m['door_height']})"),
            (0, FH, IW, FH, (220, 240, 215), f"ПРАВАЯ БОКОВИНА (4 мм)\n{IW} × {BH}..{FH} мм"),
            (IL, 0, 1525 - IL, 1525, (240, 240, 240), "Остаток")
        ])
    ]
    for idx_s, (stitle, sw_m, sh_m, rects) in enumerate(ply_layouts):
        bx_p = 55 + idx_s * 415
        by_p = 198
        sw_p, sh_p = int(sw_m * psc), int(sh_m * psc)
        d4.text((bx_p, by_p - 26), stitle, font=bold_font(14), fill=DIMENSION_BLUE)
        d4.rectangle([bx_p, by_p, bx_p + sw_p, by_p + sh_p], fill=(245, 245, 245), outline=INK_COLOR, width=3)
        for rx, ry, rwm, rhm, col, lbl in rects:
            x1, y1 = bx_p + int(rx * psc), by_p + int(ry * psc)
            x2, y2 = bx_p + int((rx + rwm) * psc), by_p + int((ry + rhm) * psc)
            d4.rectangle([x1, y1, x2, y2], fill=col, outline=INK_COLOR, width=2)
            d4.text((x1 + 6, y1 + 8), lbl, font=bold_font(12), fill=INK_COLOR)
        d4.text((bx_p + sw_p // 2 - 55, by_p + sh_p + 6), "1525 × 1525 мм", font=mono_font(14), fill=MUTED_TEXT_COLOR)

    osb_x, osb_y = 1310, 198
    osc = 0.24
    ow_p, oh_p = int(2500 * osc), int(1250 * osc)
    d4.text((osb_x, osb_y - 26), f"ОСБ-3 9 мм — ЛИСТ НА КРЫШУ (2500×1250 мм)", font=bold_font(15), fill=FASTENER_RED)
    d4.rectangle([osb_x, osb_y, osb_x + ow_p, osb_y + oh_p], fill=(240, 240, 240), outline=INK_COLOR, width=3)
    r1w, r1h = int(m["roof_length"] * osc), int(m["roof_width"] * osc)
    d4.rectangle([osb_x, osb_y, osb_x + r1w, osb_y + r1h], fill=OSB_FILL, outline=INK_COLOR, width=2)
    d4.text((osb_x + 12, osb_y + 20), f"ВЕРХНИЙ ЛИСТ КРЫШИ\n{m['roof_length']} × {m['roof_width']} мм\n(ЦЕЛЬНЫЙ БЕЗ СТЫКА!)", font=bold_font(15), fill=INK_COLOR)
    d4.rectangle([osb_x + r1w, osb_y, osb_x + r1w + int(m["roof_plug_width"] * osc), osb_y + int(m["roof_plug_length"] * osc)], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)
    d4.text((osb_x + r1w + 8, osb_y + 20), f"ПОДШИВКА\nКРЫШИ СНИЗУ\n{m['roof_plug_width']} × {m['roof_plug_length']} мм\n(ЦЕЛЬНАЯ!)", font=bold_font(13), fill=INK_COLOR)
    d4.text((osb_x + ow_p // 2 - 65, osb_y + oh_p + 8), "2500 × 1250 мм", font=mono_font(14), fill=MUTED_TEXT_COLOR)

    d4.text((55, 610), f"2. КАРТА РАСПИЛА БРУСА {B}×{B} ММ ({m['num_3m_bars']} ШТУК ПО 3000 ММ — ВСЕ {m['total_timber_pieces']} ДЕТАЛЬ):", font=bold_font(21), fill=INK_COLOR)
    bsc = 0.25
    for b_idx, bar_cuts in enumerate(m["packed_bars"]):
        col_i = b_idx // 6
        row_i = b_idx % 6
        lx_b = 55 + col_i * 960
        by_b = 655 + row_i * 47
        d4.text((lx_b, by_b + 6), f"Брус 3м №{b_idx + 1}", font=bold_font(15), fill=INK_COLOR)
        bs_x = lx_b + 165
        d4.rectangle([bs_x, by_b, bs_x + int(3000 * bsc), by_b + 33], fill=(235, 235, 235), outline=INK_COLOR, width=2)
        cx_b = bs_x
        for clen, clbl in bar_cuts:
            cw_p = int(clen * bsc)
            d4.rectangle([cx_b, by_b, cx_b + cw_p, by_b + 33], fill=TIMBER_FILL, outline=INK_COLOR, width=2)
            d4.text((cx_b + 4, by_b + 8), clbl, font=bold_font(12), fill=INK_COLOR)
            cx_b += cw_p

    d4.rectangle([55, 955, 1945, 1365], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    d4.text((75, 970), f"3. АВТОМАТИЧЕСКИЙ РАСЧЕТ СМЕТЫ PYTHON (ВАРИАНТ: {'БЮДЖЕТ 30 ММ' if is_budget else 'ОСНОВНОЙ 50 ММ'} — ИТОГО {m['total_cost_byn']} BYN):", font=bold_font(20), fill=DIMENSION_BLUE)

    half_n = (len(m["bom_items"]) + 1) // 2
    left_bom = m["bom_items"][:half_n]
    right_bom = m["bom_items"][half_n:]

    ly_b = 1006
    for it in left_bom:
        d4.text((75, ly_b), f"{it['num']}. {it['title']} — {it['price']} BYN", font=bold_font(15), fill=INK_COLOR)
        d4.text((95, ly_b + 22), f"• {it['note']}", font=regular_font(14), fill=MUTED_TEXT_COLOR)
        ly_b += 54

    ry_b = 1006
    for it in right_bom:
        d4.text((1005, ry_b), f"{it['num']}. {it['title']} — {it['price']} BYN", font=bold_font(15), fill=INK_COLOR)
        d4.text((1025, ry_b + 22), f"• {it['note']}", font=regular_font(14), fill=MUTED_TEXT_COLOR)
        ry_b += 54

    d4.text((1005, ry_b + 8), f"ИТОГО ПОЛНЫЙ КОМПЛЕКТ (ТОЧНЫЙ СУММАТОР PYTHON): {m['total_cost_byn']} BYN", font=bold_font(18), fill=FASTENER_RED)
    s4_img.save(os.path.join(PLANS_OUTPUT_DIR, "04_cutlist_plywood_and_penoplex.png"))

    s5_img, d5 = create_blueprint_sheet(
        f"КАРТА ВСЕХ УГЛОВ РЕЗА (УКЛОН {m['slope_degrees']}°, УГЛЫ {m['acute_angle_deg']}° / {m['obtuse_angle_deg']}°) + УЗЕЛ УГЛА",
        f"Все углы и миллиметровые сдвиги рассчитаны тригонометрически в Python: сдвиг на ширине бруса {B} мм равен {m['bevel_offset_exact_mm']} мм (~{m['bevel_offset_rounded_mm']} мм)",
        5
    )

    d5.rectangle([45, 135, 975, 715], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    d5.text((65, 150), f"1. ТОЧНЫЕ РАЗМЕРЫ СТОЕК БОКОВИН (УКЛОН {m['slope_degrees']}°, УГОЛ {m['acute_angle_deg']}°):", font=bold_font(19), fill=DIMENSION_BLUE)
    d5.text((65, 182), f"Крыша растет слева направо: правый край каждой стойки выше левого на {m['bevel_offset_exact_mm']} мм!", font=bold_font(15), fill=FASTENER_RED)

    bx_base, by_base = 115, 625
    stud_defs = [
        (f"Стойка Б-3 (x=0..{B})", m["stud_b3_left"], m["stud_b3_right"], 0),
        (f"Стойка Б-4 (x={m['mid_stud_x0']}..{m['mid_stud_x0']+B})", m["stud_b4_left"], m["stud_b4_right"], 275),
        (f"Стойка Б-2 (x={IW-B}..{IW})", m["stud_b2_left"], m["stud_b2_right"], 550)
    ]
    for title_s, h_left, h_right, x_off in stud_defs:
        sx0_s = bx_base + x_off
        w_b = 115
        h_l_px = int(h_left * 0.46)
        y_top_l = by_base - h_l_px
        y_top_r = y_top_l - 22
        d5.polygon([(sx0_s, by_base), (sx0_s + w_b, by_base), (sx0_s + w_b, y_top_r), (sx0_s, y_top_l)], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
        d5.line([(sx0_s, y_top_r), (sx0_s + w_b, y_top_r)], fill=FASTENER_RED, width=2)
        d5.text((sx0_s - 20, by_base + 12), title_s, font=bold_font(14), fill=INK_COLOR)
        d5.text((sx0_s - 20, by_base + 34), f"Слева {h_left} / Справа {h_right} мм", font=mono_font(13), fill=DIMENSION_BLUE)
        d5.text((sx0_s + 10, by_base - 26), "90°", font=bold_font(15), fill=ACCENT_GREEN)
        d5.text((sx0_s + w_b - 38, by_base - 26), "90°", font=bold_font(15), fill=ACCENT_GREEN)
        d5.text((sx0_s + 6, y_top_l + 6), f"{m['obtuse_angle_deg']}°", font=bold_font(14), fill=FASTENER_RED)
        d5.text((sx0_s + w_b - 54, y_top_r + 12), f"{m['acute_angle_deg']}°", font=bold_font(14), fill=FASTENER_RED)
        d5.text((sx0_s + 4, y_top_r - 22), f"+{m['bevel_offset_rounded_mm']} мм", font=bold_font(14), fill=FASTENER_RED)
        d5.text((sx0_s + 24, by_base - h_l_px // 2), f"{B} мм", font=bold_font(15), fill=INK_COLOR)

    d5.rectangle([1015, 135, 1955, 715], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    d5.text((1035, 150), "2. ВЕРХНИЙ НАКЛОННЫЙ БРУС Б-5 И ТРАПЕЦИЯ ФАНЕРЫ БОКОВИНЫ:", font=bold_font(19), fill=DIMENSION_BLUE)
    d5.text((1035, 182), f"Точный расчет Python: гипотенуза Б-5 = sqrt({IW}² + {m['height_drop']}²) = {m['sloped_beam_length']} мм", font=regular_font(16), fill=INK_COLOR)

    b5_x1, b5_y1 = 1090, 310
    b5_x2, b5_y2 = 1850, 235
    b5_h = 54
    d5.polygon([(b5_x1, b5_y1), (b5_x2, b5_y2), (b5_x2, b5_y2 + b5_h), (b5_x1, b5_y1 + b5_h)], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d5.text((b5_x1 + 160, b5_y2 - 28), f"Брус Б-5: длина {m['sloped_beam_length']} мм (наклон {m['slope_degrees']}°)", font=bold_font(17), fill=INK_COLOR)
    d5.text((b5_x1 + 10, b5_y1 + 6), f"{m['obtuse_angle_deg']}°", font=bold_font(14), fill=FASTENER_RED)
    d5.text((b5_x1 + 10, b5_y1 + b5_h - 22), f"{m['acute_angle_deg']}°", font=bold_font(14), fill=FASTENER_RED)
    d5.text((b5_x2 - 55, b5_y2 + 6), f"{m['acute_angle_deg']}°", font=bold_font(14), fill=FASTENER_RED)
    d5.text((b5_x2 - 55, b5_y2 + b5_h - 22), f"{m['obtuse_angle_deg']}°", font=bold_font(14), fill=FASTENER_RED)
    d5.text((b5_x1 - 10, b5_y1 + b5_h + 10), f"Сдвиг торца по линейке = {m['bevel_offset_rounded_mm']} мм (или отпилить по месту!)", font=bold_font(15), fill=DIMENSION_BLUE)

    tr_x, tr_y_bot = 1140, 680
    tr_w, tr_h_l, tr_h_r = 420, 210, 250
    d5.polygon([(tr_x, tr_y_bot), (tr_x + tr_w, tr_y_bot), (tr_x + tr_w, tr_y_bot - tr_h_r), (tr_x, tr_y_bot - tr_h_l)], fill=PLYWOOD_FILL, outline=INK_COLOR, width=3)
    d5.text((tr_x + 65, tr_y_bot - 135), "Боковой лист фанеры 4 мм (2 шт.)", font=bold_font(16), fill=INK_COLOR)
    d5.text((tr_x + 65, tr_y_bot - 108), "Нижние углы: строго 90° и 90°", font=regular_font(15), fill=ACCENT_GREEN)
    d5.text((tr_x + 65, tr_y_bot - 84), f"Верхние углы: {m['obtuse_angle_deg']}° и {m['acute_angle_deg']}°", font=regular_font(15), fill=FASTENER_RED)
    d5.text((tr_x + 12, tr_y_bot - 26), "90°", font=bold_font(16), fill=ACCENT_GREEN)
    d5.text((tr_x + tr_w - 42, tr_y_bot - 26), "90°", font=bold_font(16), fill=ACCENT_GREEN)
    d5.text((tr_x + 12, tr_y_bot - tr_h_l + 8), f"{m['obtuse_angle_deg']}°", font=bold_font(16), fill=FASTENER_RED)
    d5.text((tr_x + tr_w - 58, tr_y_bot - tr_h_r + 12), f"{m['acute_angle_deg']}°", font=bold_font(16), fill=FASTENER_RED)
    d5.text((tr_x - 85, tr_y_bot - tr_h_l // 2), f"{BH} мм", font=mono_font(16), fill=DIMENSION_BLUE)
    d5.text((tr_x + tr_w + 12, tr_y_bot - tr_h_r // 2), f"{FH} мм", font=mono_font(16), fill=DIMENSION_BLUE)
    d5.text((tr_x + tr_w // 2 - 40, tr_y_bot + 8), f"{IW} мм", font=mono_font(16), fill=DIMENSION_BLUE)

    d5.rectangle([45, 745, 975, 1360], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    d5.text((65, 762), "3. УЗЕЛ СТЫКОВКИ УГЛА БУДКИ (ВИД СВЕРХУ КРУПНО — ВСЕ УГЛЫ 90°):", font=bold_font(19), fill=DIMENSION_BLUE)
    d5.text((65, 792), f"Как соединяются в углу брус {B}×{B}, фанера 4 мм, обшивка и наличник 13×74 мм:", font=regular_font(16), fill=INK_COLOR)

    cx, cy = 260, 930
    s_u = 2.4
    b_u = int(50 * s_u)
    p4_u = int(4 * s_u)
    v_u = int(16 * s_u)
    n_t = int(13 * s_u)
    n_w = int(74 * s_u)

    d5.rectangle([cx, cy, cx + 380, cy + b_u], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    d5.rectangle([cx, cy, cx + b_u, cy + b_u], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d5.text((cx + 8, cy + 28), f"Стойка П-2\n({B}×{B} мм)\nУгол 90°", font=bold_font(14), fill=INK_COLOR)

    d5.rectangle([cx, cy + b_u, cx + b_u, cy + 340], fill=PENOPLEX_FILL, outline=INK_COLOR, width=2)
    d5.rectangle([cx, cy + b_u, cx + b_u, cy + b_u * 2], fill=TIMBER_FILL, outline=INK_COLOR, width=3)
    d5.text((cx + 8, cy + b_u + 28), f"Стойка Б-2\n({B}×{B} мм)\nУгол 90°", font=bold_font(14), fill=INK_COLOR)

    d5.line([(cx + b_u - 16, cy - 18), (cx + b_u - 16, cy + b_u + 65)], fill=FASTENER_RED, width=5)
    d5.text((cx + b_u + 15, cy + 12), f"Саморез {'4,5×75' if is_budget else '4,5×90'} мм (стягивает 2 стены под 90°)", font=bold_font(15), fill=FASTENER_RED)

    d5.rectangle([cx + b_u, cy + b_u, cx + 380, cy + b_u + p4_u], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)
    d5.rectangle([cx + b_u, cy + b_u + p4_u, cx + b_u + p4_u, cy + 340], fill=PLYWOOD_FILL, outline=INK_COLOR, width=2)
    d5.text((cx + b_u + 30, cy + b_u + 18), "Внутренняя фанера 4 мм (стык в углу под 90°)", font=bold_font(15), fill=ACCENT_GREEN)

    d5.rectangle([cx - v_u, cy - v_u, cx + 380, cy], fill=VAGONKA_FILL, outline=INK_COLOR, width=2)
    d5.rectangle([cx - v_u, cy, cx, cy + 340], fill=VAGONKA_FILL, outline=INK_COLOR, width=2)
    d5.text((cx + 150, cy - v_u + 8), f"{outer_label} снаружи", font=bold_font(14), fill=INK_COLOR)

    d5.rectangle([cx - v_u - n_t, cy - v_u - n_t, cx - v_u - n_t + n_w, cy - v_u], fill=TIMBER_FILL, outline=FASTENER_RED, width=3)
    d5.rectangle([cx - v_u - n_t, cy - v_u, cx - v_u, cy - v_u + n_w - n_t], fill=TIMBER_FILL, outline=FASTENER_RED, width=3)
    d5.text((cx - v_u - n_t, cy - v_u - n_t - 26), "2 планки наличника 13×74 мм (сбиваются буквой Г под 90°)", font=bold_font(15), fill=FASTENER_RED)

    d5.rectangle([1015, 745, 1955, 1360], fill=(255, 255, 255), outline=INK_COLOR, width=3)
    d5.text((1035, 762), "4. СВОДНАЯ ВЕДОМОСТЬ УГЛОВ РЕЗА (ВЫЧИСЛЕНО В PYTHON):", font=bold_font(20), fill=DIMENSION_BLUE)

    angle_summary = [
        f"• {m['straight_90_pieces']} из {m['total_timber_pieces']} брусков каркаса пилятся СТРОГО ПОД ПРЯМЫМ УГЛОМ 90°:",
        "  - Рама пола и цоколь: Д-1 (2 шт.), Д-2 (4 шт.), Ц-1 (2 шт.), Ц-2 (3 шт.) -> все торцы 90°.",
        "  - Передняя стенка: П-1 (2 шт.), П-2 (5 шт.), П-3 (1 шт.) -> все торцы 90°.",
        "  - Задняя стенка: З-1 (2 шт.), З-2 (4 шт.) -> все торцы 90°.",
        "  - Нижний брус боковин Б-1 (2 шт.) и вся рамка крыши К-1 (2 шт.), К-2 (4 шт.) -> все торцы 90°.",
        "",
        f"• ТОЛЬКО {m['angled_pieces']} ИЗ {m['total_timber_pieces']} ДЕТАЛЕЙ БРУСА ИМЕЮТ СКОС {m['slope_degrees']}° ({m['acute_angle_deg']}° / {m['obtuse_angle_deg']}°):",
        f"  - Стойка Б-3 (2 шт.): левый край {m['stud_b3_left']} мм, правый край {m['stud_b3_right']} мм (верх {m['acute_angle_deg']}°).",
        f"  - Стойка Б-4 (2 шт.): левый край {m['stud_b4_left']} мм, правый край {m['stud_b4_right']} мм (верх {m['acute_angle_deg']}°).",
        f"  - Стойка Б-2 (2 шт.): левый край {m['stud_b2_left']} мм, правый край {m['stud_b2_right']} мм (верх {m['acute_angle_deg']}°).",
        f"  - Верхний наклонный брус боковин Б-5 (2 шт., длина {m['sloped_beam_length']} мм): оба торца {m['acute_angle_deg']}° / {m['obtuse_angle_deg']}°.",
        "",
        "• ЛИСТОВЫЕ МАТЕРИАЛЫ (ФАНЕРА И ОСБ-3):",
        "  - Чистовой пол, черновой пол, передняя стенка, задняя стенка, оба листа крыши -> все углы 90°.",
        f"  - Боковые стенки внутри (2 шт., фанера 4 мм): снизу углы 90°, сверху скос {m['acute_angle_deg']}° / {m['obtuse_angle_deg']}°.",
        "",
        "• НАЛИЧНИК 13×74 ММ НА УГЛЫ И РАМКУ ЛАЗА:",
        f"  - На 4 углах будки: скручивается внахлест под 90°, верхний торец под крышей срезается на {m['slope_degrees']}°.",
        "  - Вокруг окна лаза (350×450 мм): углы рамки запиливаются под 45° (или встык под 90°)."
    ]
    ay = 802
    for line in angle_summary:
        is_hdr = line.startswith("•")
        d5.text((1035, ay), line, font=bold_font(16) if is_hdr else regular_font(15), fill=FASTENER_RED if "ТОЛЬКО" in line else (INK_COLOR if not is_hdr else DIMENSION_BLUE))
        ay += 29
    s5_img.save(os.path.join(PLANS_OUTPUT_DIR, "05_angles_and_corner_joints.png"))

    s1_img.save(
        os.path.join(PLANS_OUTPUT_DIR, "doghouse_blueprints_telekhany.pdf"),
        "PDF",
        resolution=150.0,
        save_all=True,
        append_images=[s2_img, s3_img, s4_img, s5_img, generate_sheet_six(m)]
    )

    with open(os.path.join(PLANS_OUTPUT_DIR, "calculations_verified.json"), "w", encoding="utf-8") as jf:
        json.dump(m, jf, ensure_ascii=False, indent=2)



def generate_readme_markdown(m):
    readme_path = os.path.join(os.path.dirname(PLANS_OUTPUT_DIR), "README.md")
    B = m["beam_size"]
    FL = m["frame_length"]
    FW = m["frame_width"]
    IL = m["interior_frame_length"]
    IW = m["interior_frame_width"]
    CL = m["clean_room_length"]
    CW = m["clean_room_width"]
    FH = m["front_wall_height"]
    BH = m["back_wall_height"]
    is_budget = m["is_budget"]
    variant_title = "Бюджетная версия 30 мм + вагонка снаружи" if is_budget else "Основная версия 50 мм + вагонка снаружи"
    bt = chr(96)
    lines = [
        f"# Проект зимней утепленной будки {IL}×{IW} мм — {variant_title} ({m['total_cost_byn']} BYN)",
        "",
        f"> **100% расчетов на Python:** все линейные размеры, тригонометрические углы наклона крыши, высоты каждой стойки по координате X, раскладка по листам/брускам и итоговая смета вычисляются и проверяются {bt}assert{bt}-условиями в [{bt}scripts/generate_blueprints.py{bt}](./scripts/generate_blueprints.py) и сохраняются в [{bt}plans/calculations_verified.json{bt}](./plans/calculations_verified.json).",
        ">",
        "> **Навигация по документации проекта:**",
        f"> * [{bt}docs/ASSEMBLY_GUIDE.md{bt}](./docs/ASSEMBLY_GUIDE.md) — **Пошаговая инструкция по сборке и безопасной пропитке** (от распила до установки).",
        f"> * [{bt}docs/PROCUREMENT_TELEKHANY.md{bt}](./docs/PROCUREMENT_TELEKHANY.md) — **Где и как заказать материалы в г.п. Телеханы** (телефоны лесхоза, ТЗСИ и коды ОМА).",
        f"> * [{bt}docs/DECISIONS.md{bt}](./docs/DECISIONS.md) — **Журнал проектных решений** (почему выбраны именно такие размеры, узлы и материалы).",
        f"> * [{bt}AGENTS.md{bt}](./AGENTS.md) — **Файл-память для ИИ-агента** (автоматически загружается при открытии проекта в новой сессии).",
        "",
        "---",
        "",
        f"## Вычисленные параметры конструкции ({variant_title})",
        "",
        f"* **Наружный габарит каркаса по брусу {bt}{B}×{B} мм{bt}:** {bt}{FL} × {FW} мм{bt} (полный наружный габарит с обшивкой: {bt}{m['outer_total_length']} × {m['outer_total_width']} мм{bt}).",
        f"* **Внутренний размер комнаты по каркасу:** {bt}{IL} × {IW} мм{bt} (чистый размер по внутренней фанере: **{bt}{CL} × {CW} мм{bt}**).",
        f"* **Высота стен каркаса:** спереди {bt}{FH} мм{bt}, сзади {bt}{BH} мм{bt} (перепад высоты {bt}{m['height_drop']} мм{bt} на ширине боковины {bt}{IW} мм{bt}).",
        f"* **Точный угол наклона крыши:** **{bt}{m['slope_degrees']}°{bt}** (острый угол **{bt}{m['acute_angle_deg']}°{bt}**, тупой угол **{bt}{m['obtuse_angle_deg']}°{bt}**, сдвиг по линейке на ширине бруса {bt}{B} мм{bt} равен **{bt}{m['bevel_offset_exact_mm']} мм{bt}** ≈ {bt}{m['bevel_offset_rounded_mm']} мм{bt}).",
        "* **Точные высоты стоек боковых стенок (слева направо по росту ската):**",
        f"  * Задняя стойка **Б-3** (x = 0..{B} мм): слева **{bt}{m['stud_b3_left']} мм{bt}** -> справа **{bt}{m['stud_b3_right']} мм{bt}**.",
        f"  * Средняя стойка **Б-4** (x = {m['mid_stud_x0']}..{m['mid_stud_x0']+B} мм): слева **{bt}{m['stud_b4_left']} мм{bt}** -> справа **{bt}{m['stud_b4_right']} мм{bt}**.",
        f"  * Передняя стойка **Б-2** (x = {IW-B}..{IW} мм): слева **{bt}{m['stud_b2_left']} мм{bt}** -> справа **{bt}{m['stud_b2_right']} мм{bt}**.",
        f"  * Верхний наклонный брус **Б-5**: длина **{bt}{m['sloped_beam_length']} мм{bt}**, торцы запилены параллельно стойкам под **{bt}{m['acute_angle_deg']}° / {m['obtuse_angle_deg']}°{bt}**.",
        f"* **Теплая рамка-пробка под крышей:** **{bt}{m['roof_plug_length']} × {m['roof_plug_width']} мм{bt}** (входит внутрь комнаты {bt}{CL} × {CW} мм{bt} с зазором 5 мм на сторону).",
        "",
        "---",
        "",
        "## Чертежи (6 листов)",
        "",
        "### Лист 1. Общий вид, план сверху и боковой разрез",
        "![Лист 1](./plans/01_general_view_and_layers.png)",
        "",
        "### Лист 2. Чертежи каркаса — Щит №1 (Дно + Цоколь), Щит №2 (Перед), Щит №3 (Зад)",
        "![Лист 2](./plans/02_frame_shields_1_to_3.png)",
        "",
        "### Лист 3. Чертежи каркаса — Щиты №4, №5 (Боковины) и Щит №6 (Откидная крыша)",
        "![Лист 3](./plans/03_frame_shields_4_to_6.png)",
        "",
        f"### Лист 4. Карта раскроя листов, {m['num_3m_bars']} брусков и автоматическая смета",
        "![Лист 4](./plans/04_cutlist_plywood_and_penoplex.png)",
        "",
        "### Лист 5. Карта всех углов реза (в градусах и миллиметрах) + узел стыковки угла",
        "![Лист 5](./plans/05_angles_and_corner_joints.png)",
        "",
        "### Лист 6. Шпаргалка новичка: как складывать и скручивать бруски (стыки «Г» и «Т»)",
        "![Лист 6](./plans/06_beginner_screwing_guide.png)",
        "",
        "---",
        "",
        f"## Таблица всех {m['total_timber_pieces']} деталей из бруса {bt}{B} × {B} мм{bt} ({m['num_3m_bars']} брусков по 3 м = {m['timber_volume_m3']} м³)",
        "",
        f"* **{m['straight_90_pieces']} из {m['total_timber_pieces']} деталей** пилятся строго под прямым углом **{bt}90°{bt}**.",
        f"* **Только {m['angled_pieces']} из {m['total_timber_pieces']} деталей** (стойки боковин {bt}Б-3{bt}, {bt}Б-4{bt}, {bt}Б-2{bt} и наклонный брус {bt}Б-5{bt}) имеют скос **{bt}{m['slope_degrees']}°{bt}** ({bt}{m['acute_angle_deg']}° / {m['obtuse_angle_deg']}°{bt}, сдвиг по рулетке {bt}{m['bevel_offset_rounded_mm']} мм{bt}).",
        "",
        "| Код | Назначение | Длина (мм) | Кол-во (шт.) | Углы торцов (левый / правый) |",
        "| :--- | :--- | :---: | :---: | :---: |",
    ]
    for p in m["timber_parts"]:
        lines.append(f"| **{p['code']}** | {p['name']} | **{p['length']}** | **{p['qty']}** | {bt}{p['angle_left']}° / {p['angle_right']}°{bt} |")
    lines += [
        "",
        "---",
        "",
        f"## Автоматическая смета (рассчитано Python {bt}Decimal{bt}, BYN)",
        "",
        "| № | Позиция и применение | Сумма (BYN) |",
        "| :-: | :--- | :---: |",
    ]
    for it in m["bom_items"]:
        lines.append(f"| {it['num']} | **{it['title']}**<br>_{it['note']}_ | **{it['price']}** |")
    lines.append(f"| | **ИТОГО ПОЛНЫЙ КОМПЛЕКТ (ВСЁ НОВОЕ):** | **{m['total_cost_byn']} BYN** |")
    with open(readme_path, "w", encoding="utf-8") as rf:
        rf.write(chr(10).join(lines) + chr(10))

if __name__ == "__main__":
    import sys
    variant = sys.argv[1] if len(sys.argv) > 1 else "main_50mm"
    model_data = compute_doghouse_engineering_model(variant)
    render_all_sheets_and_readme(model_data)
    generate_readme_markdown(model_data)
    print(f"Successfully computed and rendered variant={variant}, total={model_data['total_cost_byn']} BYN")
