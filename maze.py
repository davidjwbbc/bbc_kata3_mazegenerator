#!/usr/bin/python3
'''
Maze generator
==============

Generates a maze using a depth-first algorithm

The main class is Maze which uses Maze.Cell objects to store information about
cells in the maze.
'''

import random
import sys

class Maze:
  '''Maze - class to hold a maze of cells
'''

  def __init__(self, max_width, max_height):
    'Constructor - create an empty maze with maximum dimensions'
    self.__max_width = max_width
    self.__max_height = max_height
    self.__cellrows = {'min': [None, None], 'max': [None, None]}

  class Cell:
    '''Class to hold information about an individual cell

This class can also represent an empty Cell which is not part the maze at
present.'''

    def __init__(self, maze, x, y, empty=False):
      '''Constructor - create a new walled cell or empty cell

Creates a Cell at the x,y position in the given maze. If the cell is currently
empty in the maze then the walls are derived from the presence of adjacent
cells in the maze. If this is a new non-empty cell then all walls are present.
'''
      self.__maze = maze
      self.x = x
      self.y = y
      self.__empty = empty
      if empty:
        self.__wall_below = maze.cellExists(x, y+1)
        self.__wall_right = maze.cellExists(x+1, y)
      else:
        self.__wall_below = True
        self.__wall_right = True

    def __str__(self):
      '''Return a string representation of right and bottom walls (left and top
are handled by adjacent cells).'''
      ret = ''
      if self.__wall_below:
        ret += '_'
      else:
        ret += ' '
      if self.__wall_right:
        ret += '|'
      else:
        if self.__wall_below:
          ret += '_'
        else:
          ret += ' '
      return ret

    def __repr__(self):
      '''Return a string representation of this cell for debugging. Mark as
Transient if this cell object was created as a temporary empty maze cell.'''
      return 'Maze.%sCell(x=%i, y=%i, walls="%s")'%({False:'', True: 'Transient'}[self.__empty], self.x, self.y, str(self))

    def hasWallRight(self):
      '''Return True if there is a righthand wall to this cell'''
      return self.__wall_right

    def hasWallBelow(self):
      '''Return True if there is a bottom wall to this cell'''
      return self.__wall_below

    def hasWallLeft(self):
      '''Return True if there is a lefthand wall to this cell'''
      return self.__maze.getcell(self.x-1, self.y).hasWallRight()

    def hasWallAbove(self):
      '''Return True if there is a top wall to this cell'''
      return self.__maze.getcell(self.x, self.y-1).hasWallBelow()

    def breakWallRight(self):
      '''Remove the righthand wall of this cell. Return True if there was a wall to remove.'''
      if not self.__empty and self.__wall_right:
        self.__wall_right = False
        return True
      return False

    def breakWallBelow(self):
      '''Remove the bottom wall of this cell. Return True if there was a wall to remove.'''
      if not self.__empty and self.__wall_below:
        self.__wall_below = False
        return True
      return False

    def breakWallLeft(self):
      '''Remove the lefthand wall of this cell. Return True if there was a wall to remove.'''
      return self.__maze.getcell(self.x-1, self.y).breakWallRight()

    def breakWallAbove(self):
      '''Remove the top wall of this cell. Return True if there was a wall to remove.'''
      return self.__maze.getcell(self.x, self.y-1).breakWallAbove()

  def createCell(self, x, y):
    '''Maze.createCell - Create a cell in the maze if within bounds.

Will create a new cell or return an existing cell if x,y is a valid position
in the maze.

Returns the Maze.Cell at x,y in the Maze or None if x,y is out of bounds.'''
    if x < 0 or x >= self.__max_width:
      return None
    if y < 0 or y >= self.__max_height:
      return None
    if self.__cellrows['min'][1] is None or self.__cellrows['min'][1] > y:
      self.__cellrows['min'][1] = y
    if self.__cellrows['max'][1] is None or self.__cellrows['max'][1] < y:
      self.__cellrows['max'][1] = y
    if self.__cellrows['min'][0] is None or self.__cellrows['min'][0] > x:
      self.__cellrows['min'][0] = x
    if self.__cellrows['max'][0] is None or self.__cellrows['max'][0] < x:
      self.__cellrows['max'][0] = x
    if y not in self.__cellrows:
      ret = Maze.Cell(self, x, y)
      self.__cellrows[y] = {x: ret}
      return ret
    row = self.__cellrows[y]
    if x not in row:
      ret = Maze.Cell(self, x, y)
      row[x] = ret
      return ret
    return row[x]

  def _recursivePopulate(self, cell):
    '''Recursive maze population function'''
    for dir in random.sample([((cell.x-1, cell.y), lambda x: x.breakWallRight()),
                ((cell.x, cell.y-1), lambda x: x.breakWallBelow()),
                ((cell.x+1, cell.y), lambda x: cell.breakWallRight()),
                ((cell.x, cell.y+1), lambda x: cell.breakWallBelow())], 4):
      if not self.cellExists(*dir[0]):
        nc = self.createCell(*dir[0])
        if nc is not None:
          dir[1](nc)
          self._recursivePopulate(nc)

  def populateFrom(self, x, y):
    '''Populate the entire maze using a depth-first algorithm starting at x,y.
'''
    if self.cellExists(x, y):
      return False
    cell = self.createCell(x, y)
    self._recursivePopulate(cell)
    return True

  def cellExists(self, x, y):
    '''Return True if a Maze.Cell exists at position x,y in the Maze.'''
    if y not in self.__cellrows:
      return False
    if x not in self.__cellrows[y]:
      return False
    return True

  def getCell(self, x, y):
    '''Get an existing or empty Maze.Cell for position x,y.'''
    if x < 0 or x >= self.__max_width:
      return Maze.Cell(self, x, y, empty=True)
    if y < 0 or y >= self.__max_height:
      return Maze.Cell(self, x, y, empty=True)
    if y not in self.__cellrows:
      return Maze.Cell(self, x, y, empty=True)
    if x not in self.__cellrows[y]:
      return Maze.Cell(self, x, y, empty=True)
    return self.__cellrows[y][x]

  def __str__(self):
    '''Return a string representation of the Maze.'''
    ret = ''
    # Need to iterate through the range of cells from one to the left of the
    # leftmost defined cell, and for the row above the top row of defined
    # cells in order to get empty cells to fill in the missing top and left
    # walls.
    for row in range(self.__cellrows['min'][1]-1, self.__cellrows['max'][1]+1):
      for col in range(self.__cellrows['min'][0]-1, self.__cellrows['max'][0]+1):
        cell = self.getCell(col,row)
        ret += str(cell)
      ret += '\n'
    return ret

def main():
  '''Main function if running as a standalone program.'''
  max_width = 30
  max_height = 30
  if len(sys.argv) > 1:
    max_width = int(sys.argv[1])
  if len(sys.argv) > 2:
    max_height = int(sys.argv[2])
  m = Maze(max_width, max_height)
  m.populateFrom(random.randint(0, max_width-1),random.randint(0, max_height-1))
  print(str(m))
  return 0

if __name__ == '__main__':
  '''If run as a program, trigger main().'''
  sys.exit(main())
