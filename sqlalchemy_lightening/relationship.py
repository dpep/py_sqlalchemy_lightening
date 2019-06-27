import logging

from sqlalchemy import event
from sqlalchemy.exc import NoForeignKeysError
from sqlalchemy.orm import foreign, Mapper, RelationshipProperty

from .result_list import ResultList


logger = logging.getLogger(__name__)


class RelationshipWrapper(RelationshipProperty):
    def do_init(self):
        try:
            # see if it works as is
            return super(RelationshipWrapper, self).do_init()
        except NoForeignKeysError as error:
            # nope, try to construct the relationship

            try:
                # only the extreme base case is supported
                if self.secondary or self.primaryjoin or self.secondaryjoin or self._user_defined_foreign_keys or (self.uselist is not None):
                    raise NotImplementedError()

                class_ = self.parent.class_
                foreign_class = self.argument()


                # check for many-to-one relationship
                foreign_key = self.key + '_id'
                if hasattr(class_, foreign_key):
                    id_col = getattr(class_, foreign_key)
                    foreign_col = getattr(foreign_class, 'id')

                    self.primaryjoin = id_col == foreign(foreign_col)
                    self.uselist = False
                    self.viewonly = True  # custom update logic below

                    logger.info(
                        'implicit many-to-one relationship: %s.%s: %s' % (
                            class_.__name__,
                            self.key,
                            self.primaryjoin,
                        )
                    )

                    # retry mapping the relationship
                    rel = super(RelationshipWrapper, self).do_init()

                    # set foreign key (XXX_id) during relationship update
                    @event.listens_for(getattr(class_, self.key), "set")
                    def on_set(target, value, oldvalue, initiator):
                        if value:
                            setattr(target, foreign_key, value.id)
                        else:
                            setattr(target, foreign_key, None)

                    return rel


                # check for one-to-many relationship
                foreign_key = class_.__table__.name + '_id'
                if hasattr(foreign_class, foreign_key):
                    id_col = getattr(class_, 'id')
                    foreign_col = getattr(foreign_class, foreign_key)

                    if not (foreign_col.index or foreign_col.unique):
                        # do not use unless foreign column is indexed
                        raise NotImplementedError()

                    self.primaryjoin = id_col == foreign(foreign_col)

                    logger.info(
                        'implicit one-to-many relationship: %s.%s: %s' % (
                            class_.__name__,
                            self.key,
                            self.primaryjoin,
                        )
                    )

                    # retry mapping the relationship
                    return super(RelationshipWrapper, self).do_init()
            except:
                # swallow and reraise the original exception
                pass

            raise error


def relationship(*args, **kwargs):
    # upgrade collection class
    if kwargs.get('collection_class') is None:
        kwargs['collection_class'] = ResultList

    return RelationshipWrapper(*args, **kwargs)
