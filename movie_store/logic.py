from math import ceil
from django.utils import timezone


def calculate_charge(rental, initial_charge=1.0, default_charge=0.5, initial_charge_days=3):
    current_time = timezone.now()
    if current_time < rental.rental_date:
        return 0.0
    time_diff = current_time - rental.rental_date
    number_of_days = ceil(time_diff.total_seconds() / 86400)
    if number_of_days > initial_charge_days:
        return initial_charge * initial_charge_days + default_charge * (number_of_days - initial_charge_days)
    return initial_charge * number_of_days

