"""6.009 Lab 4 -- HyperMines"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

class HyperMinesGame:   

    def get_item(self, coord, array):
        """
        Get the item in array at coord.
        
        Args:
            coord (list): [x_0,...,x_k]
            array (list): (k+1)-dimensional list
        
        Return:
            array[x_0][x_1]...[x_k]
        
        >>> game = HyperMinesGame([3,3,2],[[1,2,0]])
        >>> game.get_item([2, 2, 0], game.board)
        1
        
        """
        if len(coord) == 1:
            return array[coord[0]]
        return self.get_item(coord[1:], array[coord[0]])
    
    def set_item(self, coord, array, new_val):
        """
        Set the item at index coord in array with new_val
        
        Args:
            coord (list): [x_0,...,x_k], coordinate for the item that we want to set
            array (list): we want to set array[x_0]...[x_k] with new_val
            new_val (boolean or int): the new value for that item
        
        Return:
            array (list): the item at coord is new_val and everything else is same as the input array
            
        >>> game = HyperMinesGame([3,3,2],[[1,2,0]])
        >>> game.set_item([2, 2, 0], game.board,9)
        [[[0, 0], [1, 1], [1, 1]], [[0, 0], [1, 1], ['.', 1]], [[0, 0], [1, 1], [9, 1]]]
        """        
        def recurse_set(sub_coord, sub_array, new_val):
            """
            Helper function to find and set the item recursively
            """
            if len(sub_coord) == 1:
                sub_array[sub_coord[0]] = new_val
            else:
                recurse_set(sub_coord[1:],sub_array[sub_coord[0]],new_val)
        recurse_set(coord, array, new_val) 
        return array
    
    def get_neighbors(self, coord, dimensions):  
        """
        Return the neighbor coordinates of coord, including itself
        
        Args:
            coord (list): find the neighbors of coord
            dims (list): dimensions of the board
        
        Return:
            (list): a list of coordinates adjacent to coord, including coord itself
        
        >>> game = HyperMinesGame([3,3,2],[[1,2,0]])
        >>> game.get_neighbors([2, 2, 0], game.dimensions)
        [[1, 1, 0], [2, 1, 0], [1, 2, 0], [2, 2, 0], [1, 1, 1], [2, 1, 1], [1, 2, 1], [2, 2, 1]]
        """
        if len(coord) == 0:
            return [[]]
        
        new_nghb = []
        x_i = coord[0]
        d_i = dimensions[0]
        offset = [-1,0,1]   
        for prev_coord in self.get_neighbors(coord[1:], dimensions[1:]):
            for delta in offset:
                y_i = x_i + delta
                # check boundaries
                if y_i >= 0 and y_i < d_i:             
                    new_nghb.append([y_i]+prev_coord)
        return new_nghb
    
    def get_all_coord(self, dimensions):
        """
        Return the list of all coordinates with given dimensions
        
        Args:
            dimensions (list): dimensions of the board
            
        Return:
            (list): list of all coordinates in the board
        
        >>> game = HyperMinesGame([2,3],[[1,2]])
        >>> game.get_all_coord([2,3])
        [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2], [1, 2]]
        
        """
        if len(dimensions) == 0:
            return [[]]
        d_i = dimensions[0]
        new_coord = []
        for prev_coord in self.get_all_coord(dimensions[1:]):
            for i in range(d_i):
                new_coord.append([i]+prev_coord)
        return new_coord
    
    def init_N_dim_array(self, dimensions, init_val):
        """
        Initialize an N-dimensional empty array with value init_val.

        Args:
            dimensions (list): [d_0,...,d_k], k = N-1, specifies the dimensions of the array
            init_val (boolean or int): the initial value in this N-dim array

        Return:
            array (list): N-dimensional array with init_val
            
        >>> game = HyperMinesGame([3,3,2],[[1,2,0]])
        >>> game.init_N_dim_array(game.dimensions,0)
        [[[0, 0], [0, 0], [0, 0]], [[0, 0], [0, 0], [0, 0]], [[0, 0], [0, 0], [0, 0]]]
        """
        if len(dimensions) == 0:
            return init_val
        return [self.init_N_dim_array(dimensions[1:],init_val) for j in range(dimensions[0])]

    def create_board(self, dims, bombs):
        """ Create the game board
            
        Args:
            dims (list): dimensions of the board
            bombs (list): Bomb locations as a list of lists, each is an N-dimensional coordinate
        Return:
            board (list): a board where each cell is either '.' or the number of surrounding bombs
            
        >>> game = HyperMinesGame([3,3,2],[[1,2,0]])
        >>> game.dump()
        dimensions: [3, 3, 2]
        board: [[0, 0], [1, 1], [1, 1]]
               [[0, 0], [1, 1], ['.', 1]]
               [[0, 0], [1, 1], [1, 1]]
        mask:  [[False, False], [False, False], [False, False]]
               [[False, False], [False, False], [False, False]]
               [[False, False], [False, False], [False, False]]
        state: ongoing
        """            
        board = self.init_N_dim_array(dims, 0)
            
        # insert bombs
        for bomb_coord in bombs:
            board = self.set_item(bomb_coord, board, '.')
                
        # increment each non-bomb cell surrounding a bomb
        for bomb_coord in bombs:
            bomb_nghb = self.get_neighbors(bomb_coord,dims)
            for nghb_coord in bomb_nghb:
                nghb_val = self.get_item(nghb_coord,board)
                if nghb_val != '.':
                    board = self.set_item(nghb_coord, board, nghb_val+1)
        return board            
    
    def __init__(self, dims, bombs):
        """Start a new game.

        This method should properly initialize the "board", "mask",
        "dimensions", and "state" attributes.

        Args:
           dims (list): Dimensions of the board
           bombs (list): Bomb locations as a list of lists, each an
                         N-dimensional coordinate

        >>> g = HyperMinesGame([2, 4, 2], [[0, 0, 1], [1, 0, 0], [1, 1, 1]])
        >>> g.dump()
        dimensions: [2, 4, 2]
        board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
               [['.', 3], [3, '.'], [1, 1], [0, 0]]
        mask:  [[False, False], [False, False], [False, False], [False, False]]
               [[False, False], [False, False], [False, False], [False, False]]
        state: ongoing
        """
                
        board = self.create_board(dims, bombs)
        self.board = board
        self.dimensions = dims
        self.mask = self.init_N_dim_array(dims, False)
        self.state = "ongoing"
                
    def dump(self):
        """Print a human-readable representation of this game."""
        lines = ["dimensions: %s" % (self.dimensions, ),
                 "board: %s" % ("\n       ".join(map(str, self.board)), ),
                 "mask:  %s" % ("\n       ".join(map(str, self.mask)), ),
                 "state: %s" % (self.state, )]
        print("\n".join(lines))
        
    def dig(self, coords):
        """Recursively dig up square at coords and neighboring squares.

        Update the mask to reveal square at coords; then recursively reveal its
        neighbors, as long as coords does not contain and is not adjacent to a
        bomb.  Return a number indicating how many squares were revealed.  No
        action should be taken and 0 returned if the incoming state of the game
        is not "ongoing".

        The updated state is "defeat" when at least one bomb is visible on the
        board after digging, "victory" when all safe squares (squares that do
        not contain a bomb) and no bombs are visible, and "ongoing" otherwise.

        Args:
           coords (list): Where to start digging

        Returns:
           int: number of squares revealed

        >>> g = HyperMinesGame.from_dict({"dimensions": [2, 4, 2],
        ...         "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
        ...                   [['.', 3], [3, '.'], [1, 1], [0, 0]]],
        ...         "mask": [[[False, False], [False, True], [False, False], [False, False]],
        ...                  [[False, False], [False, False], [False, False], [False, False]]],
        ...         "state": "ongoing"})
        >>> g.dig([0, 3, 0])
        8
        >>> g.dump()
        dimensions: [2, 4, 2]
        board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
               [['.', 3], [3, '.'], [1, 1], [0, 0]]
        mask:  [[False, False], [False, True], [True, True], [True, True]]
               [[False, False], [False, False], [True, True], [True, True]]
        state: ongoing
        >>> g = HyperMinesGame.from_dict({"dimensions": [2, 4, 2],
        ...         "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
        ...                   [['.', 3], [3, '.'], [1, 1], [0, 0]]],
        ...         "mask": [[[False, False], [False, True], [False, False], [False, False]],
        ...                  [[False, False], [False, False], [False, False], [False, False]]],
        ...         "state": "ongoing"})
        >>> g.dig([0, 0, 1])
        1
        >>> g.dump()
        dimensions: [2, 4, 2]
        board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
               [['.', 3], [3, '.'], [1, 1], [0, 0]]
        mask:  [[False, True], [False, True], [False, False], [False, False]]
               [[False, False], [False, False], [False, False], [False, False]]
        state: defeat
        """
        
        def recurse_dig(coords, mask): 
            """Recursively dig cells around a zero cell
            Parameters:
               mask (list of lists): indicates whether the contents of square (row,col) are visible to the player
               coords (int): where to start digging
            return: 
               int: the number of new squares revealed 
            """
            neighbors = self.get_neighbors(coords, self.dimensions)
            count = 1
            if self.get_item(coords,mask) == False:
                mask = self.set_item(coords,mask, True)
                if self.get_item(coords,self.board) == 0:
                    for nghb_coord in neighbors:
                        if self.get_item(nghb_coord,self.board) != '.':
                            count += recurse_dig(nghb_coord,mask)
                return count
            return 0
        
        # if this dig is trivial
        if self.state == "defeat" or self.state == "victory" or self.get_item(coords, self.mask):
            return 0
        
        board = self.board
        
        # reveals a bomb
        if self.get_item(coords, board) == '.':           
            self.mask = self.set_item(coords, self.mask, True)
            self.state = 'defeat'
            return 1
        
        # reveals a nonzero cell
        count = 1
        mask = self.mask[:]
        if self.get_item(coords, board) != 0:
            self.mask = self.set_item(coords, mask, True)
        
        # reveals a zero cell
        else:                            
            neighbors = self.get_neighbors(coords, self.dimensions)            
            count = recurse_dig(coords,mask)
        
        # if not defeat, then check and update the state of the game
        if self.state != 'defeat':
            self.state = 'victory'
            iterate = self.get_all_coord(self.dimensions)
            for c in iterate:
                    # if there is a cell that is masked but not a bomb, then this game is ongoing
                if self.get_item(c, board) != '.' and (not self.get_item(c, mask)):
                    self.state = 'ongoing'
        return count          

    def render(self, xray=False):
        """Prepare the game for display.

        Returns an N-dimensional array (nested lists) of "_" (hidden squares),
        "." (bombs), " " (empty squares), or "1", "2", etc. (squares
        neighboring bombs).  The mask indicates which squares should be
        visible.  If xray is True (the default is False), the mask is ignored
        and all cells are shown.

        Args:
           xray (bool): Whether to reveal all tiles or just the ones allowed by
                        the mask

        Returns:
           An n-dimensional array (nested lists)

        >>> g = HyperMinesGame.from_dict({"dimensions": [2, 4, 2],
        ...            "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
        ...                      [['.', 3], [3, '.'], [1, 1], [0, 0]]],
        ...            "mask": [[[False, False], [False, True], [True, True], [True, True]],
        ...                     [[False, False], [False, False], [True, True], [True, True]]],
        ...            "state": "ongoing"})
        >>> g.render(False)
        [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
         [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

        >>> g.render(True)
        [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
         [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
        """
        render_board = self.init_N_dim_array(self.dimensions,0)
        dims = self.dimensions
        coords = self.get_all_coord(dims)
        for coord in coords:
            val = self.get_item(coord, self.board)
            if (not xray) and (not self.get_item(coord, self.mask)):
                new_val = '_'                
            else:
                if val == 0:
                    new_val = ' '
                else:
                    new_val = str(val)
            render_board = self.set_item(coord, render_board, new_val)    
        return render_board

    @classmethod
    def from_dict(cls, d):
        """Create a new instance of the class with attributes initialized to
        match those in the given dictionary."""
        game = cls.__new__(cls)
        for i in ('dimensions', 'board', 'state', 'mask'):
            setattr(game, i, d[i])
        return game

if __name__ == '__main__':   
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
