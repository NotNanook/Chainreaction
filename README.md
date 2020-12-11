# Chainreaction
This is a version of the game Chainreaction, made in Python 3.9

## Features
* 2 Player games (Can be changed)
* Customizable maps
* AI implementation easily possible

## How to use
To start a new game, go to your entry-point and create a new ```Game``` object
```Python
if __name__ ==  "__main__":
    game = Game()
```
After that you have to create a board to play on
```Python
game.initializeGrid(height=9, width=8)
```
For the default experience, let the height be 9 and the width 8.
If you want to switch to a custom board, fill in the parameter ```board``` with the corresponding name
```Python
game.initializeGrid(9, 8, board="circle")
```
The gameloop can be changed and altered, but there is a pre-made one
```Python
play(game)
```
## To do
- [ ] Animations
- [ ] Easier switch to more than 2 players
