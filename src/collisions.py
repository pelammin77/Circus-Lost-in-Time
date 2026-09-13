"""Use physical bodies rather than transparent sprite padding."""
def collision_rect(obj):
    return obj.body_rect() if hasattr(obj,'body_rect') else obj.rect
