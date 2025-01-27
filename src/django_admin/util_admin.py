from importlib import import_module


def get_admin_class(app_name: str, admin_class_name: str):
    """ Look up an admin class and return the class """
    module_path = f"{app_name}.admin"
    module = import_module(module_path)
    admin_class = getattr(module, admin_class_name, None)

    return admin_class