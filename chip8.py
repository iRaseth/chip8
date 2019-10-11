from random import seed, randint
import pygame
import time

class game_window():
    def __init__(self, scale_factor):
        self.height = 32
        self.width = 64
        self.pixel_colors = {
            0: pygame.Color(0, 0, 0, 255),
            1: pygame.Color(250,250,250,255)
        }
        self.scale_factor = scale_factor
        pygame.display.init()
        pygame.display.set_caption("Chip 8")
        self.surface = pygame.display.set_mode(
                            (self.width * self.scale_factor,
                            self.height * self.scale_factor),
                            pygame.HWSURFACE | pygame.DOUBLEBUF, 8)


    def draw_pixel(self, x_cord, y_cord, pixel_state):
        x_position = x_cord * self.scale_factor
        y_position = y_cord * self.scale_factor
        pygame.draw.rect(self.surface, self.pixel_colors.get(int(pixel_state)),
                (x_position, y_position, self.scale_factor, self.scale_factor))

    def get_pixel_state(self, x_cord, y_cord):
        x_position = x_cord * self.scale_factor
        y_position = y_cord * self.scale_factor
        pixel_state = self.surface.get_at((x_position, y_position))
        if pixel_state == self.pixel_colors.get(0):
            return 0
        else:
            return 1

    def clear_screen(self):
        self.surface.fill(self.pixel_colors[0])

    def update(self):
        pygame.display.flip()

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width

    KEY_MAPPING = {
        0x0: pygame.K_g,
        0x1: pygame.K_4,
        0x2: pygame.K_5,
        0x3: pygame.K_6,
        0x4: pygame.K_7,
        0x5: pygame.K_r,
        0x6: pygame.K_t,
        0x7: pygame.K_y,
        0x8: pygame.K_u,
        0x9: pygame.K_f,
        0xA: pygame.K_h,
        0xB: pygame.K_j,
        0xC: pygame.K_v,
        0xD: pygame.K_b,
        0xE: pygame.K_n,
        0xF: pygame.K_m,
    }

