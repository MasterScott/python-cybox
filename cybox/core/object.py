# Copyright (c) 2013, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

import cybox
import cybox.utils as utils
import cybox.bindings.cybox_core as core_binding
#import cybox.core.structured_text as Structured_Text
from cybox.common import ObjectProperties, VocabString
#from cybox.common.measuresource import Measure_Source


class Object(cybox.Entity):
    """The CybOX Object element.

    Currently only supports the following data members:
    - id_
    - idref
    - properties
    - related_objects
    """
    _binding = core_binding
    _namespace = 'http://cybox.mitre.org/cybox-2'

    def __init__(self, properties=None, type_=None):
        # TODO: Accept id_ as an argument
        if properties:
            prefix = str(properties.__class__.__name__)
        else:
            prefix = "Object"
        self.id_ = utils.create_id(prefix=prefix)
        self.idref = None
        self.properties = properties
        self.related_objects = []
        self.domain_specific_object_attributes = None

    def __str__(self):
        return self.id_

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        if value and not isinstance(value, ObjectProperties):
            raise ValueError("Not a ObjectProperties")
        self._properties = value

        self._modify_childs_parent()

    def _modify_childs_parent(self):
        if self._properties:
            self._properties.parent = self

    def add_related(self, related, relationship, inline=True):
        if not isinstance(related, ObjectProperties):
            raise ValueError("Must be a ObjectProperties")
        r = RelatedObject(related, relationship=relationship, inline=inline)
        self.related_objects.append(r)

    def to_obj(self, bindings_obj=None):
        if bindings_obj == None:
            obj = core_binding.ObjectType()
        else:
            obj = bindings_obj

        if self.id_:
            obj.set_id(self.id_)
        if self.idref:
            obj.set_idref(self.idref)
        if self.properties:
            obj.set_Properties(self.properties.to_obj())
        if self.related_objects:
            relobj_obj = core_binding.RelatedObjectsType()
            for x in self.related_objects:
                relobj_obj.add_Related_Object(x.to_obj())
            obj.set_Related_Objects(relobj_obj)
        if self.domain_specific_object_attributes is not None:
            obj.set_Domain_Specific_Object_Attributes(self.domain_specific_object_attributes.to_obj())

        return obj

    def to_dict(self):
        obj_dict = {}
        if self.id_:
            obj_dict['id'] = self.id_
        if self.idref:
            obj_dict['idref'] = self.idref
        if self.properties:
            obj_dict['properties'] = self.properties.to_dict()
        if self.related_objects:
            obj_dict['related_objects'] = [x.to_dict() for x in
                                                self.related_objects]
        #if self.domain_specific_object_attributes is not none: pass

        return obj_dict

    @staticmethod
    def from_obj(object_obj, obj_class=None):
        if not object_obj:
            return None

        if obj_class == None:
            obj = Object()
        else:
            obj = obj_class

        obj.id_ = object_obj.get_id()
        obj.idref = object_obj.get_idref()
        obj.properties = ObjectProperties.from_obj(object_obj.get_Properties())
        obj.domain_specific_object_attributes = object_obj.get_Domain_Specific_Object_Attributes()
        rel_objs = object_obj.get_Related_Objects()
        if rel_objs:
            obj.related_objects = [RelatedObject.from_obj(x) for x in
                                   rel_objs.get_Related_Object()]

        if obj.id_:
            cybox.utils.cache_put(obj)

        return obj

    @staticmethod
    def from_dict(object_dict, obj_class=None):
        if not object_dict:
            return None

        if obj_class == None:
            obj = Object()
        else:
            obj = obj_class

        obj.id_ = object_dict.get('id')
        obj.idref = object_dict.get('idref')
        obj.properties = ObjectProperties.from_dict(
                                    object_dict.get('properties'))
        obj.related_objects = [RelatedObject.from_dict(x) for x in
                                        object_dict.get('related_objects', [])]
        obj.domain_specific_object_attributes = object_dict.get('domain-specific_object_attributes')

        if obj.id_:
            cybox.utils.cache_put(obj)

        return obj


class Relationship(VocabString):
    _XSI_TYPE = 'cyboxVocabs:ObjectRelationshipVocab-1.0'


class RelatedObject(Object):

    def __init__(self, *args, **kwargs):
        self.relationship = kwargs.pop('relationship', None)
        self._inline = kwargs.pop('inline', True)
        super(RelatedObject, self).__init__(*args, **kwargs)
        if not self._inline and self.properties:
            self.idref = self.properties.parent.id_

    def __str__(self):
        return "Related: " + super(RelatedObject, self).__str__()

    #TODO: make this a property somehow
    def get_properties(self):
        if self.properties:
            return self.properties
        elif self.idref:
            try:
                return cybox.utils.cache_get(self.idref).properties
            except cybox.utils.CacheMiss:
                #TODO: take out
                print cybox.utils.caches._get_cache()._DictCache__inner.items()
                raise
        else:
            return None

    def _modify_childs_parent(self):
        if self._inline:
            super(RelatedObject, self)._modify_childs_parent()

    @property
    def relationship(self):
        return self._relationship

    @relationship.setter
    def relationship(self, value):
        if value and not isinstance(value, Relationship):
            value = Relationship(value)
        self._relationship = value

    def to_obj(self):
        relobj_obj = core_binding.RelatedObjectType()

        if self._inline:
            super(RelatedObject, self).to_obj(relobj_obj)
        else:
            relobj_obj.set_idref(self.idref)

        if self.relationship:
            relobj_obj.set_Relationship(self.relationship.to_obj())

        return relobj_obj

    def to_dict(self):

        if self._inline:
            relobj_dict = super(RelatedObject, self).to_dict()
        else:
            relobj_dict = {'idref': self.idref}

        if self.relationship:
            relobj_dict['relationship'] = self.relationship.to_dict()

        return relobj_dict

    @staticmethod
    def from_obj(relobj_obj):
        if not relobj_obj:
            return None

        relobj = RelatedObject()
        Object.from_obj(relobj_obj, relobj)
        relobj.relationship = Relationship.from_obj(relobj_obj.get_Relationship())

        if relobj.idref:
            relobj._inline = True

        return relobj

    @staticmethod
    def from_dict(relobj_dict):
        if not relobj_dict:
            return None

        relobj = RelatedObject()
        Object.from_dict(relobj_dict, relobj)
        relobj.relationship = Relationship.from_dict(relobj_dict.get('relationship'))

        if relobj.idref:
            relobj._inline = True

        return relobj
