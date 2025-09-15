from .models import Barbershop

def reset_daily_turns():
    """Resets the current_turn_number for all barbershops to 0."""
    updated_count = Barbershop.objects.all().update(current_turn_number=0)
    return updated_count
