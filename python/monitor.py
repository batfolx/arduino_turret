from constants import *
from threading import Thread
import cv2
import json

width_threshold = 35
height_threshold = 35
travel_time_x = 7
travel_time_y = 2
multiplier = 0.035


def receive_data():
    """
    Called on a separate thread to receive data from the Arduino
    :return: None
    """

    while True:
        try:
            bytes_to_read = ser.readline()
            print(bytes_to_read)
            data = json.loads(bytes_to_read.decode('utf-8'))
            distance = data['distance']
            print(f'distance: {distance}')
        except Exception as e:
            print(f'Error in reading bytes from the \'duino: {e}')


def send_data(servo: str, degrees: float, subtract: bool, fire: bool):
    """
    Sends JSON data over serialization to the Arduino
    :param servo: The servo to turn
    :param degrees: the degrees to turn
    :param subtract: Whether to subtract degrees or not
    :param fire: Whether or not to fire the blaster. Pew pew!
    :return: None
    """
    data = json.dumps({
        'servo': servo,
        'degrees': degrees,
        'subtract': subtract,
        'fire': fire
    })
    ser.write(bytes(data.strip('\n').encode('utf-8') + '\0'.encode('utf-8')))


def monitor():
    """
    Function that gets image from the camera
    and then processes it, main function to combine functionality
    :return: None
    """

    # TODO start two threads to swivel. Need them to listen to a variable
    # TODO in order to 'lock on', so to speak

    # get data to read full body's (and maybe faces later)
    body_data = 'haarcascades/haarcascade_upperbody.xml'
    face_data = 'haarcascades/haarcascade_frontalface_alt.xml'

    # train the classifier
    classifier = cv2.CascadeClassifier(face_data)

    # get the video device
    video = cv2.VideoCapture(0)
    """
        init_board()
    # create two PWM (pulse width modulation) objects
    base_pwm = GPIO.PWM(base_servo_pin, freq)
    side_pwm = GPIO.PWM(side_pin, freq)

    # start servos in the middle for neutral (90 degrees)
    base_pwm.start(neutral)
    side_pwm.start(neutral)

    right_deg = 0
    left_deg = 0    
    """

    fire = 0

    ret, frame = video.read()
    if not ret:
        print('Wait like 2 seconds to start this up again lol')
        return

    # get the height & width of the frame
    height, width = get_image_size(frame)

    # get the middle of the frame / image. this is not very correct mathematics
    # because the middle of a rect should be its (width / 2, height / 2)
    # but since opencv handles coordinate systems a little different we have
    # to tweak the numbers
    middle_height, middle_width = height // 4, int((width // 1.15))

    # y increases when you go DOWN, x increases when you go LEFT
    # get the thresholds between the bounds that we need to keep the
    # camera in so it can fire the nerf bullet correctly
    upper_height_thresh = middle_height + height_threshold
    lower_height_thresh = middle_height - height_threshold

    upper_width_thresh = middle_width + width_threshold
    lower_width_thresh = middle_width - width_threshold

    while True:

        # read in the frame
        ret, frame = video.read()

        # if frame could not be read, continue through the loop
        if not ret:
            print("Could not capture image; continuing")
            continue

        # flip the frame probably change this
        frame = cv2.flip(frame, 1)

        # convert to gray
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # draw circle in middle of screen
        cv2.circle(frame, (middle_width, middle_height), 7, (255, 0, 0), -1)

        # look for a human in the shot and get a rectangle
        rectangles = classifier.detectMultiScale(frame, scaleFactor=1.2, minNeighbors=3)

        # display a rectangle around the face
        # this is where we want to shoot the gun and center the
        for (x, y, w, h) in rectangles:

            middle_x = x + w/2
            middle_y = y + h/2

            # print(f'height: {height} width: {width} and center: {(width/2, height/2)}')
            # print(f'this is y: {y}, uppery: {upper_height_thresh}, lowery: {lower_height_thresh}')
            # here we need to check for the bounds of the person being in the center or not
            if lower_width_thresh < middle_x < upper_width_thresh:
                print('X IS IN MIDDLE')
                fire += 1

            elif middle_x < lower_width_thresh:
                # the rectangle is left of the screen; we need to calculate exactly how many pixels, and translate
                # to degrees
                print(f"X IS TOO LEFT, MOVE [X] LEFT TO MATCH. Amount to move {lower_width_thresh - middle_x}")
                send_data('base', (lower_width_thresh - middle_x) * multiplier, True, False)
                fire = 0
            elif middle_x > upper_width_thresh:
                print(f'X IS TOO RIGHT, MOVE [X] RIGHT TO MATCH. Amount to move {middle_x - upper_width_thresh}')
                send_data('base', (middle_x - upper_width_thresh) * multiplier, False, False)
                fire = 0

            # if y is in between bounds, this is good. Keep it here and shoot!
            if lower_height_thresh < middle_y < upper_height_thresh:
                # print("Y IS IN MIDDLE")
                fire += 1

            elif middle_y < upper_height_thresh:
                # print("TOO FAR UP, MOVE [Y] UP TO MATCH")
                send_data('side', travel_time_y, True, False)
                # (lower_height_thresh - middle_y) * multiplier
                fire = 0

            elif middle_y > lower_height_thresh:
                # print("TOO FAR DOWN, MOVE [Y] DOWN TO MATCH")
                send_data('side', travel_time_y, False, False)
                # (middle_y - lower_height_thresh) * multiplier
                fire = 0

            if fire >= 30:
                print("Target acquired, firing.")
                send_data('lol', 0, False, True)
                fire = 0

            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 1)



        # show the shot to the screen
        cv2.imshow('frame', frame)


        if cv2.waitKey(1) & ord('q') == 0xFF:
            break

    video.release()
    cv2.destroyAllWindows()


def get_image_size(frame) -> tuple:
    """
    Gets the image size for a specific frame
    :param frame: The frame to get the size for
    :return: a tuple of (height, width)
    """
    return tuple(frame.shape[1::-1])



if __name__ == '__main__':
    receive_data_t = Thread(target=receive_data, daemon=False)
    #receive_data_t.start()
    monitor()
