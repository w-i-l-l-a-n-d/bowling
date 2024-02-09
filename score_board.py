from tkinter import Tk, DISABLED, NORMAL, ttk

from frame import Frame

FRAME_NUMBER = 10


class ScoreBoard:
    """
    Class for storing board GUI and score information
    """

    def __init__(self):
        """
        Initialization of the board
        """
        self.__root: Tk = Tk()
        self.__frame: ttk.Frame = ttk.Frame(self.__root, padding=10)
        self.__frame.grid()

        self.__frames: list = []
        self.__create_frames()

        self.__entries = []
        self.__sum_list: list = []
        self.__create_board()

        ttk.Button(self.__frame, text="Reset", command=self.__reset).grid(
            column=0, row=5)
        self.__root.mainloop()

    def __create_frames(self):
        """
        Creates frames for bowling
        """
        next_frame = None
        for i in range(FRAME_NUMBER):
            current_frame = Frame(next_frame)
            self.__frames.append(current_frame)
            next_frame = current_frame
        self.__frames.reverse()

    def __create_board(self):
        """
        Creates score board for GUI
        """
        for i in range(FRAME_NUMBER):
            label = ttk.Label(self.__frame, text=str(i + 1))
            label.grid(column=i, row=0)
            for j in [0, 1]:
                entry = self.__create_entry(i, j)
                entry.grid(column=i, row=j + 1)
                entry.config(state=DISABLED)
                self.__entries.append(entry)
            label = ttk.Label(self.__frame, text="")
            label.grid(column=i, row=4)
            self.__sum_list.append(label)
        self.__reset()

    def __create_entry(self, column: int, row: int) -> ttk.Entry:
        """
        Creates an entry widget with binding key-press and using callback

        :param column: which column the entry in
        :param row: which row the entry in
        :return: the created entry widget
        """
        entry = ttk.Entry(self.__frame)
        entry.bind('<KeyPress>',
                   lambda event: self.__handle_input(str(event.char).upper(),
                                                     entry, column, row))
        return entry

    def __reset(self):
        """
        Resets all the frames
        """
        for frame in self.__frames:
            frame.reset()
        for i in range(FRAME_NUMBER):
            for j in [0, 1]:
                index = i * 2 + j
                self.__entries[index].delete(-1)
                self.__entries[index].config(state=DISABLED)
        self.__entries[0].focus_set()
        self.__entries[0].config(state=NORMAL)
        # remove extra entry for third shot in last frame
        if len(self.__entries) == FRAME_NUMBER * 2 + 1:
            self.__entries.pop().destroy()
        self.refresh_gui()

    def refresh_gui(self):
        """
        Refreshes GUI on input or on resetting
        """
        prev_sum = "0"
        for i in range(FRAME_NUMBER):
            current_sum = self.__frames[i].get_sum(prev_sum)
            self.__sum_list[i].config(text=current_sum)
            prev_sum = current_sum

    def __handle_input(self, user_input: str, entry: ttk.Entry, column: int,
                       row: int):
        """
        Handles user input:
        - sends user input to frame object to validate and/or save
        - clears input field (maybe it contains wrong text)
        - refreshes GUI for correct score labels
        - goes on to the next field or frame
        - creates extra entry for third shot in the last frame if necessary

        :param user_input: user input in upper case
        :param column: in which column (frame) we are now
        :param row: which shot we are doing now
        """
        if row == 0:
            is_valid, go_next = self.__frames[column].first_shot(user_input)
        elif row == 1:
            is_valid, go_next = self.__frames[column].second_shot(user_input)
        else:
            is_valid, go_next = self.__frames[column].third_shot(user_input)

        entry.delete(-1)
        if not is_valid:
            return

        index = column * 2 + row
        self.refresh_gui()

        if go_next:
            self.__entries[index + 2 - row].focus_set()
            self.__entries[index + 2 - row].config(state=NORMAL)
        else:
            if self.__check_for_extra_entry(column, row, user_input):
                new_entry = self.__create_entry(9, 2)
                new_entry.grid(column=9, row=3)
                self.__entries.append(new_entry)

            if row < 2:
                self.__entries[index + 1].focus_set()
                self.__entries[index + 1].config(state=NORMAL)

    def __check_for_extra_entry(self, column: int, row: int,
                                user_input: str) -> bool:
        """
        Checks whether an extra entry can be created for third shot in last
            frame.

        :param column: column of current frame
        :param row: row of current shot
        :param user_input: user input in upper case
        :return: True if the circumstances are good for creating the entry
        """
        if column != 9:
            return False
        if len(self.__entries) != 20:
            return False
        if row == 0 and user_input == "X":
            return True
        if row == 1 and user_input == "/":
            return True
        return False
