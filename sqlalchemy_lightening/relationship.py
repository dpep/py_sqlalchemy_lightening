import logging
import sqlalchemy.orm

from sqlalchemy import event
from sqlalchemy.exc import NoForeignKeysError
from sqlalchemy.orm import foreign, RelationshipProperty
from sqlalchemy.orm.base import instance_dict

from .result_list import ResultList


logger = logging.getLogger(__name__)


def resolve_argument(prop):
    '''resolve a relationship's target argument to a mapped class'''
    arg = prop.argument

    # unwrap a lambda, eg. relationship(lambda: Pet)
    if callable(arg) and not isinstance(arg, type):
        arg = arg()

    # resolve a string name, eg. relationship('Pet')
    if isinstance(arg, str):
        arg = prop.parent.registry._class_registry[arg]

    return arg


def set_join_arg(prop, name, value):
    '''
    Inject a join argument (primaryjoin, secondary, secondaryjoin) into a
    relationship after construction.

    As of SQLAlchemy 2.0, join conditions are resolved from `_init_args`
    during do_init, so assigning eg. `prop.primaryjoin` directly is discarded.
    '''
    getattr(prop._init_args, name).argument = value


class RelationshipWrapper(RelationshipProperty):
    # safe to reuse the superclass cache key; we only customize init-time
    # join construction, not query compilation
    inherit_cache = True

    def do_init(self):
        try:
            # see if it works as is
            return super(RelationshipWrapper, self).do_init()
        except NoForeignKeysError as error:
            # nope, try to construct the relationship

            try:
                # only the extreme base case is supported.  user-provided join
                # config lives in _init_args until configuration completes (the
                # eventual self.primaryjoin etc. don't exist yet at this point).
                init_args = self._init_args
                if (init_args.secondary.argument is not None
                        or init_args.primaryjoin.argument is not None
                        or init_args.secondaryjoin.argument is not None
                        or init_args.foreign_keys.argument is not None
                        or self.uselist is not None):
                    raise NotImplementedError()

                class_ = self.parent.class_
                foreign_class = resolve_argument(self)


                # check for many-to-one relationship
                foreign_key = self.key + '_id'
                if hasattr(class_, foreign_key):
                    foreign_col = getattr(class_, foreign_key)
                    id_col = getattr(foreign_class, 'id')

                    primaryjoin = id_col == foreign(foreign_col)
                    set_join_arg(self, 'primaryjoin', primaryjoin)

                    logger.info(
                        'implicit many-to-one relationship: %s.%s: %s' % (
                            class_.__name__,
                            self.key,
                            primaryjoin,
                        )
                    )

                    # retry mapping the relationship
                    rel = super(RelationshipWrapper, self).do_init()

                    # the relationship and its foreign key are kept in sync in
                    # both directions; this guards against the resulting events
                    # ping-ponging back and forth (which side drives wins)
                    syncing = set()

                    '''
                    When the related object is updated, set the foreign key,
                      eg. Pet.food sets Pet.food_id accordingly.
                    '''
                    @event.listens_for(getattr(class_, self.key), 'set')
                    def on_set(target, value, oldvalue, initiator):
                        if id(target) in syncing:
                            return

                        syncing.add(id(target))
                        try:
                            setattr(target, foreign_key, value.id if value else None)
                        finally:
                            syncing.discard(id(target))


                    '''
                    When the foreign key is updated, resync the related object,
                      eg. Pet.food_id sets Pet.food accordingly.
                    Setting it (rather than just expunging the cache) means it
                    resolves even before the object is flushed, including via
                    the initializer, eg. Pet(food_id=1).food
                    '''
                    @event.listens_for(getattr(class_, foreign_key), 'set')
                    def on_set_foreign(target, value, oldvalue, initiator):
                        if id(target) in syncing:
                            return

                        dict_ = instance_dict(target)
                        foreign_obj = dict_.get(self.key)
                        current_id = foreign_obj.id if foreign_obj is not None else None
                        if current_id == value:
                            # already consistent
                            return

                        syncing.add(id(target))
                        try:
                            setattr(
                                target,
                                self.key,
                                foreign_class.get(value) if value is not None else None,
                            )
                        finally:
                            syncing.discard(id(target))

                    return rel


                # check for one-to-many relationship
                foreign_key = class_.__table__.name + '_id'
                if hasattr(foreign_class, foreign_key):
                    id_col = getattr(class_, 'id')
                    foreign_col = getattr(foreign_class, foreign_key)

                    if not (foreign_col.index or foreign_col.unique):
                        # do not use unless foreign column is indexed
                        raise NotImplementedError()

                    primaryjoin = id_col == foreign(foreign_col)
                    set_join_arg(self, 'primaryjoin', primaryjoin)

                    logger.info(
                        'implicit one-to-many relationship: %s.%s: %s' % (
                            class_.__name__,
                            self.key,
                            primaryjoin,
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


def backref(*args, **kwargs):
    # upgrade collection class
    if kwargs.get('collection_class') is None:
        kwargs['collection_class'] = ResultList

    return sqlalchemy.orm.backref(*args, **kwargs)
