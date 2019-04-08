from sqlalchemy.exc import NoForeignKeysError
from sqlalchemy.orm import RelationshipProperty, foreign

from .result_list import ResultList


class RelationshipWrapper(RelationshipProperty):
    def do_init(self):
        try:
            # see if it works as is
            return super(RelationshipWrapper, self).do_init()
        except NoForeignKeysError as error:
            # nope, try to construct the relationship

            try:
                # only the extreme base case is supported
                if self.secondary or self.primaryjoin or self.secondaryjoin or self._user_defined_foreign_keys:
                    raise NotImplementedError()

                foreign_class = self.argument()
                foreign_key = self.parent.mapped_table.name + '_id'

                if hasattr(foreign_class, foreign_key):
                    id_col = getattr(self.parent.class_, 'id')
                    foreign_col = getattr(foreign_class, foreign_key)

                    if not (foreign_col.index or foreign_col.unique):
                        # do not use unless foreign column is indexed
                        raise NotImplementedError()

                    self.primaryjoin = id_col == foreign(foreign_col)

                    self.logger.info(
                        'implicit primaryjoin for relationship: %s.%s: %s' % (
                            self.parent.class_.__name__,
                            self.key,
                            self.primaryjoin,
                        )
                    )

                    # retry mapping the relationship
                    return super(RelationshipWrapper, self).do_init()
            except:
                # skip and reraise the original exception
                pass

            raise error


def relationship(*args, **kwargs):
    # upgrade collection class
    if kwargs.get('collection_class') is None:
        kwargs['collection_class'] = ResultList

    return RelationshipWrapper(*args, **kwargs)
