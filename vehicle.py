import math
import operator
from collections import defaultdict
# import pprint as pp

# Base stats
BASE_SPEED = 1
BASE_AC = 5

# Ship size constants
DECK_SIZE = 9
LOCATION_SIZE = 45

# Load multipliers
LIGHT_LOAD = 2
MEDIUM_LOAD = 5
HEAVY_LOAD = 10

# Stat mappings
DODGE_BONUS = {
    'Perfect': 9,
    'Good': 7,
    'Average': 5,
    'Poor': 3,
    'Clumsy': 1,
}
MANEUVERABILITY = {
    5: 'Perfect',
    4: 'Good',
    3: 'Average',
    2: 'Poor',
    1: 'Clumsy',
}
SIZE_MODIFIER = {
    'Large': 1,
    'Huge': 2,
    'Gargantuan': 4,
    'Colossal': 8,
    'Colossal+': 8,
}


class Vehicle(object):
    maneuver_mod = 0
    speed_mod = 0
    cost_mod = 0
    load_mult = 1
    weight_mult = 1
    crew_mult = 1
    power_mult = 1
    mass_mult = 1
    maneuver_set = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

        # TODO add weapons
        self.weapons = []

        self.apply_templates()
        self.build_vehicle()
        self.build_props()
        self.build_rooms()
        self.gen_template_data()

        self.mass

        # pp.pprint(self.__dict__)

    def apply_templates(self):
        for template in self.vehicle_templates:
            for name, tup in template.iteritems():
                if not isinstance(tup, tuple):
                    continue

                val, op = tup

                if op is operator.__setitem__:
                    op(self, name, val)
                else:
                    setattr(self, name, op(val, getattr(self, name)))

    def build_rooms(self):
        note_rooms = (room for room in self.rooms if 'note' in room)

        for room in note_rooms:
            val, unit = room['note']
            room['formatted_note'] = '{} {}'.format(
                val * room['hardpoints'], unit
            )

    # TODO weapons
    def build_weapons(self):
        pass

    ##########################################
    # STATIC METHODS
    ##########################################
    @staticmethod
    def calc_size(hardpoints):
        return {
            'total': hardpoints,
            'decks': hardpoints // DECK_SIZE,
            'remainder': hardpoints % DECK_SIZE
        }

    @staticmethod
    def prop_size(prop):
        return Vehicle.calc_size(prop['hardpoints'])

    ##########################################
    # PROPERTIES
    ##########################################
    @property
    def power(self):
        power = sum(p['power'] * p['hardpoints'] for p in self.propulsions)
        return power * self.power_mult

    @property
    def required_crew(self):
        def count_crew(tasks, required_crew):
            for task in tasks:
                required_crew[task['crew_type']] += int(
                    math.ceil(
                        task['required_crew'] *
                        task['hardpoints'] * self.crew_mult
                    )
                )

        required_crew = defaultdict(int)
        count_crew(self.propulsions, required_crew)
        count_crew(self.weapons, required_crew)

        return required_crew

    def external_hardpoints(self):
        return (
            self.sum_hardpoints(self.propulsions) +
            self.hull_hardpoints()
        )

    def hull_hardpoints(self):
        return self.sum_hardpoints(self.hulls)

    @staticmethod
    def sum_hardpoints(items):
        return sum(i['hardpoints'] for i in items if i['external'])

    @property
    def dodge_bonus(self):
        return DODGE_BONUS[self.maneuverability]

    @property
    def size_ac_mod(self):
        return -self.size_mod

    @property
    def ac(self):
        return BASE_AC + self.dodge_bonus + self.size_ac_mod

    @property
    def size_mod(self):
        return SIZE_MODIFIER[self.size_catagory]

    # TODO add crew weight, add weapons weight
    @property
    def equipment_weight(self):
        return sum(p['weight'] * p['hardpoints'] for p in self.propulsions)

    @property
    def ram_damage(self):
        return '{}d8'.format(self.size_mod)

    @property
    def mass(self):
        mass = sum(hull['hardpoints'] * hull['mass'] for hull in self.hulls)
        return mass * self.mass_mult

    @property
    def vehicle_space(self):
        return max(1, self.external_hardpoints() // LOCATION_SIZE)

    @property
    def cmb(self):
        return self.size_mod + self.vehicle_space - 1

    @property
    def cmd(self):
        return 10 + self.cmb

    @property
    def maneuverability(self):
        if self.maneuver_set:
            return MANEUVERABILITY[self.maneuver_set]

        if self.external_hardpoints() > 45:
            maneuver = 1
        elif self.external_hardpoints() > 8:
            maneuver = 2
        else:
            maneuver = 3

        maneuver = min(5, max(1, maneuver + self.maneuver_mod))

        return MANEUVERABILITY[maneuver]

    @property
    def size_catagory(self):
        hardpoints = self.external_hardpoints()
        if hardpoints > 45:
            return 'Colossal+'
        elif hardpoints > 8:
            return 'Colossal'
        elif hardpoints > 4:
            return 'Gargantuan'
        elif hardpoints > 2:
            return 'Huge'
        elif hardpoints > 0:
            return 'Large'
        else:
            raise ValueError('Invalid hardpoints')

    # TODO weapons
    @property
    def cost(self):
        return (
            self.sum_cost(self.hulls) +
            self.sum_cost(self.propulsions) +
            self.sum_cost(self.rooms) +
            self.template_cost()
        )

    @staticmethod
    def sum_cost(items):
        return sum(i['cost'] * i['hardpoints'] for i in items)

    def template_cost(self):
        return self.cost_mod * self.size_mod

    @property
    def total_size(self):
        return self.calc_size(self.external_hardpoints())

    @property
    def hull_size(self):
        return self.calc_size(self.hardpoints)

    @property
    def speed(self):
        return self.power / self.mass + self.speed_mod

    @property
    def acceleration(self):
        return self.speed / 2

    def locations(self):
        locations = []
        self.format_locations(self.hulls, locations)
        self.format_locations(self.propulsions, locations)

        return locations

    def build_props(self):
        for prop in self.propulsions:
            prop.update(self.calc_size(prop['hardpoints']))

    def build_vehicle(self):
        for hull in self.hulls:
            hull['name'] = 'Hull'
            hull['external'] = True

        self.light_load = self.hull_hardpoints() * LIGHT_LOAD * self.load_mult
        self.medium_load = self.hull_hardpoints() * MEDIUM_LOAD * self.load_mult
        self.heavy_load = self.hull_hardpoints() * HEAVY_LOAD * self.load_mult

    def gen_template_data(self):
        self.travel_template_names = '/'.join(
            template['template_name'] for template in self.travel_templates
        )

        self.vehicle_template_names = ','.join(
            template['template_name'] for template in self.vehicle_templates
        )

        self.material_names = '/'.join(
            hull['material'].capitalize() for hull in self.hulls
        )

    @staticmethod
    def format_locations(sections, locations):
        def create_loc(section, count, hp):
            return {
                'name': section['name'],
                'count': count,
                'hp': hp,
                'hardness': section['hardness'],
            }

        for section in sections:
            if not section['external']:
                continue

            hardpoints = section['hardpoints']

            # Count the number of full locations the vehicle has
            if hardpoints >= LOCATION_SIZE:
                locations.append(create_loc(
                    section,
                    hardpoints // LOCATION_SIZE,
                    section['hp'] * LOCATION_SIZE,
                ))

            # Check if the vehicle has a partial location
            if hardpoints % LOCATION_SIZE:
                locations.append(create_loc(
                    section,
                    1,
                    section['hp'] * (hardpoints % LOCATION_SIZE),
                ))

        return locations
