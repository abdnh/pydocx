from __future__ import absolute_import

import posixpath

from pydocx.openxml import (
    OpenXmlPart,
    OpenXmlPackage,
)


class ChildPartLoader(object):
    child_part_types = NotImplemented

    def get_relationship_lookup(self):
        raise NotImplementedError

    def load_parts(self):
        relationship_lookup = self.get_relationship_lookup()
        for child_part_type in self.child_part_types:
            relationships = relationship_lookup.get_relationships_by_type(
                child_part_type.relationship_type,
            )
            if not relationships:
                continue
            relationship = relationships[0]
            base, _ = posixpath.split(relationship.source_uri)
            part_uri = posixpath.join(
                base,
                relationship.target_uri,
            )
            part = child_part_type(
                open_xml_package=self,
                uri=part_uri,
            )
            self.add_part(
                part=part,
                relationship_id=relationship.relationship_id,
            )


class ImagePart(OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'image',
    ])


class StyleDefinitionsPart(OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'styles',
    ])


class NumberingDefinitionsPart(OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'numbering',
    ])


class FontTablePart(OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'fontTable',
    ])


class MainDocumentPart(ChildPartLoader, OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'officeDocument',
    ])

    child_part_types = [
        FontTablePart,
        ImagePart,
        NumberingDefinitionsPart,
        StyleDefinitionsPart,
    ]

    def get_relationship_lookup(self):
        package_lookup = self.open_xml_package.get_relationship_lookup()
        return package_lookup.get_part(self.uri)

    def get_part_of_type(self, part_class):
        self.ensure_parts_are_loaded()
        parts = self.get_parts_of_type(
            part_class.relationship_type,
        )
        if parts:
            return parts[0]

    @property
    def style_definitions_part(self):
        return self.get_part_of_type(StyleDefinitionsPart)

    @property
    def numbering_definitions_part(self):
        return self.get_part_of_type(NumberingDefinitionsPart)

    @property
    def font_table_part(self):
        return self.get_part_of_type(FontTablePart)

    @property
    def image_parts(self):
        return self.get_parts_of_type(
            relationship_type=ImagePart.relationship_type,
        )


class WordprocessingDocument(ChildPartLoader, OpenXmlPackage):
    namespace = '/'.join([
        'http://schemas.openxmlformats.org',
        'wordprocessingml',
        '2006',
        'main',
    ])

    child_part_types = [
        MainDocumentPart,
    ]

    def get_relationship_lookup(self):
        return self.package

    @property
    def main_document_part(self):
        self.ensure_parts_are_loaded()
        return self.get_parts_of_type(
            MainDocumentPart.relationship_type,
        )[0]


class Document(object):
    pass
