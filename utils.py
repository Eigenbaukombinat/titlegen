from scr_config import SIZE_X, SIZE_Y
import pygame.midi

def align_rect(rect_size, x=0, y=0, halign=None, valign=None, margin=0, fit_to_screen=False):
    if fit_to_screen:
        return 0, 0, 0
    sx, sy = rect_size
    if halign and x:
        raise ValueError("Cannot use halign and x together.")
    if halign == 'center':
        x = (SIZE_X - sx) / 2
    elif halign == 'right':
        x = SIZE_X - sx - margin
    if valign and y:
        raise ValueError("Cannot use valign and y together.")
    if valign == 'bottom':
        y = SIZE_Y - sy - margin
    elif valign == 'top':
        y = margin
    elif valign == 'middle':
        y = (SIZE_Y - sy) / 2
    if halign == 'right' or valign == 'bottom' or halign == 'center':
        margin = 0
    return x, y, margin


def print_midi_device_info():
    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        interf, name, input, output, opened = r
        name = str(name)
        interf = str(interf)
        print(f"{i}: {name} {input and 'IN' or ''}{output and 'OUT' or ''} ({interf})")
