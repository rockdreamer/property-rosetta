# -*- coding: utf-8 -*-

import pytest
import os
from pathlib import Path
from property_rosetta.dictionary import DictionaryLoadingError, DictionaryValidationError, \
    DictionaryEnumerationValue, DictionaryEnumeration, \
    DictionaryDataType, DictionaryProperty, DictionaryEntity, Dictionary


TEST_FILES_PATH = Path(__file__).parent / 'data' / 'dictionary_loading'


def test_enumeration_value_loading_from_dict():
    evalue = DictionaryEnumerationValue.from_dict(None, {
        'id': 'a',
        'integral_value': 1,
        'description': 'bar',
    })
    assert evalue.id == 'a'
    assert evalue.integral_value == 1
    assert evalue.description == 'bar'
    assert not evalue.enumeration
    assert not evalue.entity
    assert not evalue.dictionary


def test_enumeration_loading_from_dict():
    evalue = DictionaryEnumeration.from_dict(None, {
        'id': 'anenum',
        'description': 'foo',
        'name': 'anenum of sorts',
        'values': [
            {
                'id': 'a',
                'integral_value': 1,
                'description': 'bar',
            },
        ]
    })
    assert evalue.id == 'anenum'
    assert evalue.name == 'anenum of sorts'
    assert evalue.description == 'foo'
    assert evalue.value_for_id('a').id == 'a'
    assert not evalue.entity
    assert not evalue.dictionary


def test_enumeration_loading_from_yaml_ok():
    DictionaryEnumeration.from_yaml_enum_list(
        None, TEST_FILES_PATH/'enum_ok.yaml')


def test_enumeration_loading_raises_errors():
    with pytest.raises(DictionaryLoadingError):
        DictionaryEnumeration.from_yaml_enum_list(None,
                                                  TEST_FILES_PATH/'nonexistent.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryEnumeration.from_yaml_enum_list(None,
                                                  TEST_FILES_PATH/'enum_noid.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryEnumeration.from_yaml_enum_list(None,
                                                  TEST_FILES_PATH/'enum_noname.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryEnumeration.from_yaml_enum_list(None,
                                                  TEST_FILES_PATH/'enum_value_noid.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryEnumeration.from_yaml_enum_list(None,
                                                  TEST_FILES_PATH/'enum_value_no_integral.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryEnumeration.from_yaml_enum_list(None,
                                                  TEST_FILES_PATH/'enum_value_invalid_integral.yaml')
    with pytest.raises(DictionaryValidationError):
        DictionaryEnumeration.from_yaml_enum_list(None,
                                                  TEST_FILES_PATH/'enum_duplicate_ids.yaml')
    with pytest.raises(DictionaryValidationError):
        DictionaryEnumeration.from_yaml_enum_list(None,
                                                  TEST_FILES_PATH/'enum_duplicate_integrals.yaml')


def test_type_loading_from_dict():
    evalue = DictionaryDataType.from_dict(None, {
        'id': 'atype',
        'description': 'foo',
        'name': 'atype of sorts',
        'semantics': 'reference',
        'attributes':
            {
                'custom_attribute': 'foo',
            },
    })
    assert evalue.id == 'atype'
    assert evalue.name == 'atype of sorts'
    assert evalue.description == 'foo'
    assert evalue.semantics == 'reference'
    assert evalue.deprecated == False
    assert 'custom_attribute' in evalue.attributes
    assert not evalue.dictionary


def test_type_loading_from_yaml_ok():
    result = DictionaryDataType.from_yaml_data_type_list(None,
                                                         TEST_FILES_PATH/'data_types_ok.yaml')
    assert not result[0].attributes
    assert result[1].id == 'bool'
    assert 'boolean_attribute' in result[1].attributes
    assert result[2].deprecated


def test_type_loading_raises_errors():
    with pytest.raises(DictionaryLoadingError):
        DictionaryDataType.from_yaml_data_type_list(None,
                                                    TEST_FILES_PATH/'nonexistent.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryDataType.from_yaml_data_type_list(None,
                                                    TEST_FILES_PATH/'data_types_noid.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryDataType.from_yaml_data_type_list(None,
                                                    TEST_FILES_PATH/'data_types_noname.yaml')


def test_property_loading_from_dict():
    evalue = DictionaryProperty.from_dict(None, {
        'id': 'aproperty',
        'description': 'foo',
        'name': 'aproperty of sorts',
        'type': 'int64',
        'attributes':
            {
                'custom_attribute': 'foo',
            },
    })
    assert evalue.id == 'aproperty'
    assert evalue.name == 'aproperty of sorts'
    assert evalue.description == 'foo'
    assert evalue.type_id == 'int64'
    assert evalue.deprecated == False
    assert 'custom_attribute' in evalue.attributes
    assert not evalue.dictionary
    assert not evalue.dictionary_type


