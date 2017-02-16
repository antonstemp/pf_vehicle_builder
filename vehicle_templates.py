import operator

TRAVEL_TEMPLATES = {
    'air': {'template_name': 'Air'},
    'land': {'template_name': 'Land'},
    'water': {'template_name': 'Water'},
}

VEHICLE_TEMPLATES = {
    'aerodynamic': {
        'template_name': 'aerodynamic',
        'maneuver_mod': (1, operator.add),
        'load_mult': (0.5, operator.mul),
        'speed_mod': (1, operator.add),
        'cost_mod': (200, operator.add),
    },
    'covered': {
        'template_name': 'covered',
        'cost_mod': (100, operator.add),
    },
    'glider': {
        'template_name': 'glider',
        'maneuver_mod': (-1, operator.add),
        'weight_mult': (0, operator.mul),
        'cost_mod': (200, operator.add),
    },
    'living': {
        'template_name': 'living',
        'crew_mult': (0, operator.mul),
        'cost_mod': (6000, operator.add),
    },
    'maneuverable': {
        'template_name': 'maneuverable',
        'maneuver_mod': (1, operator.add),
        'power_mult': (0.5, operator.mul),
        'cost_mod': (200, operator.add),
    },
    'track': {
        'template_name': 'track',
        'maneuver_set': (0, operator.__setitem__),
        'mass_mult': (0.5, operator.mul),
        'cost_mod': (200, operator.add),
    }
}
