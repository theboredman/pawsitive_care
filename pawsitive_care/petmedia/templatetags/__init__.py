from django import template
import hashlib

register = template.Library()

@register.filter
def avatar_url(user, size=40):
    """
    Generate a consistent dummy avatar URL for a user based on their username.
    Uses different avatar services to create diverse, professional-looking avatars.
    """
    if not user or not hasattr(user, 'username'):
        return f"https://ui-avatars.com/api/?name=User&size={size}&background=6c757d&color=ffffff&bold=true"
    
    username = str(user.username)
    email = getattr(user, 'email', username)
    
    # Use MD5 hash of username/email for consistent avatar selection
    user_hash = hashlib.md5(username.lower().encode()).hexdigest()
    
    # Select avatar style based on hash
    hash_int = int(user_hash[:2], 16)  # First 2 hex chars as int (0-255)
    
    # Define avatar services and styles
    avatar_styles = [
        # UI Avatars with different color schemes
        {
            'url': f"https://ui-avatars.com/api/?name={username[:2].upper()}&size={size}&background=007bff&color=ffffff&bold=true",
            'service': 'ui-avatars-blue'
        },
        {
            'url': f"https://ui-avatars.com/api/?name={username[:2].upper()}&size={size}&background=28a745&color=ffffff&bold=true",
            'service': 'ui-avatars-green'
        },
        {
            'url': f"https://ui-avatars.com/api/?name={username[:2].upper()}&size={size}&background=dc3545&color=ffffff&bold=true",
            'service': 'ui-avatars-red'
        },
        {
            'url': f"https://ui-avatars.com/api/?name={username[:2].upper()}&size={size}&background=6f42c1&color=ffffff&bold=true",
            'service': 'ui-avatars-purple'
        },
        {
            'url': f"https://ui-avatars.com/api/?name={username[:2].upper()}&size={size}&background=fd7e14&color=ffffff&bold=true",
            'service': 'ui-avatars-orange'
        },
        {
            'url': f"https://ui-avatars.com/api/?name={username[:2].upper()}&size={size}&background=17a2b8&color=ffffff&bold=true",
            'service': 'ui-avatars-teal'
        },
        # DiceBear Avatars (more diverse styles)
        {
            'url': f"https://api.dicebear.com/7.x/initials/svg?seed={username}&size={size}&backgroundColor=3b82f6&textColor=ffffff",
            'service': 'dicebear-initials'
        },
        {
            'url': f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}&size={size}&backgroundColor=transparent",
            'service': 'dicebear-avataaars'
        },
        {
            'url': f"https://api.dicebear.com/7.x/personas/svg?seed={username}&size={size}&backgroundColor=transparent",
            'service': 'dicebear-personas'
        },
        {
            'url': f"https://api.dicebear.com/7.x/bottts/svg?seed={username}&size={size}&backgroundColor=transparent",
            'service': 'dicebear-bottts'
        }
    ]
    
    # Select avatar based on hash
    selected_avatar = avatar_styles[hash_int % len(avatar_styles)]
    
    return selected_avatar['url']


@register.filter
def avatar_color(user):
    """
    Generate a consistent color for user based on their username.
    Used for borders, accents, etc.
    """
    if not user or not hasattr(user, 'username'):
        return '#6c757d'
    
    username = str(user.username)
    user_hash = hashlib.md5(username.lower().encode()).hexdigest()
    
    # Define color palette
    colors = [
        '#007bff',  # Blue
        '#28a745',  # Green
        '#dc3545',  # Red
        '#6f42c1',  # Purple
        '#fd7e14',  # Orange
        '#17a2b8',  # Teal
        '#e83e8c',  # Pink
        '#6610f2',  # Indigo
        '#20c997',  # Cyan
        '#ffc107'   # Yellow
    ]
    
    hash_int = int(user_hash[:2], 16)
    return colors[hash_int % len(colors)]


@register.filter
def user_initials(user):
    """
    Get user initials for avatar fallback.
    """
    if not user:
        return 'U'
    
    if hasattr(user, 'get_full_name') and user.get_full_name():
        full_name = user.get_full_name().strip()
        if full_name:
            parts = full_name.split()
            if len(parts) >= 2:
                return f"{parts[0][0]}{parts[-1][0]}".upper()
            else:
                return parts[0][:2].upper()
    
    username = getattr(user, 'username', 'User')
    return username[:2].upper()
