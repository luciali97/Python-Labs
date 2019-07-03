"""6.009 Lab 3 -- Six Double-Oh Mines"""

# NO IMPORTS ALLOWED!


class MinesGame:
    """
    Class to represent a game of Mines.
    """

    def __init__(self, num_rows, num_cols, bombs):
        """Start a new game.

        Initializes a new instance of `MinesGame` to have the following
        attributes:
           * `dimensions`
           * `state`
           * `board`
           * `mask`

        Each of these should be as described in the handout.

        Parameters:
           num_rows (int): Number of rows
           num_cols (int): Number of columns
           bombs (list/tuple): List of bombs, given in (row, column) pairs,
                               which can be either tuples or lists 
        """
        
        """
        Bugs:
        1.
        self.board = [[0] * num_cols] * num_rows
        
        [0] * num_cols] returns just a reference to a list of num_cols zeros, but not a list. The subsequent repeating of this element creates a list of num_rows items that all reference to the same list, so all rows in the resulting list are actually the same string
             
        """
        
        def get_neighbors(num_rows, num_cols, row, col):
            """
            Parameters:
               num_rows (int): Number of rows
               num_cols (int): Number of columns
               row (int), col (int): get the surrounding cells of (row,col)
            Return:
               list: surrounding cell coordinates of (row,col), every element in the list is of the form coord = [x][y]
            """
            neighbors = []
            coord1 = [row - 1, col - 1]
            coord2 = [row - 1, col]
            coord3 = [row - 1, col + 1]

            coord4 = [row, col - 1]
            coord5 = [row, col + 1]

            coord6 = [row + 1, col - 1]
            coord7 = [row + 1, col]
            coord8 = [row + 1, col + 1]        
            for coord in [coord1, coord2, coord3, coord4, 
                          coord5, coord6, coord7, coord8]:
                # check if a cell is out of the boundary
                if coord[0]>=0 and coord[0]<num_rows and coord[1]>=0 and coord[1]<num_cols:
                    neighbors.append(coord)
            return neighbors 
        
        def create_board(num_rows, num_cols, bombs):
            """ create the game board
            Parameters:
               num_rows (int): Number of rows
               num_cols (int): Number of columns
               bombs (list/tuple): List of bombs, given in (row, column) pairs,
                               which can be either tuples or lists
            Return:
               board (list of lists): return the game board, where each element is either '.' or an integer between 0 and 8 
            """
            
            board = [[0 for j in range(num_cols)] for i in range(num_rows)]

            # insert bombs to the board
            for row in range(num_rows):
                for col in range(num_cols):
                    if (row,col) in bombs or [row,col] in bombs:
                        board[row][col] = '.'
                        
            # for each non-bomb cell, count the number of bombs around this cell
            for row in range(num_rows):
                for col in range(num_cols):
                    if board[row][col] != '.':
                        num_bombs = 0
                        neighbors = get_neighbors(num_rows,num_cols,row,col)
                        for r,c in neighbors:
                            if board[r][c] == '.':
                                num_bombs += 1                       
                        board[row][col] = num_bombs
            return board
        
        self.board = create_board(num_rows, num_cols, bombs)
        self.dimensions = [num_rows,num_cols]
        self.state = "ongoing"
        self.mask = [[False for j in range(num_cols)] for i in range(num_rows)]
       
    def get_neighbors(self, row, col):
            """Get surrounding cells of (row, col)
            Parameters:
               row (int), col (int): find surrounding cells of (row, col)
            Return:
               list: surrounding cell coordinates of (row,col)
            """
            neighbors = []
            coord1 = [row - 1, col - 1]
            coord2 = [row - 1, col]
            coord3 = [row - 1, col + 1]

            coord4 = [row, col - 1]
            coord5 = [row, col + 1]

            coord6 = [row + 1, col - 1]
            coord7 = [row + 1, col]
            coord8 = [row + 1, col + 1]        
            for coord in [coord1, coord2, coord3, coord4, 
                          coord5, coord6, coord7, coord8]:
                if coord[0]>=0 and coord[0]<self.dimensions[0] and coord[1]>=0 and coord[1]<self.dimensions[1]:
                    neighbors.append(coord)
            return neighbors     

    
    def dump(self):
        """Print a human-readable representation of this game.

        >>> g = MinesGame(1, 2, [(0, 0)])
        >>> g.dump()
        dimensions: [1, 2]
        board: ['.', 1]
        mask:  [False, False]
        state: ongoing
        """
        lines = ["dimensions: {}".format(self.dimensions),
                 "board: {}".format("\n       ".join(map(str, self.board))),
                 "mask:  {}".format("\n       ".join(map(str, self.mask))),
                 "state: {}".format(self.state),
                 ]
        print("\n".join(lines))
    
    def recurse_dig(self, mask, row, col): 
        """Recursively dig cells around a zero cell
        Parameters:
           mask (list of lists): indicates whether the contents of square (row,col) are visible to the player
           rol (int), col (int): where to start digging
        return: 
           int: the number of new squares revealed 
        """
        neighbors = self.get_neighbors(row,col)
        count = 1
        if mask[row][col] == False:
            mask[row][col] = True
            if self.board[row][col] == 0:
                for r,c in neighbors:
                    if self.board[r][c] != '.':
                        count += self.recurse_dig(mask,r,c)
            return count
        return 0


    def dig(self, row, col):
        """
        Recursively dig up (row, col) and neighboring squares.

        Update self.mask to reveal (row, col); then recursively reveal (dig up)
        its neighbors, as long as (row, col) does not contain and is not adjacent
        to a bomb.  Return an integer indicating how many new squares were
        revealed.

        The state of the game should be changed to "defeat" when at least one bomb
        is visible on the board after digging, "victory" when all safe squares
        (squares that do not contain a bomb) and no bombs are visible, and
        "ongoing" otherwise.

        Parameters:
           row (int): Where to start digging (row)
           col (int): Where to start digging (col)

        Returns:
           int: the number of new squares revealed

        >>> game = MinesGame.from_dict({
        ...         "dimensions": [2, 4],
        ...         "board": [[".", 3, 1, 0],
        ...                   [".", ".", 1, 0]],
        ...         "mask": [[False, True, False, False],
        ...                  [False, False, False, False]],
        ...         "state": "ongoing"})
        >>> game.dig(0, 3)
        4
        >>> game.dump()
        dimensions: [2, 4]
        board: ['.', 3, 1, 0]
               ['.', '.', 1, 0]
        mask:  [False, True, True, True]
               [False, False, True, True]
        state: victory

        >>> game = MinesGame.from_dict({
        ...         "dimensions": [2, 4],
        ...         "board": [[".", 3, 1, 0],
        ...                   [".", ".", 1, 0]],
        ...         "mask": [[False, True, False, False],
        ...                  [False, False, False, False]],
        ...         "state": "ongoing"})
        >>> game.dig(0, 0)
        1
        >>> game.dump()
        dimensions: [2, 4]
        board: ['.', 3, 1, 0]
               ['.', '.', 1, 0]
        mask:  [True, True, False, False]
               [False, False, False, False]
        state: defeat
        
        """
        
        """
        Bugs:
        1.
        if state == "defeat" or state == "victory":
            self.state = state
            return 1
        
        Fix: should return 0
        
        2.
        if self.board[row][col] > 0, then we dig all its neighbors
        
        Fix: We should only reveal 1 cell
        
        3. 
        if self.board[row][col] = 0, then we dig all its neighbors
        
        Fix: We need to recursively dig its neighbors
        
        4. 
        if we get the victory state after self.mask[row][col] is set to True, then 
        return 0.
        
        Fix: We should return the correct count
        
        5. 
        if coord[0] < self.height:
        if coord[1] < self.width:
        
        self.height and self.width do not exist
        
        Fix: we should use self.dimensions[0] and self.dimensions[1]
        
        6.
        if cooef[1] >= 0:
        
        Fix: we should use coord[1] instead
        
        7.
        self.mask[coord[0], coord[1]] = True
        
        Fix: self.mask[coord[0]][coord[1]] = True
        """
        
        
        
        if self.state == "defeat" or self.state == "victory":
            return 0
        board = self.board
        
        # reveals a bomb
        if board[row][col] == '.':           
            self.mask[row][col] = True
            self.state = 'defeat'
            return 1
        
        # reveals a nonzero cell
        count = 1
        if board[row][col] != 0:
            self.mask[row][col] = True
        
        # reveals a zero cell
        else:                            
            neighbors = self.get_neighbors(row,col)
            mask = self.mask[:]
            count = self.recurse_dig(mask,row,col)
        
        # if not defeat, then check and update the state of the game
        if self.state != 'defeat':
            self.state = 'victory'
            for r in range(self.dimensions[0]):
                for c in range(self.dimensions[1]):
                    # if there is a cell that is masked but not a bomb, then this game is ongoing
                    if self.board[r][c] != '.' and (not self.mask[r][c]):
                        self.state = 'ongoing'
        return count          
        
    def render(self, xray=False):
        """Prepare a game for display.

        Returns a two-dimensional array (list of lists) of "_" (hidden
        squares), "." (bombs), " " (empty squares), or "1", "2", etc. (squares
        neighboring bombs).  game.mask indicates which squares should be
        visible.  If xray is True (the default is False), the mask is ignored
        and all cells are shown.

        Parameters:
           xray (bool): Whether to reveal all tiles or just the ones allowed by
                        the mask

        Returns:
           A 2D array (list of lists) representing the rendered board

        >>> g = MinesGame.from_dict({
        ...         "dimensions": [2, 4],
        ...         "state": "ongoing",
        ...         "board": [[".", 3, 1, 0],
        ...                   [".", ".", 1, 0]],
        ...         "mask":  [[False, True, True, False],
        ...                   [False, False, True, False]]})
        >>> g.render(False)
        [['_', '3', '1', '_'], ['_', '_', '1', '_']]

        >>> g.render()
        [['_', '3', '1', '_'], ['_', '_', '1', '_']]

        >>> g.render(True)
        [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
        """
        num_rows = self.dimensions[0]
        num_cols = self.dimensions[1]
        config = []
        for r in range(0, num_rows):
            row_r = []
            for c in range(0, num_cols):               
                if (not xray) and (not self.mask[r][c]):         
                    row_r.append('_')
                else:
                    if self.board[r][c] == 0:
                        row_r.append(' ')
                    else:
                        row_r.append(str(self.board[r][c]))
            config.append(row_r)           
        return config        


    def render_ascii(self, xray=False):
        """Render a game as ASCII art.

        Returns a string-based representation of the game.  Each tile of
        the game board should be rendered as in the `render` method.

        Parameters:
           xray (bool): Whether to reveal all tiles or just the ones allowed by
                        the mask

        Returns:
           A string-based representation of game

        >>> g = MinesGame.from_dict({"dimensions": [2, 4],
        ...                     "state": "ongoing",
        ...                     "board": [[".", 3, 1, 0],
        ...                               [".", ".", 1, 0]],
        ...                     "mask":  [[True, True, True, False],
        ...                               [False, False, True, False]]})
        >>> print(g.render_ascii())
        .31_
        __1_
        """
        config = self.render(xray)
        config_str = ''
        for r_list in config:
            for x in r_list:
                config_str += x
            config_str += '\n'
        return config_str[0:len(config_str)-1]


    @classmethod
    def from_dict(cls, d):
        """
        Create an instance of `MinesGame` from a dictionary representation of
        the game.

        Parameters:
          d (dict): a dictionary with keys 'board', 'state', 'mask', and
                    'dimensions'.

        Returns:
          An instance of `MinesGame` with parameters as specified in the
          dictionary.

        Invariant:
          The four dictionary elements ('board', 'state', 'mask', and 'dimensions')
          are assumed to be sufficient and complete in establishing a current state
          of the game. This assumption is used in the test.py testing framework.
        """
        game = cls.__new__(cls)
        for i in ('dimensions', 'board', 'state', 'mask'):
            setattr(game, i, d[i])
        return game


if __name__ == "__main__":
    import doctest
    doctest.testmod() #runs ALL doctests

    # Alternatively, can run the doctests JUST for specified
    # function/methods, e.g., for MinesGame.rendor or any other
    # function you might want.  This may be useful as you write/debug
    # individual doctests or functions.  Also, the verbose flag can be
    # set to True to see all test results, including those that pass.
    #
    #doctest.run_docstring_examples(MinesGame.render, globals(), verbose=False)
