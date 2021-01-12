import serial


# the steps between the degrees
step = 0.15

# the time interval to wait before change next duty cycle for pwm
time_interval = 0.05

# makes servo go to 0 degrees
zero_deg = 2.5

# makes the motor go to 90 degrees
neutral = 7.5

# makes servo go to 180 degrees
full_deg = 12.5

# create frequency
freq = 50

base_servo_pin = 7
side_pin = 11
claw_pin = 13

min_deg = 1
max_deg = 180
max_steps = 180

device = "/dev/ttyACM0"
serial_size = 9600
mambo_addr = ''

ser = serial.Serial(device, baudrate=serial_size)

