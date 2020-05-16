# -*- coding: utf-8 -*-
"""
Rosetta common dictionary classes
"""
import sys
import logging
import yaml
import weakref
from typing import List
from property_rosetta import __version__

__author__ = "Claudio Bantaloukas"
__copyright__ = "Claudio Bantaloukas"
__license__ = "new-bsd"

_logger = logging.getLogger(__name__)


class DictionaryError(Exception):
    """Exception signalling an error in the dictionary"""
    pass


class DictionaryLoadingError(DictionaryError):
    def __init__(self, message: str, exc: Exception):
        """Exception signalling a file or a required value was missing

        Parameters
        ----------
        message : str
            Human readable string describing the exception.
        exc : :obj:`Exception`, optional
            Exception that caused this exception to be thrown

        Attributes
        ----------
        message : str
            Human readable string describing the exception.
        exc : Exception
            Exception that caused this exception to be thrown
        """
        self.message = message
        self.exc = exc


class DictionaryValidationError(DictionaryError):
    """Exception signalling the dictionary didn't pass validation"""
    pass


class DictionaryEnumerationValue(object):
    """A value in an enumeration"""

    def __init__(self, enumeration):
        """A possible enumeration value
        Parameters
        ----------
        enumeration
            The enumeration this value belongs to.

        Attributes
        ----------
        id : str
            A unique identifier for an enumeration value.
        enumeration: DictionaryEnumeration
            The enumeration this value belongs to
        integral_value : int
            A unique numeric value for an enumeration value
        description : str
            a long winded description of the value
        deprecated : bool
            whether the enumeration value is deprecated and should no longer be used
        """
        self.id = None
        self.enumeration = weakref.proxy(enumeration) if enumeration else None
        self.integral_value = None
        self.description = None
        self.deprecated = False

    @property
    def dictionary(self):
        """The dictionary this enumeration value belongs to"""
        return self.enumeration.dictionary if self.enumeration else None

    @property
    def entity(self):
        """The base entity this enumeration value belongs to"""
        return self.enumeration.entity if self.enumeration else None

    @classmethod
    def from_dict(cls, enumeration, d: dict):
        """Create from a python dictionary.

        Parameters
        ----------
        enumeration
            The enumeration this value belongs to.
        d
            The dictionary.

        Returns
        -------
        DictionaryEnumerationValue
            a single value based on the dictionary contents.

        Raises
        ------
        DictionaryLoadingError
            If id or integral_value are missing
        """
        e = DictionaryEnumerationValue(enumeration)
        e.id = d.get('id', None)
        if not e.id:
            raise DictionaryLoadingError(
                'Missing id in enumeration value', None)

        try:
            e.integral_value = int(d['integral_value'])
        except Exception as exc:
            raise DictionaryLoadingError(
                f'Invalid integral_value in enumeration value {e.id}', exc)
        e.description = d.get('description', '')
        e.deprecated = d.get('deprecated', False)
        return e


class DictionaryEnumeration(object):
    def __init__(self, entity):
        """A generic representation of an enumeration
        Parameters
        ----------
        entity
            The base entity this enumeration belongs to.

        Attributes
        ----------
        id : str
            A unique identifier for an enumeration.
        entity : DictionaryEntity
            the entity this enumeration belongs to
        name : int
            A unique readable brief name for an enumeration
        description : str
            a long winded description of the enumeration
        values : list
            a list of accepted values
        deprecated : bool
            whether the enumeration value is deprecated and should no longer be used
        """
        self.id = None
        self.entity = weakref.proxy(entity) if entity else None
        self.name = None
        self.description = None
        self.values = []
        self._values_by_value_id = {}
        self.deprecated = False

    @property
    def dictionary(self):
        """The dictionary this enumeration value belongs to"""
        return self.entity.dictionary if self.entity else None

    def value_for_id(self, id: str) -> DictionaryEnumerationValue:
        """Returns the value assiciated with an id"""
        return self._values_by_value_id[id]

    @classmethod
    def from_dict(cls, entity, d: dict):
        _logger.debug(f"Loading enumeration {d}")
        e = DictionaryEnumeration(entity)
        e.id = d.get('id', None)
        if not e.id:
            raise DictionaryLoadingError('Missing id in enumeration', None)
        e.name = d.get('name', None)
        if not e.name:
            raise DictionaryLoadingError(
                f'Missing name in enumeration {e.id}', None)
        e.description = d.get('description', None)
        e.deprecated = d.get('deprecated', False)
        e.values = [DictionaryEnumerationValue.from_dict(
            e, v) for v in d['values']]
        if len(set([v.id for v in e.values])) != len(e.values):
            raise DictionaryValidationError(
                f'Duplicate value ids in enumeration {e.id}', None)
        if len(set([v.integral_value for v in e.values])) != len(e.values):
            raise DictionaryValidationError(
                f'Duplicate integral values in enumeration {e.id}', None)
        e._values_by_value_id = {v.id: weakref.proxy(v) for v in e.values}
        return e

    @classmethod
    def from_yaml_enum_list(cls, entity, path) -> List:
        """Returns a list of enumerations from a yaml file"""
        try:
            _logger.debug(f"Loading enumerations from {path}")
            with open(path) as f:
                yamlenum = yaml.safe_load(f)
            return [DictionaryEnumeration.from_dict(entity, d) for d in yamlenum]
        except (OSError, yaml.YAMLError) as exc:
            raise DictionaryLoadingError(
                f"Error reading enumeration file: {path}", exc)