class chip8():

    def __init__(self, screen):
        """ Initializing the physical configuration """
        self.memory = [0]*4096
        self.display = [0] * 64 * 32
        self.screen = screen
        self.draw_flag = False
        self.keyboard = [0] * 16
        self.ip = 0x200
        self.current_opcode = 0
        self.index_register = 0
        self.stack_pointer = 0
        self.stack = [0]*16
        self.V = [0]*16
        self.I = 0
        self.fonts = 	 [0xF0, 0x90, 0x90, 0x90, 0xF0,
                          0x20, 0x60, 0x20, 0x20, 0x70,
                          0xF0, 0x10, 0xF0, 0x80, 0xF0,
                          0xF0, 0x10, 0xF0, 0x10, 0xF0,
                          0x90, 0x90, 0xF0, 0x10, 0x10,
                          0xF0, 0x80, 0xF0, 0x10, 0xF0,
                          0xF0, 0x80, 0xF0, 0x90, 0xF0,
                          0xF0, 0x10, 0x20, 0x40, 0x40,
                          0xF0, 0x90, 0xF0, 0x90, 0xF0,
                          0xF0, 0x90, 0xF0, 0x10, 0xF0,
                          0xF0, 0x90, 0xF0, 0x90, 0x90,
                          0xE0, 0x90, 0xE0, 0x90, 0xE0,
                          0xF0, 0x80, 0x80, 0x80, 0xF0,
                          0xE0, 0x90, 0x90, 0x90, 0xE0,
                          0xF0, 0x80, 0xF0, 0x80, 0xF0,
                          0xF0, 0x80, 0xF0, 0x80, 0x80]
        self.delay_timer = 0
        self.sound_timer = 0
        """ For random byte generator """
        seed(1)

        for x in range(len(self.fonts)):
            self.memory[x] = self.fonts[x]

    def load_ROM(self, rom_path):
            print(f'Loading {rom_path}...')
            with open(rom_path, 'rb') as ROM:
                buffer_size = ROM.read()
                for x in range(len(buffer_size)):
                    self.memory[x + 0x200] = buffer_size[x]

    def process_opcode(self, opcode):

        nnn = opcode & 0x0FFF
        n = opcode & 0x000F
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        kk = opcode & 0x00FF


        """
            Clear the display
            0x00E0
        """
        if opcode == 0x00E0:
            self.display = [0] * 64 * 32
            self.screen.clear_screen()

        """
            Return from a subroutine
            0x00EE
        """
        if opcode == 0x00EE:
            self.ip = self.stack[self.stack_pointer]
            self.stack_pointer -= 1


        """
            Jump to location at nnn
            1nnn
        """
        if opcode & 0xF000 == 0x1000:
            self.ip = nnn
            print(f'LOOP ! {self.ip}')

        """
            Call subroutine at nnn.
            2nnn
        """
        if opcode & 0xF000 == 0x2000:
            self.stack_pointer += 1
            self.stack[self.stack_pointer] = self.ip
            self.ip = nnn


        """
            Skip next instruction if Vx == kk
            3xkk
        """
        if opcode & 0xF000 == 0x3000:
            print(f'self.V[x] = {self.V[x]}, kk = {kk}')
            if self.V[x] == kk:
                self.ip += 2


        """
            Skip next instruction if Vx != kk
            4xkk
        """
        if opcode & 0xF000 == 0x4000:
            if self.V[x] != kk:
                self.ip += 2


        """
            Skip next instruction if Vx == Vy
            5xy0
        """
        if opcode & 0xF000 == 0x5000:
            if self.V[x] == self.V[y]:
                self.ip += 2


        """
            Set Vx = kk
            6xkk
        """
        if opcode & 0xF000 == 0x6000:
            self.V[x] = kk


        """
            Set Vx = Vx + kk.
            7xkk
        """
        if opcode & 0xF000 == 0x7000:
            self.V[x] = self.V[x] + kk


        """
            Set Vx = Vy.
            8xy0
        """
        if opcode & 0xF00F == 0x8000:
            self.V[x] = self.V[y]


        """
            Set Vx = Vx OR Vy.
            8xy1
        """
        if opcode & 0xF00F == 0x8001:
            self.V[x] = self.V[x] | self.V[y]


        """
            Set Vx = Vx AND Vy.
            8xy2
        """
        if opcode & 0xF00F == 0x8002:
            self.V[x] = self.V[x] & self.V[y]


        """
            Set Vx = Vx XOR Vy.
            8xy3
        """
        if opcode & 0xF00F == 0x8003:
            self.V[x] = self.V[x] ^ self.V[y]


        """
            Set Vx = Vx + Vy, set VF = carry.
            8xy4
        """
        if opcode & 0xF00F == 0x8004:
            temp = self.V[x] + self.V[y]
            if temp > 255:
                self.V[0xF] = 1
            else:
                self.V[0xF] = 0
            self.V[x] = temp & 0x00FF


        """
            Set Vx = Vx - Vy, set VF = NOT borrow.
            8xy5
        """
        if opcode & 0xF00F == 0x8005:
            if self.V[x] > self.V[y]:
                self.V[0xF] = 1
            else:
                self.V[0xF] = 0
            self.V[x] = self.V[x] - self.V[y]


        """
            Set Vx = Vx SHR 1.
            8xy6
        """
        if opcode & 0xF00F == 0x8006:
            if (self.V[x] % 2) == 1:
                self.V[0xF] = 1
            else:
                self.V[0xF] = 0
            self.V[x] = self.V[x] >> 1


        """
            Set Vx = Vy - Vx, set VF = NOT borrow.
            8xy7
        """
        if opcode & 0xF00F == 0x8007:
            if self.V[y] > self.V[x]:
                self.V[0xF] = 1
            else:
                self.V[0xF] = 0
            self.V[x] = self.V[y] - self.V[x]


        """
            Set Vx = Vx SHL 1.
            8xyE
        """
        if opcode & 0xF00F == 0x800E:
            self.V[0xF] = self.V[x] >> 7
            self.V[x] = self.V[x] << 1


        """
            Skip next instruction if Vx != Vy.
            9xy0
        """
        if opcode & 0xF000 == 0x9000:
            if self.V[x] != self.V[y]:
                self.ip += 2


        """
            Set I = nnn.
            Annn
        """
        if opcode & 0xF000 == 0xA000:
            self.I = nnn


        """
            Jump to location nnn + V0.
            Bnnn
        """
        if opcode & 0xF000 == 0xB000:
            self.ip = nnn + self.V[0]


        """
            Set Vx = random byte AND kk.
            Cxkk
        """
        if opcode & 0xF000 == 0xC000:
            random_byte = randint(0,255) & kk
            self.V[x] = random_byte

        """
            Display n-byte sprite starting at memory location
            I at (Vx, Vy), set VF = collision.
            Dxyn
        """
        if opcode & 0xF000 == 0xD000:

            location_x = self.V[x]
            location_y = self.V[y]
            memory_location = self.I
            self.V[0xF] = 0

            for byte in range(n):

                binary_byte = bin(self.memory[memory_location + byte])[2:].zfill(8)
                actual_y_coordinate = location_y + byte
                if actual_y_coordinate > self.screen.get_height():
                    actual_y_coordinate = actual_y_coordinate % self.screen.get_height()

                for bit in range(8):

                    actual_x_coordinate = location_x + bit
                    if actual_x_coordinate > self.screen.get_width():
                        actual_x_coordinate = actual_x_coordinate % self.screen.get_width()

                    display_pixel_cords = actual_y_coordinate * 64 + actual_x_coordinate
                    pixel = self.display[display_pixel_cords]

                    if int(bit) == 1 and pixel == 1:
                        self.display[display_pixel_cords] = 0
                        self.V[0xF] = 1
                    elif int(bit) == 1 and pixel == 0 :
                        self.display[display_pixel_cords] = 1
                    elif int(bit) == 0 and pixel == 1  :
                        self.display[display_pixel_cords] = 1
                    elif int(bit) == 0 and pixel == 0 :
                        self.display[display_pixel_cords] = 0

                    self.screen.draw_pixel(actual_x_coordinate, actual_y_coordinate, self.display[display_pixel_cords])

            self.screen.update()


        """
            Skip next instruction if key with the value of Vx is pressed.
            Ex9E
        """
        if opcode & 0xF0FF == 0xE09E:
            if self.keyboard[self.V[x]] == 1:
                self.ip = self.ip + 2


        """
            Skip next instruction if key with the value of Vx is not pressed.
            ExA1
        """
        if opcode & 0xF0FF == 0xE0A1:
            if self.keyboard[self.V[x]] == 0:
                self.ip = self.ip + 2


        """
            Set Vx = delay timer value.
            Fx07
        """
        if opcode & 0xF0FF == 0xF007:
            self.V[x] = self.delay_timer


        """
            Wait for a key press, store the value of the key in Vx.
            Fx0A
        """
        if opcode & 0xF0FF == 0xF00A:
            self.V[x] = self.delay_timer
            #############TODO###################

        """
            Set delay timer = Vx.
            Fx15
        """
        if opcode & 0xF0FF == 0xF015:
            self.delay_timer = self.V[x]


        """
            Set sound timer = Vx.
            Fx18
        """
        if opcode & 0xF0FF == 0xF018:
            self.sound_timer = self.V[x]


        """
            Set I = I + Vx.
            Fx1E
        """
        if opcode & 0xF0FF == 0xF01E:
            self.I = self.I + self.V[x]


        """
            Set I = location of sprite for digit Vx.
            Fx29
        """
        if opcode & 0xF0FF == 0xF029:
            self.I = self.V[x] * 5


        """
            Store BCD representation of Vx in memory locations I, I+1, and I+2.
            Fx33
        """
        if opcode & 0xF0FF == 0xF033:
            decimal_representation = self.V[x]
            self.memory[self.I] = int(str(decimal_representation)[0])
            self.memory[self.I + 1] = int(str(decimal_representation)[1])
            self.memory[self.I + 2] = int(str(decimal_representation)[2])


        """
            Store registers V0 through Vx in memory starting at location I.
            Fx55
        """
        if opcode & 0xF0FF == 0xF055:
            for register in range(x):
                self.memory[self.I + register] = self.V[register]


        """
            Read registers V0 through Vx from memory starting at location I.
            Fx65
        """
        if opcode & 0xF0FF == 0xF065:
            for register in range(x):
                self.V[register] = self.memory[self.I + register]




    def cycle(self):

        current_opcode = self.memory[self.ip] << 8 | self.memory[self.ip + 1]

        self.process_opcode(current_opcode)
        print(hex(current_opcode))

        self.ip = self.ip + 2

        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
            if self.sound_timer == 0:
                printf("sound")

        self.draw_flag = True









game = game_window(16)
chip = chip8(game)
chip.load_ROM('maze.ch8')
while True:
    chip.cycle()
    time.sleep(0.01)
# game = game_window(16)
# run = True
# while run:
#     pygame.time.delay(100)
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             run = False
# pygame.quit()
