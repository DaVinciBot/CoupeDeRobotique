from matplotlib import patches, transforms


class CrateRenderer:
    ZONE_ROTATIONS: dict[int, float] = {
        3: 90,
        4: 90,
        5: 0.0,
        6: 0.0,
        7: 90,
        8: 90,
        9: 0.0,
        10: 0.0,
        11: 90,
        12: 0.0,
        13: 0.0,
        14: 0.0,
        15: 90,
        16: 0.0,
        17: 0.0,
        18: 0.0,
        19: 0.0,
        20: 0.0,
    }

    @classmethod
    def plot(cls, ax, stuff: dict[int, list[dict]]) -> None:
        """Entry point ultra simple."""
        for zone_id, items in stuff.items():
            rotation = cls.ZONE_ROTATIONS.get(zone_id, 0.0)

            for item in items:
                cls._plot_item(ax, item, rotation)

    @classmethod
    def _plot_item(cls, ax, item: dict, rotation: float) -> None:
        """Dispatcher selon type"""
        item_type = item.get("type", "crate")

        if item_type == "crate":
            cls._plot_crate(ax, item, rotation)
        else:
            cls._plot_default(ax, item, rotation)

    @classmethod
    def _plot_crate(cls, ax, item: dict, rotation: float) -> None:
        x, y = item["x"], item["y"]
        color = item["color"]

        width, height = 5.0, 15.0
        cx, cy = x - width / 2, y - height / 2

        t = transforms.Affine2D().rotate_deg_around(x, y, rotation) + ax.transData

        ax.add_patch(
            patches.Rectangle(
                (cx, cy),
                width,
                height,
                linewidth=0.5,
                edgecolor="#333333",
                facecolor=color,
                alpha=0.85,
                zorder=3,
                transform=t,
            ),
        )

        qr_size = width * 0.7
        qr_x = x - qr_size / 2
        qr_y = y - qr_size / 2

        ax.add_patch(
            patches.Rectangle(
                (qr_x, qr_y),
                qr_size,
                qr_size,
                linewidth=0,
                facecolor="white",
                zorder=4,
                transform=t,
            ),
        )

        cell = qr_size / 3
        pattern = [(0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2)]

        for col, row in pattern:
            ax.add_patch(
                patches.Rectangle(
                    (qr_x + col * cell, qr_y + row * cell),
                    cell,
                    cell,
                    linewidth=0,
                    facecolor="black",
                    zorder=5,
                    transform=t,
                ),
            )

    @classmethod
    def _plot_default(cls, ax, item: dict, rotation: float) -> None:
        x, y = item["x"], item["y"]

        t = transforms.Affine2D().rotate_deg_around(x, y, rotation) + ax.transData

        ax.plot(x, y, "o", transform=t)