def test_property_loading_from_yaml_ok():
    result = DictionaryProperty.from_yaml_property_list(None,
                                                        TEST_FILES_PATH/'properties_ok.yaml')
    assert result[0].id == 'foo.index'
    assert result[0].type_id == 'int32'
    assert len(result[0].description) > 0
    assert 'minimum_value_inclusive' in result[0].attributes
    assert not result[0].deprecated
    assert result[1].type_id == 'elementid'
    assert result[1].deprecated


def test_property_loading_raises_errors():
    with pytest.raises(DictionaryLoadingError):
        DictionaryProperty.from_yaml_property_list(None,
                                                   TEST_FILES_PATH/'nonexistent.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryProperty.from_yaml_property_list(None,
                                                   TEST_FILES_PATH/'properties_no_id.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryProperty.from_yaml_property_list(None,
                                                   TEST_FILES_PATH/'properties_no_name.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryProperty.from_yaml_property_list(None,
                                                   TEST_FILES_PATH/'properties_no_type.yaml')


def test_entity_loading_from_dict():
    evalue = DictionaryEntity.from_dict(None, {
        'id': 'anentity',
        'description': 'foo',
        'name': 'anentity of sorts',
        'attributes':
            {
                'custom_attribute': 'foo',
            },
        'properties':
            [
                {
                    'id': 'aproperty',
                    'description': 'foo',
                    'name': 'aproperty of sorts',
                    'type': 'int64',

                },
            ]
    })
    assert evalue.id == 'anentity'
    assert evalue.name == 'anentity of sorts'
    assert evalue.description == 'foo'
    assert evalue.deprecated == False
    assert 'custom_attribute' in evalue.attributes
    assert not evalue.dictionary
    assert evalue.properties[0].id == 'aproperty'


def test_entity_loading_from_yaml_ok():
    result = DictionaryEntity.from_yaml_entity_list(None,
                                                    TEST_FILES_PATH/'entities_ok.yaml')
    assert result[0].id == 'ok'
    assert result[0].name == 'An Ok entity'
    assert result[0].description == 'An entity that works'
    assert result[0].attributes['important']
    assert len(result[0].properties) > 0
    assert result[0].property_by_id('ok.index').id == 'ok.index'
    assert result[0].property_by_id('ok.index').attributes['important']


def test_entity_loading_raises_errors():
    with pytest.raises(DictionaryLoadingError):
        DictionaryEntity.from_yaml_entity_list(None,
                                               TEST_FILES_PATH/'nonexistent.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryEntity.from_yaml_entity_list(None,
                                               TEST_FILES_PATH/'entities_missing_properties.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryEntity.from_yaml_entity_list(None,
                                               TEST_FILES_PATH/'entities_no_id.yaml')
    with pytest.raises(DictionaryLoadingError):
        DictionaryEntity.from_yaml_entity_list(None,
                                               TEST_FILES_PATH/'entities_no_name.yaml')


def test_dictionary_loading_from_yaml_ok():
    result = Dictionary.from_yaml_dictionary(
        TEST_FILES_PATH/'dictionary_ok'/'dictionary.yaml')
    assert result.id == 'ok.dictionary'
    assert result.name == 'A proper Dictionary'
    assert result.description == 'Happy path test'
    assert len(result.data_types) > 0
    assert len(result.entities) > 0
    assert result.version == '0.0.1'


def test_dictionary_loading_raises_errors():
    with pytest.raises(DictionaryLoadingError):
        Dictionary.from_yaml_dictionary(TEST_FILES_PATH/'nonexistent.yaml')
    with pytest.raises(DictionaryLoadingError):
        Dictionary.from_yaml_dictionary(
            TEST_FILES_PATH/'dictionary_no_id.yaml')
    with pytest.raises(DictionaryLoadingError):
        Dictionary.from_yaml_dictionary(
            TEST_FILES_PATH/'dictionary_no_name.yaml')
    with pytest.raises(DictionaryLoadingError):
        Dictionary.from_yaml_dictionary(
            TEST_FILES_PATH/'dictionary_no_version.yaml')
    with pytest.raises(DictionaryValidationError):
        Dictionary.from_yaml_dictionary(
            TEST_FILES_PATH/'dictionary_bad_version.yaml')
