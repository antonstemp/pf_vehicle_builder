from jinja2 import Environment, PackageLoader
from parser import gather_info
from vehicle import Vehicle


if __name__ == '__main__':
    env = Environment(
        loader=PackageLoader('pf_vehicle_builder', 'templates')
    )
    template = env.get_template('vehicle.template')

    vehicle_data = gather_info()

    vehicle = Vehicle(**vehicle_data)

    print template.render(v=vehicle)
