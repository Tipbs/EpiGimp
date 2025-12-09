def clamp(v, a=0, b=255):
    return max(a, min(b, int(v)))

def rgba_tuple_to_hex(rgba):
    r, g, b, a = rgba
    return '#{0:02x}{1:02x}{2:02x}{3:02x}'.format(r, g, b, a)
