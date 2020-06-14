"""
Docstring
"""
# from adafruit_bus_device.i2c_device import I2CDevice

from hybotics_ht16k33.segments import Seg14x4

# from adafruit_ht16k33.segments import Seg14x4

# from micropython import const


class MultiSeg14x4(Seg14x4):
    """Docstring"""

    _DEFAULT_DISPLAY_BRIGHTNESS = 0.1

    def __init__(
        self,
        i2c,
        address,
        auto_write=False,
        brightness=_DEFAULT_DISPLAY_BRIGHTNESS,
        blink_rate=0,
    ):
        # super().__init__(i2c, address, auto_write, brightness)
        self._address = None
        self._auto_write = auto_write
        self._brightness = brightness
        self._blink_rate = blink_rate
        self.devices = []
        self._nr_disp = 0

        if isinstance(address, int):
            print("DEBUG: (display.py) single display")
            self.devices = Seg14x4(i2c, address, auto_write, brightness)
            self._address = address
        elif isinstance(address, list):
            print("DEBUG: (display.py) multi-display")
            self._address = None

            for index, addr in enumerate(address):
                print(
                    "DEBUG (display.py) display {0} at address = {1}".format(
                        index, hex(addr)
                    )
                )

                self.devices.append(Seg14x4(i2c, addr, auto_write, brightness))
                self.devices[index]._address = addr
                self.devices[index]._brightness = brightness
                self.devices[index]._blink_rate = blink_rate

            self._nr_disp = len(self.devices)
            self._nr_digits = self._nr_disp * 4
            print("DEBUG (display.py) There are {0} displays".format(len(self.devices)))

    def fill(self, color):
        """Fill the whole display with a given color."""
        for _, disp in enumerate(self.devices):
            disp.fill(color)

        if self._auto_write:
            self.show()

    def show(self):
        """Light up all the displays"""
        for _, disp in enumerate(self.devices):
            disp.show()

    def print(self, value, decimal=0):
        """Print the value to the display."""
        if isinstance(value, (str)):
            self._text(value)
        elif isinstance(value, (int, float)):
            self._number(value, decimal)
        else:
            raise ValueError("Unsupported display value type: {}".format(type(value)))
        if self._auto_write:
            self.show()

    def _text(self, text):
        """Display the specified text."""
        for character in text:
            self._push(character)

    def _multitext(self, text):
        """Display the specified text."""
        length = len(text)

        if length > self.nr_digits:
            raise ValueError(
                "Input overflow - '{0}' is too long for the display!".format(text)
            )

        char_nr = 0
        disp_nr = 0
        disp_pos = 0
        shift_pos = 0

        while char_nr < length and disp_nr < self.nr_disp:
            disp_nr = char_nr // 4

            if disp_pos == 3:
                # Must shift everything one character to the left
                disp_nr += 1
                self.devices[disp_nr].print(text[shift_pos])
                shift_pos += 1
                disp_pos = 0
                char_nr += 1
                self.devices[0].print(text[char_nr])

                for d_nr in range(self.nr_disp, -1, -1):
                    self.devices[d_nr].print(text[char_nr - disp_pos - 1])
                    disp_pos += 1
                    shift_pos += 1
                    disp_pos += 1

            self.devices[disp_nr].print(text[char_nr])
            char_nr += 1
            disp_pos += 1

    def _number(self, number, decimal=0):
        """
		Display a floating point or integer number on the Adafruit HT16K33 based displays

		param: number int or float - The floating point or integer number to be displayed, which must be
			in the range 0 (zero) to 9999 for integers and floating point or integer numbers
			and between 0.0 and 999.0 or 99.00 or 9.000 for floating point numbers.
		param: decimal int - The number of decimal places for a floating point number if decimal
			is greater than zero, or the input number is an integer if decimal is zero.

        Returns: The output text string to be displayed.
        """

        auto_write = self._auto_write
        self._auto_write = False
        stnum = str(number)
        dot = stnum.find(".")

        if len(stnum) > self.nr_digits + 1 or (
            (len(stnum) > self.nr_digits) and (dot < 0)
        ):
            raise ValueError(
                "Input overflow - {0} is too long for the display!".format(number)
            )

        if dot < 0:
            # No decimal point (Integer)
            places = len(stnum)
        else:
            places = len(stnum[:dot])

        if places <= 0 < decimal:
            self.fill(False)
            places = 4

            if "." in stnum:
                places += 1

        # Set decimal places, if number of decimal places is specified (decimal > 0)
        if places > 0 < decimal < len(stnum[places:]) and dot > 0:
            txt = stnum[: dot + decimal + 1]
        elif places > 0:
            txt = stnum[:places]

        if len(txt) > self.nr_digits + 1:
            raise ValueError(
                "Input overflow - {0} is too long for the display!".format(txt)
            )

        self._multitext(txt)
        self._auto_write = auto_write

        return txt

    @property
    def blink_rate(self):
        """Return the blink rate."""
        return self._blink_rate

    @blink_rate.setter
    def blink_rate(self, blink_rate):
        """Set the blink rate. Range 0 - 3"""
        self._blink_rate = blink_rate

    @property
    def nr_disp(self):
        """The number of displays"""
        return self._nr_disp

    @property
    def nr_digits(self):
        """The number of displays"""
        return self._nr_digits
