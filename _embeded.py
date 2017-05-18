from pyfirmata import Arduino, util
from pyfirmata import INPUT, OUTPUT, PWM, SERVO
board = Arduino('/dev/ttyS0') #firmataCommunicate
board.digital[3].mode = PWM #forward Pin
board.digital[5].mode = PWM #revers Pin
board.digital[12].mode = SERVO #servo Pin
board.digital[12].write(100) # defult Degree