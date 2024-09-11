from pypika.functions import DistinctOptionFunction
from pypika import Field, MySQLQuery, Order, Criterion

QUOTE_CHAR = MySQLQuery._builder().QUOTE_CHAR


class GroupConcat(DistinctOptionFunction):
    def __init__(
        self, field: Field, order_field: Field, order=Order.asc, sep=",", alias=None
    ):
        super().__init__("GROUP_CONCAT", field, alias=alias)
        self.field = field.get_sql(with_alias=False, quote_char=QUOTE_CHAR)
        self.order_field = order_field.get_sql(with_alias=False, quote_char=QUOTE_CHAR)
        self.order = order
        self.separator = self.wrap_constant(sep)

    def get_special_params_sql(self, **kwargs):
        return (
            f"ORDER BY {self.order_field} {self.order.value} SEPARATOR {self.separator}"
        )
