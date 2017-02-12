
import importlib.util
import os
import os.path
import xml.etree.ElementTree as ElementTree


class XMLWrapper(object):
    def __init__(self, xml_element, name, parent=None):
        self._element = xml_element
        self._name = name
        self._parent = parent  # type: XMLWrapper

    def raw(self):
        return self._element

    def set(self, attribute: str, value: str):
        if self._element is None:
            print("Error: Could not set {}=\"{}\" for {}".format(attribute, value, str(self)))
            print("     : Could not get element for {}".format(self._get_invalid_element()))
            return False
        # TODO: Make sure the attribute exists
        self._element.set(attribute, value)
        return True

    def find_and_set(self, xpath_spec: str, attr: str, value: str):
        if self._element is None:
            print("Error: Could not set {}=\"{}\" for {}/{}".format(attr, value, str(self), xpath_spec))
            print("     : Could not get element for {}".format(self._get_invalid_element()))
            return False

        elem = self._element.find(xpath_spec)
        if elem is not None:
            elem.set(attr, value)
            return True
        return False

    def find_and_get(self, xpath_spec: str, attr: str, default_value=None):
        elem = self._element.find(xpath_spec)
        if elem is not None:
            # TODO: Check if the attribute exists
            return elem.get(attr)
        return default_value

    def get_element(self, xpath_spec: str):
        if self._element is None:
            return XMLWrapper(None, xpath_spec, self)
        return XMLWrapper(self._element.find("./"+xpath_spec), xpath_spec, self)

    def _get_invalid_element(self):
        if self._parent is None or self._parent._element is not None:
            return self
        else:
            return self._parent._get_invalid_element()

    def __str__(self):
        if self._parent is None:
            return self._name
        return "{}/{}".format(str(self._parent), self._name)


class ItemAttributes(XMLWrapper):
    def __init__(self, element, parent):
        XMLWrapper.__init__(self, element, "property[@class='Attributes']", parent)

    def entity_damage(self):
        return self.get_element("property[@name='EntityDamage']")

    def block_damage(self):
        return self.get_element("property[@name='BlockDamage']")


class Item(XMLWrapper):
    def __init__(self, element, name):
        XMLWrapper.__init__(self, element, "item[@name='{}']".format(name), None)
        self._name = name
        self._attributes = None
        self._action0 = None
        self._action1 = None

    def attributes(self, create_if_missing: bool=True):
        if self._attributes is not None:
            return self._attributes

        if self._element is None:
            self._attributes = ItemAttributes(None, self)
            return self._attributes

        elem = self._element.find("./property[@class='Attributes']")
        if elem is None:
            if create_if_missing:
                elem = ElementTree.Element("property", {"class": "Attributes"})
                self._element.append(elem)
            else:
                return ItemAttributes(None, self)
        return ItemAttributes(elem, self)

    def action0(self, create_if_missing: bool=True):
        if self._action0 is not None:
            return self._action0

        self._action0 = self._element.find("./property[@class='Action0']")
        if self._action0 is None and create_if_missing:
            self._action0 = ElementTree.Element("property", {"class": "Action0"})
            self._element.append(self._action0)
        return self._action0

    def action1(self, create_if_missing: bool=True):
        if self._action1 is not None:
            return self._action1

        self._action1 = self._element.find("./property[@class='Action1']")
        if self._action1 is None and create_if_missing:
            self._action1 = ElementTree.Element("property", {"class": "Action1"})
            self._element.append(self._action1)
        return self._action1


class GameData(object):
    def __init__(self):
        self.roots = {}
        self.items = None
        self.recipes = None
        self.blocks = None

    def post_load(self):
        self.items = self.roots.get("items", None)
        self.recipes = self.roots.get("recipes", None)
        self.blocks = self.roots.get("blocks", None)

    def find_item(self, name: str):
        if self.items is None:
            return Item(None, name)
        item = self.items.find("./item[@name='{}']".format(name))

        return Item(item, name)

    def create_item(self, name: str, item_id: int):
        if self.items is None:
            return None

        existing = self.items.find("./item[@id='{}']".format(item_id))
        if existing is not None:
            print("Can not create item with duplicate ID {}".format(item_id))
            return Item(None, name)
        existing = self.items.find("./item[@name='{}']".format(name))
        if existing is not None:
            return Item(existing, name)

        elem = ElementTree.Element("item", {"name": name, "id": item_id})
        self.items.append(elem)
        return Item(elem, name)


class ModManager(object):
    def __init__(self):
        self.files = {}
        self.data = GameData()

    def run(self, original: str, modded: str, mods: str):
        self.load(original)

        self.apply_all(mods)
        self.write(modded)

    def write(self, root: str):
        if not os.path.isdir(root):
            os.makedirs(root)

        for file_name, tree in self.files.items():
            file_path = os.path.join(root, file_name)
            if not os.path.isdir(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            tree.write(file_path)

    def apply_all(self, directory_path: str):
        try:
            for file_name in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file_name)
                if os.path.isdir(file_path) and file_name != "__pycache__":
                    self.apply_all(file_path)
                elif os.path.isfile(file_path) and os.path.splitext(file_name)[-1] == ".py":
                    self.apply(file_path)
                else:
                    pass
        except Exception as e:
            print("Exception Encountered: {}".format(e))

    def apply(self, file_path: str):
        try:
            spec = importlib.util.spec_from_file_location("mod.temp", file_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.apply(self.data)
        except Exception as e:
            print("Exception Encountered while apply modfile '{}'".format(file_path))
            print(e)

    def load(self, directory: str):
        print("GameData::load('{}')".format(directory))
        self.files = {}
        self._load_impl(directory, "")
        self.data.post_load()

    def _load_impl(self, root: str, extpath: str):
        # print("GameData::_load_impl('{}','{}')".format(root, extpath))
        directory = os.path.join(root, extpath)
        for fname in os.listdir(directory):
            filepath = os.path.join(directory, fname)
            print("  Loading: '{}'".format(filepath))
            if os.path.isdir(filepath):
                self._load_impl(root, os.path.join(extpath, fname))
            elif os.path.isfile(filepath) and os.path.splitext(filepath)[-1].lower() == ".xml":
                tree = ElementTree.parse(filepath)
                self.files[os.path.join(extpath, fname)] = tree
                tree_root = tree.getroot()
                if tree_root.tag in self.data.roots:
                    print("Warning: root tag '{}' already exists".format(tree_root.tag))
                self.data.roots[tree_root.tag] = tree_root
            else:
                pass

if __name__=="__main__":
    prefix = r"C:\Users\Troy Varney\Desktop\7 Days to Die"
    _original = os.path.join(prefix, "original")
    _modded = os.path.join(prefix, "modded")
    _mods = os.path.join(prefix, "mods")

    _modder = ModManager()
    _modder.run(_original, _modded, _mods)
