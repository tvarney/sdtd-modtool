
import xml.etree.ElementTree as ElementTree
from sdtd.log import Logger, PrintLogger
import sdtd.util


# The goal here is a class which provides arbitrary access down into an XML tree, only creating the nodes if needed.
# In addition, errors when messing around with the tree should not stop execution with exceptions; failing should be
# reported in some fashion, but otherwise not raise an exception.
class XMLWrapper(object):
    def __init__(self, xml_element, name, parent=None, **kwargs):
        """
        Keyword arguments:
        create_if_missing -- If methods which need a concrete element should create it if missing
        log_object -- The logging object to report error details to

        :param xml_element: The xml.etree.ElementTree.Element object backing this instance
        :param name: The name representing this. XPath specification usually
        :param parent: The parent XMLWrapper instance if possible
        :param kwargs:
        """
        self._element = xml_element  # type: ElementTree.Element
        self._name = name            # type: str
        self._parent = parent        # type: XMLWrapper

        self._create_if_missing = kwargs.get("create_if_missing", False)  # type: bool
        self._logger = kwargs.get("log_object", PrintLogger())  # type: Logger

    def create_if_missing(self, state: bool):
        """Set the behavior of the find method when the given tag is missing
        :param state: If the find method should create missing tags by default
        """
        self._create_if_missing = state

    def exists(self) -> bool:
        """Check if this XMLWrapper object is backed by an existing ElementTree.Element object
        :return: If this object has a backing XML Element
        """
        return self._element is not None

    def tag(self) -> str:
        """Get the element tag for this XML Element, or None if this XMLWrapper object is not backed by one
        :return: The element tag for this XML Element
        """
        return None if not self.exists() else self._element.tag

    def attributes(self) -> dict:
        """Get the element attributes for this XML Element, or None if this XMLWrapper object is not backed by one
        :return: The attributes dict for this XML Element
        """
        return None if not self.exists() else self._element.attrib

    def raw(self) -> ElementTree.Element:
        """
        :return: The backing ElementTree.Element object for this XMLWrapper object
        """
        return self._element

    def set(self, attribute: str, value: str, create_if_missing: bool=False) -> bool:
        """Set an attribute value on this XMLWrapper object

        This method will create the backing elements all the way up the tree if possible in order to set the attribute.

        :param attribute: The attribute name to set
        :param value: The value to set the attribute to
        :param create_if_missing: If the attribute should be added if missing
        :return: If the attribute was set successfully
        """
        if not self.exists():
            if self._create_if_missing or create_if_missing:
                if not self.create():
                    self._logger.printf("Error: Could not create {}", self._get_invalid_element())
                    return False
            else:
                return False

        self._element.set(attribute, value)
        return True

    def get(self, attribute: str) -> str:
        """Get an attribute value from this XMLWrapper object
        :param attribute: The attribute to get the value from
        :return:
        """
        if self._element is None:
            return None
        return self._element.get(attribute)

    def find(self, tag: str, attributes: dict, create_if_missing: bool=False):
        """Attempt to find a valid sub-element denoted by the given xml_type and attributes

        :param tag: The XML tag type of the element to find
        :param attributes: The attributes to search for on the given tag
        :param create_if_missing: If the attribute should be created if missing

        :return: An XMLWrapper
        """
        create = create_if_missing or self._create_if_missing
        xpath_spec = sdtd.util.fmt_xpath_spec(tag, attributes)
        if self._element is None:
            if create:
                if not self.create():
                    return XMLWrapper(None, xpath_spec, self, create_if_missing=False, log_object=self._logger)
            else:
                return XMLWrapper(None, xpath_spec, self, create_if_missing=create, log_object=self._logger)

        # If we hit this point self._element is valid, either because we created it, or it already existed
        elem = self._element.find("./"+xpath_spec)
        if elem is None and create:
            elem = ElementTree.SubElement(self._element, tag, attributes)
        return XMLWrapper(elem, xpath_spec, self, create_if_missing=create, log_object=self._logger)

    def get_element(self, xpath_spec: str):
        """Get the child element specified by the arguments
        :param xpath_spec: The xpath spec to use to look up the element
        :return: The element if it could be found
        """
        if self._element is None:
            return None
        return self._element.find(xpath_spec)

    def create(self) -> bool:
        """Recursively create elements until this element can be created.

        This function will travel up until it reaches an element for which self._parent exists and has a valid element.
        At that point, it will attempt to create itself by calling self._create_impl(). self._create_impl() is not
        provided for generic XMLWrapper classes.

        :return: If the creation of this element succeeded
        """
        if self._element is None:
            if self._parent is not None:
                if not self._parent.exists():
                    if not self._parent.create():
                        return False
                return self._create_impl()
            else:
                self._logger.printf("Can not create {}: Missing parent", str(self))
                return False

    def _create_impl(self) -> bool:
        """Implementation of the self.create() method

        This function should be overloaded for any class which extends XMLWrapper and wants to provide automatic
        creation on attribute set.

        :return: If the creation and registration of the new XML element succeeded
        """
        self._logger.printf("Can not create generic XML Element for {}".format(str(self)))
        return False

    def remove(self):
        """Remove self from parent element if able to do so

        This function will remove itself from the parent element if the following conditions are met:
        self._element is not None
        self._parent is not None
        self._parent.exists()

        If the conditions are not met, the function does nothing and returns.
        """
        if self._element is not None and self._parent is not None and self._parent.exists():
            self._parent._element.remove(self._element)

    def _get_invalid_element(self):
        if self._parent is None or self._parent._element is not None:
            return self
        else:
            return self._parent._get_invalid_element()

    def __str__(self):
        if self._parent is None:
            return self._name
        return "{}/{}".format(str(self._parent), self._name)


class PropertyName(XMLWrapper):
    def __init__(self, element, name: str, parent=None, **kwargs):
        XMLWrapper.__init__(self, element, "property[@name='{}']".format(name), parent, **kwargs)
        self._attrib_name = name

    def _create_impl(self):
        self._element = ElementTree.SubElement(self._parent._element, "property", {"name": self._attrib_name})
        return True


class PropertyContainer(XMLWrapper):
    def __init__(self, element, name: str, parent=None, **kwargs):
        XMLWrapper.__init__(self, element, name, parent, **kwargs)

    def get_property_class(self, class_name: str, create_if_missing: bool):
        elem = self.get_element("./property[@class='{}']".format(class_name))
        create = create_if_missing or self._create_if_missing
        return PropertyClass(elem, class_name, self, create_if_missing=create, log_oobject=self._logger)

    def get_property_name(self, name: str, create_if_missing: bool):
        elem = self.get_element("./property[@name='{}']".format(name))
        create = create_if_missing or self._create_if_missing
        return PropertyName(elem, name, self, create_if_missing=create, log_object=self._logger)


class PropertyClass(PropertyContainer):
    def __init__(self, element, name: str, parent=None, **kwargs):
        PropertyContainer.__init__(self, element, "property[@class='{}']".format(name), parent, **kwargs)
        self._attrib_class = name

    def _create_impl(self):
        self._element = ElementTree.SubElement(self._parent._element, "property", {"class": self._attrib_class})
        return True
