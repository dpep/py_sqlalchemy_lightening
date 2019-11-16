import logging

from sqlalchemy import event
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr, DeclarativeMeta
from sqlalchemy.orm import Mapper, RelationshipProperty, foreign
from sqlalchemy.sql.schema import Column, Index
from sqlalchemy.types import *

from . import LighteningBase, relationship
from .result_list import ResultList

logger = logging.getLogger(__name__)


__all__ = [
    'association',
    'init_assocs',
]


association_cls = None
class AssociationProxy(object):
    def __getattribute__(self, name):
        return getattr(association_cls, name)
    def __str__(self):
        return str(association_cls)
    def __repr__(self):
        return repr(association_cls)

Association = AssociationProxy()


def init_assocs(base_cls, tablename=None):
    '''
    Initialize association library and establish a sqlalchemy model
    to persist associations.
    '''
    global association_cls

    if association_cls:
        raise ValueError(
            'Association class already initialized: ', association_cls
        )

    # create new type to model the assoc table
    association_cls = type('Association', (AssociationBase, base_cls), {})
    if tablename:
        association_cls.__tablename__ = tablename


def association(to_class, **kwargs):
    if association_cls is None:
        raise Exception(
            'must initialize Association table via init_assocs()'
        )

    # upgrade collection class
    if kwargs.get('collection_class') is None:
        kwargs['collection_class'] = ResultList

    return AssociationProperty(to_class, **kwargs)


class AssociationProperty(RelationshipProperty):
    def __init__(self, to_class, **kwargs):
        self.assoc_type = kwargs.pop('type', None)

        super(AssociationProperty, self).__init__(
            to_class,
            viewonly=True,
            primaryjoin=lambda: None,  # stub for now
            **kwargs
        )


    def do_init(self):
        to_class = self.argument()
        from_class = self.parent.class_

        if self.assoc_type is None:
            # default to the field name
            self.assoc_type = self.key

        # build join now that parent's class is known
        self.primaryjoin = foreign(Association.assoc_type) == self.assoc_type
        self.primaryjoin &= foreign(Association.from_id) == from_class.id
        self.primaryjoin &= foreign(Association.from_type) == from_class.__name__

        self.secondary = Association.__table__
        self.secondaryjoin = Association.to_id == foreign(to_class.id)
        self.secondaryjoin &= Association.to_type == to_class.__name__


        if self.assoc_type == self.key:
            type_msg = ''
        else:
            type_msg = '  (%s)' % self.assoc_type

        logger.info(
            'association: %s.%s => %s%s' % (
                from_class.__name__,
                self.key,
                to_class.__name__,
                type_msg,
            )
        )

        # wire up collection operations so they persist
        field = getattr(from_class, self.key)

        if self.uselist == False:
            @event.listens_for(field, 'set')
            def on_set(target, value, oldvalue, initiator):
                if oldvalue:
                    Association.delete(self.assoc_type, target, oldvalue)

                    if 'delete-orphan' in self.cascade:
                        oldvalue.delete()

                if value:
                    Association.add(self.assoc_type, target, value)
        else:
            @event.listens_for(field, 'append')
            def on_append(target, value, initiator):
                # check/warn for null target.id or value.id ??
                Association.add(self.assoc_type, target, value)

            @event.listens_for(field, 'remove')
            def on_remove(target, value, initiator):
                Association.delete(self.assoc_type, target, value)

                if 'delete-orphan' in self.cascade:
                    value.delete()


        # https://docs.sqlalchemy.org/en/13/orm/events.html#sqlalchemy.orm.events.AttributeEvents.dispose_collection
        # TODO: handle dispose_collection / init_collection events, eg. user.friends = [<new list>] ?
        # TODO: cascade 'delete'

        return super(AssociationProperty, self).do_init()



class AssociationBase(LighteningBase):
    __tablename__ = 'sal_association'


    assoc_type = Column(String(40))
    from_id = Column(Integer)
    from_type = Column(String(40))
    to_id = Column(Integer)
    to_type = Column(String(40))

    __table_args__ = (
        Index('idx_sal_assoc_join', 'assoc_type', 'from_type', 'from_id'),
    )


    @classmethod
    def add(cls, assoc_type, from_, to):
        return cls(
            assoc_type=assoc_type,
            from_id=from_.id,
            from_type=from_.__class__.__name__,
            to_id=to.id,
            to_type=to.__class__.__name__,
        ).save()


    @classmethod
    def load(cls, assoc_type, from_, to):
        return cls.where(
            assoc_type=assoc_type,
            from_id=from_.id,
            from_type=from_.__class__.__name__,
            to_id=to.id,
            to_type=to.__class__.__name__,
        )


    @classmethod
    def delete(cls, assoc_type, from_, to):
        return cls.load(assoc_type, from_, to).delete()


    def __repr__(self):
        return '%s(%s).%s => %s(%s)' % (
            self.from_type,
            self.from_id,
            self.assoc_type,
            self.to_type,
            self.to_id,
        )
