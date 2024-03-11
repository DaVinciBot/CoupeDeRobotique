from geometry import OrientedPoint


def closest_zone(
    zone_bool,
    actual_position: OrientedPoint,
    our=True,
    exclude_not_basic=True,
    color="blue",
    basic=False,
):  # zone must math the format [zone,bool]
    if our:
        if color == "blue":
            s = 0
        else:
            s = 1
        zones = [zone_bool[i] for i in range(s, len(zone_bool), 2)]
    else:
        zones = zone_bool
    if exclude_not_basic:
        return sorted(
            zones,
            key=lambda x: (x[1] != basic, x[0].center.get_distance(actual_position)),
        )  # False before True
    return sorted(zones, key=lambda x: (x[0].center.get_distance(actual_position)))