class DictionaryDataType(object):
    def __init__(self, dictionary):
        """A generic representation of a data type
        Parameters
        ----------
        dictionary
            The dictionary this data type belongs to.

        Attributes
        ----------
        id : str
            A unique identifier for an enumeration.
        dictionary
            The dictionary this data type belongs to.
        name : int
            A unique readable brief name for an enumeration
        description : str
            a long winded description of the enumeration
        semantics : string
            whether the type has value semantics or not
        attributes : map
            custom attributes of the data type, used to inform code generation
        deprecated : bool
            whether the enumeration value is deprecated and should no longer be used
        """
        self.id = None
        self.dictionary = weakref.proxy(dictionary) if dictionary else None
        self.name = None
        self.description = None
        self.semantics = 'value'
        self.attributes = {}
        self.deprecated = False

    @classmethod
    def from_dict(cls, dictionary, d: dict):
        _logger.debug(f"Loading data type {d}")
        e = DictionaryDataType(dictionary)
        e.id = d.get('id', None)
        if not e.id:
            raise DictionaryLoadingError('Missing id in data type', None)
        e.name = d.get('name', None)
        if not e.name:
            raise DictionaryLoadingError(
                f'Missing name in data type {e.id}', None)
        e.description = d.get('description', None)
        e.semantics = d.get('semantics', 'value')
        e.attributes = d.get('attributes', {})
        e.deprecated = d.get('deprecated', False)
        return e

    @classmethod
    def from_yaml_data_type_list(cls, dictionary, path) -> List:
        """Returns a list of enumerations from a yaml file"""
        try:
            _logger.debug(f"Loading data types from {path}")
            with open(path) as f:
                yamlenum = yaml.safe_load(f)
            ret = []
            for dt in yamlenum:
                v = DictionaryDataType.from_dict(dictionary, dt)
                attributes_path = path.parent / \
                    'data-type-attributes' / f'{v.id}.yaml'
                if attributes_path.exists():
                    _logger.debug(
                        f"Loading attributes for data type {v.id} from {attributes_path}")
                    with open(attributes_path) as af:
                        attributes = yaml.safe_load(af)
                        v.attributes = attributes
                ret.append(v)
            return ret
        except (OSError, yaml.YAMLError) as exc:
            raise DictionaryLoadingError(
                f"Error reading enumeration file: {path}", exc)


class DictionaryProperty(object):
    def __init__(self, entity):
        """A generic representation of a property of an entity

        Parameters
        ----------
        entity
            The entity this property belongs to.


        Attributes
        ----------
        dictionary
            The dictionary this data type belongs to.
        id : str
            A unique identifier for an enumeration.
        name : int
            A unique readable brief name for an enumeration
        type_id : str
            a long winded description of the enumeration
        semantics : string
            whether the type has value semantics or not
        attributes : map
            custom attributes that extend what is provided by the type. Useful to inform code generators
        deprecated : bool
            whether the enumeration value is deprecated and should no longer be used
        """
        self.id = None
        self.entity = weakref.proxy(entity) if entity else None
        self.name = None
        self.type_id = None
        self.description = None
        self.entity_id = None
        self.attributes = {}

    @property
    def dictionary(self):
        """The dictionary this enumeration value belongs to"""
        return self.entity.dictionary if self.entity else None

    @property
    def dictionary_type(self):
        return self.dictionary.type_by_id(self.type_id) if self.dictionary else None

    @classmethod
    def from_dict(cls, entity, d: dict):
        _logger.debug(f"Loading property {d}")
        e = DictionaryProperty(entity)
        e.id = d.get('id', None)
        if not e.id:
            raise DictionaryLoadingError('Missing id in property', None)
        e.name = d.get('name', None)
        if not e.name:
            raise DictionaryLoadingError(
                f'Missing name in property {e.id}', None)
        e.type_id = d.get('type', None)
        if not e.type_id:
            raise DictionaryLoadingError(
                f'Missing type in property {e.id}', None)
        e.description = d.get('description', None)
        e.attributes = d.get('attributes', {})
        e.deprecated = d.get('deprecated', False)
        return e

    @classmethod
    def from_yaml_property_list(cls, entity, path) -> List:
        """Returns a list of properties from a yaml file"""
        try:
            _logger.debug(f"Loading properties from {path}")
            with open(path) as f:
                yamllist = yaml.safe_load(f)
            return [DictionaryProperty.from_dict(entity, prop) for prop in yamllist]
        except (OSError, yaml.YAMLError) as exc:
            raise DictionaryLoadingError(
                f"Error reading property list file: {path}", exc)


