NOT_YET = -1
STRIKE = -2
IGNORE = -3
SPARE = -4


class Frame:
    """
    Class for storing frame data
    """

    def __init__(self, next_frame):
        """
        Initialization

        :param next_frame: which frame to notify that we need its score
            in case of a strike or spare
        """
        self.__next_frame: Frame = next_frame
        self.reset()

    # noinspection PyAttributeOutsideInit
    def reset(self):
        """
        Resets private variables
        """
        self.__index = 0
        self.__first_buffer: list = []
        self.__second_buffer: list = []
        self.__shots: list = [NOT_YET, NOT_YET]
        if self.__is_last_frame():
            self.__shots.append(NOT_YET)
        self.__score: int = NOT_YET

    def __is_last_frame(self):
        """
        Returns whether this frame is the last one

        :return: True for last frame, False otherwise
        """
        return self.__next_frame is None

    def get_sum(self, previous_sum: str) -> str:
        """
        Returns the sum of the shots collected until now

        :type previous_sum: the collected sum before this frame
        :return: sum of scores (including this one) as a string
        """
        if previous_sum is None or not previous_sum.isnumeric():
            prev_sum: int = 0
        else:
            prev_sum: int = int(previous_sum)
        return "" if self.__score == NOT_YET else str(self.__score + prev_sum)

    def first_shot(self, score: str) -> tuple:
        """
        Saves score of first shot

        :param score: user input of first shot
        :return: tuple of two booleans:
            - whether the given score was valid
            - whether to go to the next frame (
                True before last frame if score is a strike)
        """
        if self.__check_first_score(score):
            return False, False

        if score.upper() == "X":
            self.__save_shot(10)
            self.__save_shot(IGNORE)
            self.__send_frame(True)
            return True, not self.__is_last_frame()
        self.__save_shot(int(score))
        return True, False

    def second_shot(self, score: str) -> tuple:
        """
        Saves score of second shot

        :param score: user input of second shot
        :return: tuple of two booleans:
            - whether the given score was valid
            - whether to go to the next frame (
                True before last frame if score is valid)
        """
        if self.__check_second_score(score):
            return False, False

        if score == "/":
            self.__save_shot(10 - self.__shots[0])
            self.__send_frame(False)
        elif score == "X":
            # only for last frame
            self.__save_shot(10)
        else:
            self.__save_shot(int(score))
        return True, not self.__is_last_frame()

    def third_shot(self, score: str) -> tuple:
        """
        Saves score of third shot

        :param score: user input of third shot
        :return: tuple of two booleans:
            - whether the given score was valid
            - whether to go to the next frame (always False for third shot)
        """
        if self.__check_third_score(score):
            return False, False

        if score.upper() == "X":
            self.__save_shot(10)
        elif score == "/":
            self.__save_shot(10 - self.__shots[1])
        else:
            self.__save_shot(int(score))
        return True, False

    def __check_first_score(self, score: str) -> bool:
        """
        Checks whether the score is valid for first shot
        - first shot can't be spare

        :param score: user input of a shot
        :return: True if an invalid score has been given, False otherwise
        """
        if Frame.__check_score_precheck(score):
            return True

        if self.__index != 0:
            return True

        if score.upper() == "X":
            return False

        if score == "/":
            return True

        return False

    def __check_second_score(self, score: str) -> bool:
        """
        Checks whether the score is valid for second shot
        - second shot can't be a strike, except last frame, and
            it can't be a spare if first shot was a strike
        - second shot can't be a number if it should be spare
        - the first two shots can't be more than ten except last frame with
            a first strike

        :param score: user input of a shot
        :return: True if an invalid character has been given, False otherwise
        """
        if Frame.__check_score_precheck(score):
            return True

        if self.__index != 1:
            return True

        if score.upper() == "X":
            return not self.__is_last_frame()

        if score == "/":
            return self.__shots[0] == 10

        if self.__shots[0] + int(score) > 10:
            if not self.__is_last_frame() or self.__shots[0] != 10:
                return True

        return self.__shots[0] + int(score) == 10

    def __check_third_score(self, score: str) -> bool:
        """
        Checks whether the score is valid for third shot
        - third shot can be done only in last frame
        - third shot can't be a spare if second was a strike
        - third shot can't be a strike if
            - the first two shots are less than 10 (should not happen, there
                shouldn't be a third shot in this case)
            - the first two shots are greater than 10 and the second one wasn't
                a strike (should be 20 with two strikes)
        - third shot can't be a number if it should be spare

        :param score: user input of a shot
        :return: True if an invalid character has been given, False otherwise
        """
        if Frame.__check_score_precheck(score):
            return True

        if self.__index != 2:
            return True

        if not self.__is_last_frame():
            return True

        if score.upper() == "X":
            if self.__shots[0] + self.__shots[1] < 10:
                return True
            if self.__shots[0] + self.__shots[1] > 10:
                return self.__shots[1] != 10
            return False

        if score == "/":
            return self.__shots[1] == 10

        return self.__shots[1] + int(score) == 10

    @staticmethod
    def __check_score_precheck(score: str) -> bool:
        """
        Checks whether the score is valid
        - can't be None
        - must be a one-character number or 'x', 'X', '/'

        :param score: user input of a shot
        :return: True if an invalid score has been given, False otherwise
        """
        if score is None:
            return True
        if len(score) != 1:
            return True
        if score != "/" and score.upper() != "X" and not score.isnumeric():
            return True
        return False

    def __save_shot(self, score: int):
        """
        Saves the score of the current shot

        :param score: the score of the current shot
        """
        if self.__index >= len(self.__shots):
            return
        if self.__shots[self.__index] != NOT_YET:
            return

        if not self.__is_last_frame() or score != IGNORE:
            self.__shots[self.__index] = score
        if score != IGNORE:
            self.__index += 1
            # we need to store NOT_YET for correct printing on GUI
            if self.__score == NOT_YET:
                self.__score = score
            else:
                self.__score += score
            self.__send_score(score)

    def __send_score(self, score: int):
        """
        Sends the score back to previous frame(s) having a strike or a spare.
        This method should be called before __send_frame.

        :param score: the score of the shot to be sent back
        """
        for buffer in [self.__first_buffer, self.__second_buffer]:
            if buffer:
                buffer.pop(0).__receive_score(score)

    def __receive_score(self, score):
        """
        Receives a score from a next frame(s)

        :param score: the score we receive due to a strike or a spare
        """
        self.__score += score

    def __send_frame(self, is_strike):
        """
        Sends this frame to the next one for being able to receive scores
            from it (in case of a strike or a spare).
        If the score was sent to the previous one and there is still one
            element in the first buffer (because of a strike), we have to send
            it, too
        __send_score should be called previously.

        :param is_strike: whether we had a strike
        """
        if self.__is_last_frame():
            return

        self.__next_frame.__receive_frame(self, 2 if is_strike else 1, True)
        if self.__first_buffer:
            self.__next_frame.__receive_frame(self.__first_buffer[0], 1, False)

    def __receive_frame(self, frame, shots: int, is_first: bool):
        """
        Receives the frame (which had a strike or a spare) we should send
            our scores to.
        __first_buffer contains the previous frame that many times we need to
            send (strike 2, spare 1)
        __second_buffer contains the frame before the previous one, it can
            have only one element (there was a strike at that frame)

        :param frame: the frame to send the scores to
        :param shots: how many shots we need to send
        :param is_first: whether we need to store into the first buffer
        """
        buffer = self.__first_buffer if is_first else self.__second_buffer
        for i in range(shots):
            buffer.append(frame)
