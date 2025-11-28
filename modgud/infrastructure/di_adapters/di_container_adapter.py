"""Adapter implementing DIContainerPort using EnergyInverter."""

from typing import Type, TypeVar

from modgud.infrastructure import EnergyInverter

T = TypeVar('T')


class DIContainerAdapter:
  """Adapter that implements DIContainerPort using EnergyInverter."""

  def __init__(self, energy_inverter: EnergyInverter) -> None:
    """Initialize with an EnergyInverter instance.

    :param energy_inverter: The EnergyInverter instance to wrap
    """
    self._inverter = energy_inverter

  def resolve(self, interface_type: Type[T], name: str = 'default') -> T:
    """Resolve a dependency by interface type.

    :param interface_type: The interface/protocol type to resolve
    :param name: Named instance identifier
    :return: The resolved implementation instance
    :raises KeyError: If no implementation is registered
    """
    try:
      return self._inverter.resolve(interface_type, name)
    except Exception as e:
      # Convert to KeyError as per port contract
      raise KeyError(f'No implementation registered for {interface_type}: {str(e)}') from e

  def register(self, interface_type: Type[T], implementation: T, name: str = 'default') -> None:
    """Register an implementation for an interface.

    :param interface_type: The interface/protocol type
    :param implementation: The implementation instance
    :param name: Named instance identifier
    """
    # EnergyInverter expects a type, not an instance
    # If we get an instance, register its type
    if not isinstance(implementation, type):
      implementation_type = type(implementation)
    else:
      implementation_type = implementation

    self._inverter.register(interface_type, implementation_type, name)

  def has_registration(self, interface_type: Type[T], name: str = 'default') -> bool:
    """Check if an implementation is registered.

    :param interface_type: The interface/protocol type
    :param name: Named instance identifier
    :return: True if registered, False otherwise
    """
    return self._inverter.is_registered(interface_type, name)

  def clear_registrations(self) -> None:
    """Clear all registered implementations."""
    # EnergyInverter doesn't have a clear method, so we need to
    # reinitialize it (which clears the internal container)
    self._inverter._initialize()
