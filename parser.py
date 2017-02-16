from collections import OrderedDict, defaultdict
from materials import MATERIALS
from propultion import PROPULSIONS
from rooms import ROOMS
from vehicle_templates import VEHICLE_TEMPLATES, TRAVEL_TEMPLATES

import pprint as pp


def prettify(val):
    return ' '.join(val.split('_')).capitalize()


def separate_comma_list(data):
    if not data:
        return []

    return [name.strip() for name in data.split(',')]


def format_multi_item_list(data):
    data = separate_comma_list(data)

    return (reversed(entry.split(' ')) for entry in data)


def hardpoint_validator(data):
    hardpoints = int(data)

    if hardpoints <= 0:
        return ValueError('Must have at least 1 hardpoint')

    return hardpoints


def template_validator(data, valid_templates):
    templates = separate_comma_list(data)

    if not templates:
        return []

    return [valid_templates[name] for name in templates]


def travel_template_validator(data):
    if not data:
        raise ValueError('Vehicles must have at least one medium of transportation')

    return template_validator(data, TRAVEL_TEMPLATES)


def vehicle_template_validator(data):
    return template_validator(data, VEHICLE_TEMPLATES)


def material_validator(data):
    return MATERIALS[data]


def parse_list(data, valid):
    lst = format_multi_item_list(data)

    results = []

    for name, hardpoints in lst:
        result = dict(valid[name])
        result['hardpoints'] = int(hardpoints)
        results.append(result)

    return results


def room_validator(data):
    return parse_list(data, ROOMS)


def propulsion_validator(data):
    return parse_list(data, PROPULSIONS)


def hull_validator(data):
    return parse_list(data, MATERIALS)


def parse(info, validator):
    while True:
        try:
            data = raw_input('{}: '.format(info))
            return validator(data)
        except ValueError as e:
            print(e.message)
            continue
        except KeyError:
            print('Invalid {}'.format(info))
            continue


def gather_info():
    vehicle_info = OrderedDict([
        ('name', str),
        ('travel_templates', travel_template_validator),
        ('vehicle_templates', vehicle_template_validator),
        ('hulls', hull_validator),
        ('propulsions', propulsion_validator),
        ('rooms', room_validator),
        ('weapons', list),
    ])

    vehicle = defaultdict(None)

    for info, validator in vehicle_info.iteritems():
        vehicle[info] = parse(prettify(info), validator)

    pp.pprint(dict(vehicle))

    return vehicle
