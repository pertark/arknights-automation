from Device import Device
import os
import locate_utils as utils
from image_utils import *
import time
import json
import random

adbkey = r"C:\Users\patri\.android\adbkey"


class Arknights(Bluestacks):
    """
    Arknights controller
    """
    process = 'com.YoStarEN.Arknights'

    # implement methods specific to application

    def __init__(self, adbkey, launch=True, port=5555):
        # connect to bluestacks
        super().__init__(adbkey=adbkey, launch=launch, port=port)

        # launch game
        self.launch(self.process)

    def main(self, verbose=True):
        self.title_screen(verbose=verbose)
        self.start_button(verbose=verbose)
        self.news_screen(verbose=verbose)
        self.collect_daily(verbose=verbose)

    def return_to_main(self, interval=0.5, verbose=False):
        x1, x2, y1, y2 = 37, 62, 40, 49
        while True:
            img = self.screenshot()[self.y*y1//100:self.y*y2//100, self.x*x1//100:self.x*x2//100]
            text = extract_text(img)
            if verbose:
                print(text)
            # TODO: identify something other than this text, maybe the settings gear in top left...
            if "are you sure you want to exit" in text.lower():
                self.back()
                break
            self.back()
            time.sleep(interval)

    def title_screen(self, verbose=False):
        self.wait_for_tesseract('clear cache', verbose=verbose)
        self.bluestacks_tap(50, 50, radius=30)
        self.detect_change_jpeg(threshold=10000, interval=1, verbose=verbose)
        self.wait_for_changes(20000, verbose=verbose)

    def start_button(self, verbose=False):
        self.wait_for_tesseract('start', verbose=verbose)
        img = self.screenshot()
        buttons = simple_box_identification(img, ret_type='image', inverse=True, coords=True, min_area=5000)
        for b in buttons:
            i, coord = b
            x, y, w, h = coord
            if 'start' in extract_text(i).lower():
                self.tap(x+random.randrange(w), y+random.randrange(h))
                # break
        self.wait_for_changes(0, verbose=verbose)
        self.wait_for_changes(100, verbose=verbose)

    def news_screen(self, timeout=40, verbose=False):
        start = time.monotonic()
        if verbose:
            print('Starting news screen search.')
        while True:
            #event_text = extract_text(self.screenshot()[10*self.y//100:20*self.y//100, 30*self.x//100:40*self.x//100])
            event_text = extract_text(self.screenshot())
            if verbose:
                print(event_text)
            if 'event' in event_text.lower() or 'news' in event_text.lower():
                break
            if time.monotonic() - start > timeout:
                if verbose:
                    print('News screen timed out.')
                return False
        self.bluestacks_tap(*self.coords['news-x'])

    def collect_daily(self, verbose=False, timeout=15):
        start = time.monotonic()
        while True:
            y1, y2, x1, x2 = 18, 24, 43, 56
            img = self.screenshot()[self.y*y1//100:self.y*y2//100, self.x*x1//100:self.x*x2//100]
            text = extract_text(img)
            if verbose:
                print(text)
            if 'resource' in text.lower() or 'today' in text.lower():
                self.bluestacks_tap_rect(x1, x2, y1, y2)
                self.wait_for_changes(threshold=100, interval=1, verbose=verbose)
                self.bluestacks_tap(*self.coords['news-x'])
                break
            if time.monotonic() - start > timeout:
                if verbose:
                    print('Daily collection timed out.')
                break
        return

    def farm_stage_until(self, cooldown=30, verbose=True):
        # must be on the stage to work properly
        sanity = self.ocr_bluestacks(87, 0, 96, 10).strip()
        curr_sanity, total_sanity = sanity.split('/')
        cost = self.ocr_bluestacks(92, 93, 96, 98, negative=False, config='--psm 13', debug=True).strip()
        if verbose:
            print(f"Sanity: {curr_sanity} out of {total_sanity}")
            print(f"Stage cost: {cost}")
        try:
            curr_sanity = int(curr_sanity)
            cost = int(cost)
        except ValueError:
            time.sleep(cooldown)
            self.farm_stage_until(cooldown=cooldown, verbose=verbose)
            return

        if curr_sanity < cost:
            if verbose:
                print("Out of sanity, exiting.")
            return

        self.bluestacks_tap_rect(*self.coords['combat']['start'])
        self.wait_for_changes(verbose=verbose)
        self.bluestacks_tap_rect(*self.coords['combat']['mission_start'])
        self.wait_for_changes(interval=30, verbose=verbose)
        # check if autodeploy is on
        #

    def base_smart(self, verbose=True):
        coords = self.coords
        dorm_ops = 0  # number of operators to assign to the dorm

        self.bluestacks_tap(*coords['main_screen']['base'])
        self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
        self.detect_change_jpeg(threshold=0, interval=1, verbose=verbose)
        self.wait_for_changes(threshold=3000, interval=0.4, verbose=verbose)

        # find alerts to collect factory and trading post
        '''
        alerts = simpler_box_identification(
            self.screenshot(),
            negative=True,
            coords=True,
            crop=((self.x*9//10, self.x),(self.y*8//100,self.y*23//100))
        )
        blues = [avg_color(box[0])[2] for box in alerts]
        bx, by, bw, bh = alerts[blues.index(max(blues))][1]  # get coord of blue alert
        self.tap(bx+bw//2+random.randrange(-4, 4), by+bh//2+random.randrange(-4, 4))
        # i feel like the above code works, kinda
        # i lied
        '''
        input('click warning 1')
        self.bluestacks_tap(*coords['base']['warning1'])
        if verbose:
            print('Claiming Factory, Trading Post, Trust.')
        previous_text = ''
        while True:
            y1, y2, x1, x2 = 94, 99, 15, 24
            img = self.screenshot()[self.y*y1//100:self.y*y2//100, self.x*x1//100:self.x*x2//100]
            text = extract_text(img)
            if verbose:
                print(text)
            if 'fatigued' in text.lower():
                break
            if 'stop' in text.lower():
                self.bluestacks_tap(*coords['base']['warning2'])
            if text.lower() != previous_text:
                self.bluestacks_tap_rect(x1, x2, y1, y2)
            previous_text = text
            # continuously clicks on the collections until it reaches fatigued operators
        input('click exit')
        self.bluestacks_tap_rect(*coords['base']['exit_out_alert'])
        time.sleep(random.random()*2+1)
        input('click rr')
        self.bluestacks_tap_rect(*coords['base']['reception_room'])

        while True:
            y1, y2, x1, x2 = 85, 90, 29, 35
            img = self.screenshot()[self.y*y1//100:self.y*y2//100, self.x*x1//100:self.x*x2//100]
            text = extract_text(img)
            if verbose:
                print(text)
            if 'search' in text.lower():
                self.bluestacks_tap_rect(*coords['base']['reception_room_enter'])
                break

        self.wait_for_changes(threshold=4000, verbose=verbose)
        # RECEPTION ROOM
        # get morale of operators
        '''
        y1, y2, x1, x2 = 36, 41, 10, 15
        operator1 = self.ocr_bluestacks(x1, y1, x2, y2, verbose=verbose)
        # unfortunately, above line doesn't work because of background noise in the screencap. 
        if '24' not in operator1:  # when you do clue exchange
            self.bluestacks_tap(50,50,radius=10)
        operator1 = self.ocr_bluestacks(x1, y1, x2, y2, verbose=verbose)
        y1, y2 = 80, 84
        operator2 = self.ocr_bluestacks(x1, y1, x2, y2, verbose=verbose)
        if operator1 == '0/24' or operator2 == '0/24':
            self.bluestacks_tap(10, 35, radius=7)
            self.base_reassign_operators(2)
        '''  # this doesn't work because tesseract doesn't recognize the characters. todo: fix this
        # as an alternative, we'll reassign operators regardless of morale.
        dorm_ops += 2
        self.base_reassign_operators(2)

        self.wait_for_changes(threshold=4000, verbose=verbose)

        self.bluestacks_tap_rect(*self.coords['base']['rr_receive'])
        self.wait_for_changes(threshold=0, verbose=verbose)
        previous_text = ''
        y1, y2, x1, x2 = 31, 34, 70, 75
        while True:
            img = self.screenshot()[self.y*y1//100:self.y*y2//100, self.x*x1//100:self.x*x2//100]
            text = extract_text(img)
            if verbose:
                print(text)
            if 'fatigued' in text.lower():
                break
            if 'stop' in text.lower():
                self.bluestacks_tap(*coords['base']['warning2'])
            if text.lower() != previous_text:
                self.bluestacks_tap_rect(x1, x2, y1, y2)
            previous_text = text
        # TODO: CLAIM DAILY CLUE, CLAIM GIFTED CLUES, GIVE AWAY CLUES, PUT CLUES IN SLOTS, INITIATE CLUE EXCHANGE

        self.back()
        # TODO: REASSIGN OPERATORS USING OVERVIEW MENU
        self.bluestacks_tap_rect(*coords['base']['overview'])

        '''
        # finally, leave.
        if verbose:
            print('Completed base tasks. Returning to main.')
        self.return_to_main(verbose=verbose)
        '''

    def base_reassign_operators(self, num_ops):
        interval = self.coords['base']['operator_assignment']['interval']
        top_row = self.coords['base']['operator_assignment']['top_row']
        bottom_row = self.coords['base']['operator_assignment']['bottom_row']
        width = self.coords['base']['operator_assignment']['width']
        height = self.coords['base']['operator_assignment']['height']
        first_x = self.coords['base']['operator_assignment']['height']
        bottom_rows = num_ops // 2
        top_rows = bottom_rows + num_ops % 2

        # deselect
        for operator in range(top_rows):
            self.bluestacks_tap_rect(
                first_x+operator*interval,
                first_x+operator*interval+width,
                top_row,
                top_row+height
            )

        for operator in range(bottom_rows):
            self.bluestacks_tap_rect(
                first_x+operator*interval,
                first_x+operator*interval+width,
                bottom_row,
                bottom_row+height
            )

        # reselect
        # for now, we just click the leftmost operators, since that's usually how some people do it anyways
        # todo: improve above (not urgent)

        for operator in range(top_rows, top_rows+bottom_rows):
            self.bluestacks_tap_rect(
                first_x+operator*interval,
                first_x+operator*interval+width,
                top_row,
                top_row+height
            )

        for operator in range(bottom_rows, bottom_rows+top_rows):
            self.bluestacks_tap_rect(
                first_x+operator*interval,
                first_x+operator*interval+width,
                bottom_row,
                bottom_row+height
            )

        # confirm
        self.bluestacks_tap_rect(*self.coords['base']['operator_assignment']['confirm'])

    def claim_credit(self, verbose=True):
        # todo: this
        return


def locateOnImage(sub, img, grayscale=True, confidence=0.999):
    return utils._locateAll_opencv(sub, img, grayscale=grayscale, confidence=confidence)


if __name__ == '__main__':
    a = Arknights(adbkey, launch=False, port=5030)
