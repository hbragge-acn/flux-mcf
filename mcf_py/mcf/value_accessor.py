""""
Copyright (c) 2024 Accenture
"""

from enum import Enum
from typing import Generic, TypeVar, Type, TYPE_CHECKING

from mcf.value import Value

if TYPE_CHECKING:
    from mcf.remote_control import RemoteControl


class ValueAccessorDirection(Enum):
    BOTH = 0
    RECEIVER = 1
    SENDER = 2


# ValueT can be any MCF value type generated by the MCF types_generator package.
ValueT = TypeVar("ValueT", bound=Value)


class RCValueAccessor(Generic[ValueT]):
    """
    Layer on the top of RemoteControl-API-layer that:
     - defines restrictions (e.g. types, but not only) declared by the user.
     - uses values (as opposed to the arrays of arrays + class-names).
    Should be instantiated by the remote_control.create_value_accessor()
    """
    def __init__(self, topic: str, value_type: Type['Value'], remote_control: 'RemoteControl'):
        """
        Constructor
        :param topic:            the topic that values will be written or read to / from.
        :param value_type:       the type of the values on the specified topic.
        :param remote_control:   the remote control which is used for communicating with other components.
        """
        self._topic: str = topic
        self._value_type: Type['Value'] = value_type
        self._rc: 'RemoteControl' = remote_control

    def get(self) -> 'ValueT':
        """
        Gets a value from self._topic from the remote control
        :return     value of type self._value_type
        """
        packed_value = self._rc.read_value(self._topic, withId=True)
        if packed_value is not None:
            value = self._value_type.deserialize(packed_value[1:])  
            value.inject_id(packed_value[0])
        else: 
            value = None
        
        return value

    def set(self, value: 'ValueT', timestamp=None) -> None:
        """
        Write the value to the remote value store
        :param value:       the value to be written
        :param timestamp:   If the remote control event queue has been enabled and the 
                            ReplayEventController is being used, the value will written to the value
                            store at this timestamp. Otherwise, it will be written immediately.
        :param value_id:    The MCF value ID to set
        """
        self._check_type(value)
        serialized = value.serialize()

        # If ext mem, serialised data has extra member
        if len(serialized) > 2:
            return self._rc.write_value(topic=self._topic,
                                        clazz=serialized[1],
                                        value=serialized[0],
                                        extmem=serialized[2],
                                        timestamp=timestamp,
                                        valueId=value.id)
        else:
            return self._rc.write_value(topic=self._topic,
                                        clazz=serialized[1],
                                        value=serialized[0],
                                        timestamp=timestamp,
                                        valueId=value.id)

    def _check_type(self, value: 'ValueT') -> None:
        if not isinstance(value, self._value_type):
            raise TypeError("types are not matching")


class ReceiverAccessor(RCValueAccessor, Generic[ValueT]):
    """
    One directional value accessor which only allows get() functionality.
    """
    def __init__(self, topic: str, value_type: Type['Value'], remote_control: 'RemoteControl'):
        super().__init__(topic, value_type, remote_control)

    def set(self, value: 'ValueT', timestamp=None) -> None:
        raise PermissionError("Receivers cannot call the set() function")


class SenderAccessor(RCValueAccessor, Generic[ValueT]):
    """
    One directional value accessor which only allows set() functionality.
    """
    def __init__(self, topic: str, value_type: Type['Value'], remote_control: 'RemoteControl'):
        super().__init__(topic, value_type, remote_control)

    def get(self) -> None:
        raise PermissionError("Senders cannot call the get() function")
