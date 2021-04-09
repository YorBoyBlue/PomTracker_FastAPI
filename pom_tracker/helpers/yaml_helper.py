import yaml
from yaml import safe_load


class YamlHelper:
    # yaml.load(file)
    # yaml.dump(data, file)

    @staticmethod
    def loader(filepath):
        with open(filepath, 'r') as f:
            data = safe_load(f)
        return data

    @staticmethod
    def dump(filepath, data):
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    # my_filepath = 'test.yaml'
    # my_data = yaml_loader(my_filepath)
    # print(my_data)
    #
    # items = my_data.get('items')
    # for item_name, item_value in items.items():
    #     print(item_name, item_value)
    #
    # yaml_dump('test2.yaml', my_data)
