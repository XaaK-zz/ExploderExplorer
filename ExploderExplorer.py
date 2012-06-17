import Game

def main():
    newGame = Game.Game(640,480,"levels.xml")
    newGame.initGame()
    newGame.gameLoop()

#call the "main" function if running this script
if __name__ == '__main__': main()