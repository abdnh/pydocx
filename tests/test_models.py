# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.models import (
    XmlModel,
    XmlCollection,
    XmlChild,
    XmlAttribute,
    XmlRootElementMismatchException,
)

from pydocx.util.xml import parse_xml_from_string


class AppleModel(XmlModel):
    XML_TAG = 'apple'

    type = XmlAttribute(default='Honey Crisp')


class OrangeModel(XmlModel):
    XML_TAG = 'orange'

    type = XmlAttribute(default='Organic')


class ItemsModel(XmlModel):
    XML_TAG = 'items'

    items = XmlCollection(
        ('apple', AppleModel),
        OrangeModel,
    )


class PropertiesModel(XmlModel):
    XML_TAG = 'prop'

    color = XmlChild(attrname='val')


class BucketModel(XmlModel):
    XML_TAG = 'bucket'

    items = XmlChild(type=ItemsModel)

    agua = XmlChild(name='water')
    attr_child = XmlChild(attrname='foo')

    # tag name is set by the Model itself via the XML_TAG attribute
    properties = XmlChild(type=PropertiesModel)


class BaseTestCase(TestCase):
    def _get_model_instance_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return self.model.load(root)


class XmlAttributeTestCase(BaseTestCase):
    model = AppleModel

    def test_default_attribute(self):
        xml = '<apple />'
        apple = self._get_model_instance_from_xml(xml)
        self.assertEqual(apple.type, 'Honey Crisp')

    def test_attribute_when_set(self):
        xml = '<apple type="Gala" />'
        apple = self._get_model_instance_from_xml(xml)
        self.assertEqual(apple.type, 'Gala')


class XmlChildTestCase(BaseTestCase):
    model = BucketModel

    def test_None_if_not_present(self):
        xml = '<bucket />'
        bucket = self._get_model_instance_from_xml(xml)
        self.assertEqual(bucket.items, None)

    def test_using_a_name_different_than_the_field_name(self):
        xml = '''
            <bucket>
                <water />
            </bucket>
        '''
        bucket = self._get_model_instance_from_xml(xml)
        self.assertEqual(bucket.agua.tag, 'water')

    def test_child_without_type_is_an_element(self):
        xml = '''
            <bucket>
                <water />
            </bucket>
        '''
        bucket = self._get_model_instance_from_xml(xml)
        root = parse_xml_from_string(xml)
        self.assertEqual(type(bucket.agua), type(root))

    def test_child_with_attrname_is_the_string_value_of_that_attr(self):
        xml = '''
            <bucket>
                <attr_child foo="bar" />
            </bucket>
        '''
        bucket = self._get_model_instance_from_xml(xml)
        self.assertEqual(bucket.attr_child, 'bar')

    def test_child_with_attrname_when_missing_is_None(self):
        xml = '<bucket />'
        bucket = self._get_model_instance_from_xml(xml)
        self.assertEqual(bucket.attr_child, None)

    def test_child_determines_tag_name(self):
        xml = '''
            <bucket>
                <prop>
                    <color val="blue" />
                </prop>
            </bucket>
        '''
        bucket = self._get_model_instance_from_xml(xml)
        self.assertEqual(bucket.properties.color, 'blue')

    def test_failure_if_root_tag_mismatch(self):
        xml = '<notabucket />'
        try:
            self._get_model_instance_from_xml(xml)
            raise AssertionError('Expected XmlRootElementMismatchException')
        except XmlRootElementMismatchException:
            pass


class XmlCollectionTestCase(BaseTestCase):
    model = BucketModel

    def test_items_items_empty_if_no_items_present(self):
        xml = '''
            <bucket>
                <items>
                </items>
            </bucket>
        '''
        bucket = self._get_model_instance_from_xml(xml)
        self.assertEqual(bucket.items.items, [])

    def test_non_captured_items_are_ignored_by_collection(self):
        # The items collection does not capture bananas, so it's ignored
        xml = '''
            <bucket>
                <items>
                    <banana />
                </items>
            </bucket>
        '''
        bucket = self._get_model_instance_from_xml(xml)
        self.assertEqual(bucket.items.items, [])

    def test_apples_and_oranges_included_in_collection_ordered(self):
        xml = '''
            <bucket>
                <items>
                    <apple />
                    <orange />
                    <apple />
                    <orange />
                </items>
            </bucket>
        '''
        bucket = self._get_model_instance_from_xml(xml)
        classes = [
            item.__class__
            for item in bucket.items.items
        ]
        expected_classes = [
            AppleModel,
            OrangeModel,
            AppleModel,
            OrangeModel,
        ]
        self.assertEqual(classes, expected_classes)

    def test_apples_and_oranges_models_accessed_through_collection(self):
        xml = '''
            <bucket>
                <items>
                    <apple type='one' />
                    <orange type='two' />
                    <apple type='three' />
                    <orange type='four' />
                </items>
            </bucket>
        '''
        bucket = self._get_model_instance_from_xml(xml)
        types = [
            item.type
            for item in bucket.items.items
        ]
        expected_types = [
            'one',
            'two',
            'three',
            'four',
        ]
        self.assertEqual(types, expected_types)
