from bot import RollingBasis, Shapes

bot = RollingBasis()
size = int(input("Taille de la forme : "))
bot.Go_To(Shapes.OrientedPoint(size,0))
bot.Go_To(Shapes.OrientedPoint(size,size))
bot.Go_To(Shapes.OrientedPoint(0,size))
bot.Go_To(Shapes.OrientedPoint(0,0))