class DictionaryEntity(object):
    """A generic representation of a base entity"""

    def __init__(self, dictionary):
        """A generic representation of a base entity

        Parameters
        ----------
        dictionary
            The dictionary this property belongs to.


        Attributes
        ----------
        id : str
            A unique identifier for a base entity
        name : str
            A unique readable brief name for a base entity
        properties : list
            a list of properties that the entity can contain
        attributes : map
            custom attributes of the base entity. Useful to inform code generators
        deprecated : bool
            whether the entity is deprecated and should no longer be used
        """
        self.dictionary = weakref.proxy(dictionary) if dictionary else None
        self.id = None
        self.name = None
        self.description = None
        self.properties = []
        self._properties_by_id = {}
        self.attributes = {}
        self.deprecated = False

    def property_by_id(self, property_id):
        return self._properties_by_id.get(property_id, None)

    @classmethod
    def from_dict(cls, dictionary, d: dict):
        _logger.debug(f"Loading entity {d}")
        e = DictionaryEntity(dictionary)
        e.id = d.get('id', None)
        if not e.id:
            raise DictionaryLoadingError('Missing id in entity', None)
        e.name = d.get('name', None)
        if not e.name:
            raise DictionaryLoadingError(
                f'Missing name in entity {e.id}', None)
        e.description = d.get('description', None)
        if 'properties' in d:
            e.properties = [DictionaryProperty.from_dict(
                dictionary, p) for p in d['properties']]
            e._properties_by_id = {
                p.id: weakref.proxy(p) for p in e.properties}
        e.attributes = d.get('attributes', {})
        e.deprecated = d.get('deprecated', False)
        return e

    @classmethod
    def from_yaml_entity_list(cls, dictionary, path) -> List:
        """Returns a list of entities from a yaml file"""
        try:
            _logger.debug(f"Loading entities from {path}")
            with open(path) as f:
                yamlentities = yaml.safe_load(f)
            ret = []
            for e in yamlentities:
                v = DictionaryEntity.from_dict(dictionary, e)
                properties_path = path.parent / \
                    'properties-by-entity' / f'{v.id}.yaml'
                _logger.debug(
                    f"Loading properties for entity {v.id} from {properties_path}")
                v.properties = DictionaryProperty.from_yaml_property_list(
                    v, properties_path)
                v._properties_by_id = {
                    p.id: weakref.proxy(p) for p in v.properties}
                ret.append(v)
            return ret
        except (OSError, yaml.YAMLError) as exc:
            raise DictionaryLoadingError(
                f"Error reading enumeration file: {path}", exc)


class Dictionary(object):
    """A common dictionary for bridging dialects

    The dictionary provides a common set of:
    * types and custom type attributes
    * base entities
    * properties contained within each entity
    * enumeration values
    """

    def __init__(self):
        self.id = None
        self.description = None
        self.version = None
        self.data_types = None
        self.entities = []

    @classmethod
    def from_dict(cls, d: dict):
        import semver
        _logger.debug(f"Loading dictionary {d}")
        e = Dictionary()
        e.id = d.get('id', None)
        if not e.id:
            raise DictionaryLoadingError('Missing id in dictionary', None)
        e.name = d.get('name', None)
        if not e.name:
            raise DictionaryLoadingError(
                f'Missing name in dictionary {e.id}', None)
        e.description = d.get('description', None)
        e.version = d.get('version', None)
        if not e.version:
            raise DictionaryLoadingError(
                f'Missing version in dictionary {e.id}', None)
        if not e.version in ['master', 'development'] and not semver.VersionInfo.isvalid(e.version):
            raise DictionaryValidationError(
                f'Version {e.version} in dictionary {e.id} is invalid')
        e.deprecated = d.get('deprecated', False)
        return e

    @classmethod
    def from_yaml_dictionary(cls, path) -> List:
        """Returns a dictionary from a yaml file using files in relative paths"""
        try:
            _logger.debug(f"Loading dictionary from {path}")
            with open(path) as f:
                yamldictionary = yaml.safe_load(f)
            ret = Dictionary.from_dict(yamldictionary)
        except (OSError, yaml.YAMLError) as exc:
            raise DictionaryLoadingError(
                f"Error reading dictionary file: {path}", exc)
        datatypes_path = path.parent / 'data-types.yaml'
        ret.data_types = DictionaryDataType.from_yaml_data_type_list(
            ret, datatypes_path)
        entities_path = path.parent / 'entities.yaml'
        ret.entities = DictionaryEntity.from_yaml_entity_list(
            ret, entities_path)
        return ret

    def validate(self):
        return []
