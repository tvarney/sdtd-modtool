
from sdtd.elements import *


class ItemAttributes(PropertyClass):
    def __init__(self, element, parent, **kwargs):
        PropertyClass.__init__(self, element, "Attributes", parent, **kwargs)

    def entity_damage(self, create_if_missing: bool=False):
        return self.get_property_name("EntityDamage", create_if_missing)

    def block_damage(self, create_if_missing: bool=False):
        return self.get_property_name("BlockDamage", create_if_missing)

    def degradation_max(self, create_if_missing: bool=False):
        return self.get_property_name("DegradationMax", create_if_missing)

    def degradation_rate(self, create_if_missing: bool=False):
        return self.get_property_name("DegradationRate", create_if_missing)


class Action(PropertyClass):
    def __init__(self, element, action_id: int, parent=None, **kwargs):
        PropertyClass.__init__(element, "action{}".format(action_id), parent, **kwargs)
        self._action_id = action_id


class Item(PropertyContainer):
    def __init__(self, element, name, parent=None):
        XMLWrapper.__init__(self, element, "item[@name='{}']".format(name), parent)
        self._name = name
        self._id = None if element is None else element.get("id")

    def crafting_ingredient_time(self, create_if_missing: bool=False):
        return self.get_property_name("CraftingIngredientTime", create_if_missing)

    def description_key(self, create_if_missing: bool=False):
        return self.get_property_name("DescriptionKey", create_if_missing)

    def drop_mesh_file(self, create_if_missing: bool=False):
        return self.get_property_name("DropMeshfile", create_if_missing)

    def economic_bundle_size(self, create_if_missing: bool=False):
        return self.get_property_name("EconomicBundleSize", create_if_missing)

    def economic_value(self, create_if_missing: bool=False):
        return self.get_property_name("EconomicValue", create_if_missing)

    def extends(self, create_if_missing: bool=False):
        return self.get_property_name("Meshfile", create_if_missing)

    def group(self, create_if_missing: bool=False):
        return self.get_property_name("Group", create_if_missing)

    def hold_type(self, create_if_missing: bool=False):
        return self.get_property_name("HoldType", create_if_missing)

    def is_developer(self, create_if_missing: bool=False):
        return self.get_property_name("IsDeveleoper", create_if_missing)

    def material(self, create_if_missing: bool=False):
        return self.get_property_name("Material", create_if_missing)

    def mesh_file(self, create_if_missing: bool=False):
        return self.get_property_name("Meshfile", create_if_missing)

    def pickup_journal_entry(self, create_if_missing: bool=False):
        return self.get_property_name("PickupJournalEntry", create_if_missing)

    def stack_number(self, create_if_missing: bool=False):
        return self.get_property_name("StackNumber", create_if_missing)

    def weight(self, create_if_missing: bool=False):
        return self.get_property_name("Weight", create_if_missing)

    def attributes(self, create_if_missing: bool=False):
        create = create_if_missing or self._create_if_missing
        if self._element is None:
            return ItemAttributes(None, self, create_if_missing=create, log_object=self._logger)
        elem = self.get_element("./property[@class='Attributes']")
        return ItemAttributes(elem, self, create_if_missing=create, log_object=self._logger)

    def action0(self, create_if_missing: bool=True):
        create = create_if_missing or self._create_if_missing
        if self._element is None:
            return Action(None, 0, self, create_if_missing=create, log_object=self._logger)
        elem = self.get_element("./property[@class='Action0']")
        return Action(elem, 0, self, create_if_missing=create, log_object=self._logger)

    def action1(self, create_if_missing: bool=True):
        create = create_if_missing or self._create_if_missing
        if self._element is None:
            return Action(None, 0, self, create_if_missing=create, log_object=self._logger)
        elem = self.get_element("./property[@class='Action1']")
        return Action(elem, 1, self, create_if_missing=create, log_object=self._logger)
