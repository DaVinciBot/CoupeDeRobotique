from bot import RollingBasis, Shapes

bot = RollingBasis()
bot.position_offset = Shapes.OrientedPoint(1.0, 0)
print(bot.true_pos(Shapes.OrientedPoint(0, 0)))