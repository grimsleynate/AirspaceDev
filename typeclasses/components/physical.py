"""Physical-envelope and container-storage components."""

from evennia.contrib.base_systems.components import Component, DBField


def normalized_dimensions(value):
    """Return three positive dimensions in centimeters, or ``None``."""

    if not isinstance(value, (list, tuple)) or len(value) != 3:
        return None
    try:
        dimensions = tuple(float(dimension) for dimension in value)
    except (TypeError, ValueError):
        return None
    return dimensions if all(dimension > 0 for dimension in dimensions) else None


def dimensions_fit(item_dimensions, container_dimensions):
    """Check rectangular envelopes while allowing the item to be rotated."""

    item = normalized_dimensions(item_dimensions)
    container = normalized_dimensions(container_dimensions)
    if not item or not container:
        return True
    return all(
        item_side <= container_side
        for item_side, container_side in zip(sorted(item), sorted(container))
    )


class PhysicalDimensions(Component):
    """The measured exterior envelope of a physical game object."""

    name = "physical_dimensions"
    dimensions_cm = DBField(default=None)

    def set_dimensions(self, value):
        dimensions = normalized_dimensions(value)
        if not dimensions:
            raise ValueError("Physical dimensions must be three positive centimeter values.")
        self.dimensions_cm = dimensions

    def fits_inside(self, interior_dimensions):
        return dimensions_fit(self.dimensions_cm, interior_dimensions)


class ContainerStorage(Component):
    """Usable interior envelope and discrete-item capacity of a container."""

    name = "container_storage"
    interior_dimensions_cm = DBField(default=None)
    max_items = DBField(default=20)

    def set_interior_dimensions(self, value):
        dimensions = normalized_dimensions(value)
        if not dimensions:
            raise ValueError("Interior dimensions must be three positive centimeter values.")
        self.interior_dimensions_cm = dimensions

    def set_max_items(self, value):
        value = int(value)
        if value < 0:
            raise ValueError("Container item capacity cannot be negative.")
        self.max_items = value

    def accepts_dimensions(self, item_dimensions):
        return dimensions_fit(item_dimensions, self.interior_dimensions_cm)
