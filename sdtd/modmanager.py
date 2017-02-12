
import importlib.util
import os
import os.path
import xml.etree.ElementTree as ElementTree
from sdtd.item import Item


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
            spec = importlib.util.spec_from_file_location("sdtd.temp", file_path)
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

    def _load_impl(self, root: str, ext_path: str):
        directory = os.path.join(root, ext_path)
        for fname in os.listdir(directory):
            filepath = os.path.join(directory, fname)
            print("  Loading: '{}'".format(filepath))
            if os.path.isdir(filepath):
                self._load_impl(root, os.path.join(ext_path, fname))
            elif os.path.isfile(filepath) and os.path.splitext(filepath)[-1].lower() == ".xml":
                tree = ElementTree.parse(filepath)
                self.files[os.path.join(ext_path, fname)] = tree
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
