# Chainreaction
This is a version of the game Chainreaction, made in Python 3.9

## Features
* 2 Player games (Can be changed)
* Customizable maps

## How to use
To start a new game, go to your entry-point and create a new ```Game``` object
```Python
if __name__ ==  "__main__":
    game = Game()
```
For the default experience, set first parameter ```normal```
If you want to switch to a custom board, switch to ```tree``` or a custom board size
```Python
game.initializeGrid("normal")
```
The gameloop can be changed and altered, but there is a pre-made one
```Python
play(game)
```
## To do
- [ ] Animations
- [ ] Easier switch to more than 2 players
