#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Visual Processing Speed Task

Settings Json controls the task parameters
Lang_prompt Json controls the displayed text prompts

@author: beisenre@umn.edu
        Kebert@umn.edu
'''
import pathlib
import os
import pygame
import csv
import json
import random
from glob import glob
from datetime import date, datetime

#path variables
src = pathlib.Path(__file__).parents[0].resolve().as_posix()
image_path =  f"{src}/images/"
data_path = f"{src}/logs/"

# Quick color defs
White = (255,255,255)

pygame.init()
Font = pygame.font.SysFont('Verdana',40)
screen = pygame.display.set_mode((1920,1080), pygame.FULLSCREEN | pygame.RESIZABLE)
info = pygame.display.Info()
clock = pygame.time.Clock()

class ImageDisplay:
    def __init__(self,image, position, img_id):
        self.rect= pygame.Rect(position)
        self.position=position
        self.img_id= img_id
        self.image= pygame.image.load(image).convert()
        
    def render(self, screen):
        screen.blit(
            pygame.transform.scale(
                self.image,(self.position[2],self.position[3])), self.rect)
                
class CircleStim:
    def __init__(self, color, center, radius, img_id):
        self.color = color
        self.center = center
        self.radius = radius
        self.img_id = img_id
        
    def render(self, screen):
        pygame.draw.circle(screen, self.color, self.center, self.radius)
        
class TextDisplay:
    def __init__(self,text, x,y,w,h, Font, color, buffer):
        self.pos = x,y
        self.txtspace = w,h
        self.font= Font
        self.font_color= color
        self.text= text
        self.buffer = buffer
        
    def render(self, screen):
        words = [word.split(' ') for word in self.text.splitlines()]  # 2D array where each row is a list of words.
        space = self.font.size(' ')[0]  # The width of a space.
        max_width, max_height = self.txtspace
        max_width = max_width-(self.buffer/2)
        x, y = self.pos
        for line in words:
            word_list=[]
            word_widths=[]
            for word in line:
                word_surface = self.font.render(word, 0, self.font_color)
                word_list.append(word_surface)
                word_width, word_height = word_surface.get_size()
                word_widths.append(word_width+space)
                
            x_start= x - sum(word_widths)/2
            if x_start <= self.buffer:
                x_start = self.buffer
                
            x = x_start
            for idx, w in enumerate(word_list):
                if x + word_widths[idx] >= max_width:
                    x = self.pos[0] - (sum(word_widths[idx-1:-1])/2)# Reset the x.
                    if x <= self.buffer:
                        x= self.buffer
                    y += w.get_height()  # Start on new row.
                screen.blit(w, (x,y))
                x += w.get_width() + space

            x = self.pos[0]  # Reset the x.
            y += w.get_height()  # Start on new row.

class InputBox:
    def __init__(self, x, y, w, h, Font, text=''):
        self.rect = pygame.Rect(x,y,w,h)
        self.color = (0,0,0)
        self.text = text
        self.Font= Font
        self.text_surface = self.Font.render(text, True, self.color)
        self.active = False

    def update(self):
            # Resize the box if the text is too long.
            width = max(200, self.text_surface.get_width()+10)
            self.rect.w = width
            

    def draw(self, screen):
        screen.blit(self.text_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect,2)
        
class ErrorButton:
    def __init__(self, color, x,y,w,h, callback, text):
        self.rect = pygame.Rect(x,y,w,h)
        self.posx = x
        self.posy = y
        self.callback = callback
        self.color = color
        self.active = True
        self.font = pygame.font.SysFont('verdana', 20)
        self.text = text
        
    def render(self, screen):
        msg= self.font.render(self.text, True, (0,0,0))
        pygame.draw.rect(screen,self.color, self.rect, 0, 20)
        screen.blit(msg, (self.posx+40, self.posy+20))

    def on_touch(self, event):
        if event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback(self.btn_id)       

class start_screen:
    def __init__(self,screen, info, Font):
        self.run_lang = False
        self.Font = Font
        self.width = info.current_w
        self.height = info.current_h
        self.Title_disp = TextDisplay('Welcome to the Visual Processing Speed task!', 
                                      self.width*.5, self.height*.1, self.width, self.height*.4,
                                      Font, (0,0,0), 100)
        
        self.subject_entry = InputBox(self.width*.1, self.height*.5,
                                     400,80, 
                                     self.Font,
                                     "Enter Participant Number")
        
        self.session_entry = InputBox(self.width*.1, self.height*.7,
                                     400,80, 
                                     self.Font,
                                     "Enter Session number and press return")
        self.error_msg = ErrorButton((200,200,200), self.width*.5, self.height*.5, 400, 100, 
                                     self.error_msg_click, 'Default MSG')
            
        self.subject_info = ''
        self.session_info = ''
        self.default_sbj = 'Enter Participant Number'
        self.default_sess = 'Enter Session number and press return'
        self.err_msg = False
        self.screen = screen
        
    def parse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            if self.subject_entry.rect.collidepoint(event.pos):
                self.subject_entry.text = ''
                # Toggle the active variable.
                self.subject_entry.active = not self.subject_entry.active
            else:
                self.subject_entry.active = False
                
            if self.session_entry.rect.collidepoint(event.pos):
                self.session_entry.text = ''
                # Toggle the active variable.
                self.session_entry.active = not self.session_entry.active
            else:
                self.session_entry.active = False
            if self.error_msg.rect.collidepoint(event.pos):
                self.error_msg_click()
                
        if event.type == pygame.KEYDOWN:
            if self.subject_entry.active:
                if event.key == pygame.K_RETURN:
                    self.start_click()
                elif event.key == pygame.K_BACKSPACE:
                    self.subject_entry.text = self.subject_entry.text[:-1]
                else:
                    self.subject_entry.text += event.unicode
            
            if self.session_entry.active:
                if event.key == pygame.K_RETURN:
                    self.start_click()
                elif event.key == pygame.K_BACKSPACE:
                    self.session_entry.text = self.session_entry.text[:-1]
                else:
                    self.session_entry.text += event.unicode
                # Re-render the text.
        self.subject_entry.text_surface = self.subject_entry.Font.render(self.subject_entry.text, True, self.subject_entry.color)
        self.session_entry.text_surface = self.session_entry.Font.render(self.session_entry.text, True, self.session_entry.color)        
        

    def start_click(self):
        '''grab sucject info and start experiment'''
        self.get_text_input()
        if self.err_msg:
            pass
        else:
            self.run_lang = True
            
    def error_msg_click(self):
        self.err_msg = False
        self.screen.fill((255,255,255))
        pygame.display.flip()
        
    def get_text_input(self):
        self.subject_info = self.subject_entry.text
        self.session_info = self.session_entry.text
        self.Title_disp.render(self.screen)
        if self.subject_info == self.default_sbj or self.subject_info in [' ', '', '  ']:
            #display error prompt
            self.error_msg.text = 'Please enter a subject Number'
            self.error_msg.render(self.screen)
            self.err_msg = True

        elif self.session_info == self.default_sess or self.session_info in [' ', '', '  ']:
            #display error prompt
            self.error_msg.text = 'Please enter a session number'
            self.error_msg.render(self.screen)
            self.err_msg = True
        else:
            self.err_msg = False
    
    def update(self):
        self.subject_entry.draw(self.screen)
        self.session_entry.draw(self.screen)
        self.Title_disp.render(self.screen)
        if self.err_msg:
            self.error_msg.render(self.screen)
        pygame.display.flip()  
        
class lang_screen:
    def __init__(self,screen, info, Font):
        self.run_practice = False
        self.Font = Font
        self.width = info.current_w
        self.height = info.current_h
        self.lang_prompt = TextDisplay('Select your preferred language: \n\n1 = English, \n2 = Español, \n3 = Tiếng Việt', 
                                       self.width*.5, self.height*.3, self.width, self.height, Font, (0,0,0), 100)
        self.screen = screen
        self.lang = None
        
        self.lang_prompt.render(self.screen)
        
    def parse_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.lang = 'english_prompts.json'
                self.lang_select()
            elif event.key == pygame.K_2:
                self.lang = 'espanol_prompts.json'
                self.lang_select()
            elif event.key == pygame.K_3:
                self.lang = 'tiengviet_prompts.json'
                self.lang_select()
            else:
                ''' forces selection of language'''
                pass
    def update(self):
        self.lang_prompt.render(self.screen)
    def lang_select(self):
        self.run_practice = True

class experiment:
    def __init__(self, screen, info, sbj, session, out_path, settings, prompts):
        #general display settings
        self.screen = screen
        self.width = info.current_w
        self.height = info.current_h
        self.red_dot = f"{image_path}RedDotBig.bmp"
        self.blue_dot = f"{image_path}BlueDotBig.bmp"
        self.smile = f"{image_path}smiley1.bmp"
        self.fix = f"{image_path}fix.bmp"
        self.x = f"{image_path}x.bmp"
        self.out_path = out_path
        self.is_running= True
        self.practice = True
        self.can_respond = True
                
        # Experimenter flags, user can change these with settings file
        #uses set layout in order below
        self.num_practice = settings[0]
        self.num_red_prac = settings[1]
        self.num_trials = settings[2]
        self.num_rtrial = settings[3]
        self.iti = settings[4]
        self.stim_dur = settings[5]
        self.rep_red, self.rep_blue = settings[6] #sets response keys [red, blue]
        # Set the random presentation orders
        sequence= (self.rep_red + ' ')* self.num_red_prac + (self.rep_blue+' ')*(self.num_practice-self.num_red_prac)
        sequence= sequence.split(' ')[0:-1]
        self.practice_order = random.sample(sequence, k = self.num_practice)
        sequence= (self.rep_red + ' ')* self.num_rtrial + (self.rep_blue+' ')*(self.num_trials-self.num_rtrial)
        sequence= sequence.split(' ')[0:-1]
        self.trial_order = random.sample(sequence, k = self.num_trials)
        
        
        self.practice_text = prompts[0]
        self.correct_text = prompts[1]
        self.incorrect_text = prompts[2]
        self.trial_text = prompts[3]
        self.exit_text = prompts[4]
        
        
        #trial data
        d = date.today()
        self.today = d.strftime("%y-%m-%d")
        self.hour = datetime.now().strftime("%H:%M:%S")
        self.subject = sbj
        self.session = session
        self.response = []
        self.stimuli = []
        self.correct = []
        self.trial_num = []

        #set image displays
        self.red_stim = CircleStim('red', (self.width*.5, self.height*.5), 250, 'red')
        self.blue_stim = CircleStim('blue', (self.width*.5, self.height*.5), 250, 'blue')
        self.correct_fb = ImageDisplay(self.smile, [self.width*.3, self.height*.2, self.width*.4, self.height*.52], 'blue') #fix stim
        self.incorrect_fb = ImageDisplay(self.x,[0, 0, self.width, self.height], 'blue')
        self.fixation = ImageDisplay(self.fix, [0, 0, self.width,self.height], 'fix')
        self.dp = True
    
        #exp variables
        self.clock = pygame.time
        self.current_trial = 0
        self.update_trial_state()
        self.event_dict= {self.rep_red: self.key_press,
                          self.rep_blue: self.key_press,
                          ' ': self.key_press,
                          'r': self.key_press,
                          '\x1b' : self.force_quit}

    def force_quit(self, key_id):
        self.is_running = False
        
    def event_handler(self, event):
         if event.type == pygame.KEYDOWN:
             try:
                 '''pass key press to the dictionary of functions'''
                 self.event_dict[chr(event.key)](chr(event.key))
             except:
                '''if pressed key is not in the event dictionary do nothing'''
                pass
         else:
             pass
                
    def update_trial_state(self):
        if self.practice:
            if self.current_trial == 0:
                self.display_prompt('instruction')
                self.flag='f'
                self.stims=self.practice_order
            else:
                if self.current_trial > self.num_practice:
                    self.practice = False
                    self.current_trial = 0
                    self.display_prompt('trial_text')
                    self.flag='f'
                    self.dp = True
                else:
                    self.timer_run('practice')
        else:
            '''Exp trial flow '''
            if self.current_trial == 0:
                self.display_prompt('trial_text')
                self.flag='f'
                self.stims=self.trial_order
            else:
                if self.current_trial > self.num_trials:
                    self.display_prompt('ending')
                    
                else:
                    '''load/reload screen'''
                    self.timer_run('exp')

    def display_prompt(self, flag):
        if flag == 'instruction':
            self.text_prompts = TextDisplay(self.practice_text, self.width*.5, self.height*.1, self.width, 800, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
            pygame.display.flip()
        elif flag == 'correct':
            self.text_prompts = TextDisplay(self.correct_text, self.width*.5, self.height*.7, self.width, self.height, Font, (0,0,0), 100)
            self.correct_fb.render(self.screen)
            self.text_prompts.render(self.screen)
        elif flag == 'incorrect':
            self.text_prompts = TextDisplay(self.incorrect_text, self.width*.5, self.height*.7, self.width, self.height, Font, (0,0,0),100)
            self.incorrect_fb.render(self.screen)
            self.text_prompts.render(self.screen)
        elif flag == 'trial_text':
            self.text_prompts = TextDisplay(self.trial_text, self.width*.5, self.height*.1, self.width, 800, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'ending':
            self.text_prompts = TextDisplay(self.exit_text, self.width*.5, self.height*.3, self.width, self.height, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
            
        pygame.display.flip()
    
    def timer_run(self, flag):
        '''Handles timing of sequences '''
        t= self.clock.get_ticks()
        if flag == 'practice':
            if t < (self.trial_start+ 100):        
                self.display_stim_sequence('fix')
            elif t <(self.trial_start+self.fix_time +self.iti):
                self.display_stim_sequence('iti')
            elif t <(self.trial_start+self.fix_time+self.iti+self.stim_dur):
                self.display_stim_sequence('stim')
            else:
                pass
        if flag == 'exp':
            if t < (self.trial_start+ 100):        
                self.display_stim_sequence('fix')
            elif t <(self.trial_start+self.fix_time +self.iti):
                self.display_stim_sequence('iti')
            elif t <(self.trial_start+self.fix_time+self.iti+self.stim_dur):
                self.display_stim_sequence('stim')
            
    def display_stim_sequence(self, flag):
        self.flag= flag
        if flag == 'fix':
            self.can_respond = False
            self.fixation.render(self.screen)
            pygame.display.flip()

        elif flag == 'iti':
            pass

        elif flag == 'stim':
            self.can_respond = True
            if self.stims[self.current_trial-1] == self.rep_red:
                self.red_stim.render(self.screen)
            else:
                self.blue_stim.render(self.screen)
            pygame.display.flip()
            self.stim_onset= self.clock.get_ticks()
                
    def key_press(self, key_id: str):
        rep=self.clock.get_ticks()
        if self.can_respond:
            if  key_id == ' ':
                if self.current_trial > self.num_trials:
                    self.is_running = False
                elif self.flag=='f':
                    self.screen.fill((255,255,255))
                    self.dp = False
                    pygame.display.flip()
                    self.current_trial +=1
                    self.flag='1'
                    self.fix_time = random.randrange(1000,3000,500) #generate random time to delay between 1-3 s by .25 steps
                    self.trial_start= self.clock.get_ticks()
                    self.update_trial_state()
                
            elif key_id == 'r':
                if self.current_trial == 0:
                    self.screen.fill((255,255,255))
                    pygame.display.flip()
                    self.current_trial= 0
                    self.practice = True
                    self.fix_time = random.randrange(1000,3000,500) #generate random time to delay between 1-3 s by .25 steps
                    self.trial_start= self.clock.get_ticks()
                    self.update_trial_state()
                
            elif key_id == self.rep_red or key_id ==self.rep_blue:
                if self.flag == 'stim':
                    self.screen.fill((255,255,255))
                    pygame.display.flip()
                    self.response = key_id
                    if self.practice:
                        self.log_data(rep)
                        if key_id == self.practice_order[self.current_trial-1]:
                            self.display_prompt('correct')
                        else:
                            self.display_prompt('incorrect')
                        self.dp = True
                        self.flag='f'
                    else:
                        self.correct = self.response == self.trial_order[self.current_trial-1]
                        self.log_data(rep)
                        self.current_trial +=1
                        self.fix_time = random.randrange(1000,3000,500) #generate random time to delay between 1-3 s by .25 steps
                        self.trial_start= self.clock.get_ticks()
                        self.update_trial_state()
                    
    def log_data(self,rep):
        if self.practice:
            tt = 'Practice'
        else:
            tt = self.current_trial
            
        file = open(f'{self.out_path}VP_{self.today}_{self.subject}_{self.session}.csv', 'a', newline ='')
        with file:
            header = ['Subject', 'Session', 'Date', 'Time', 'Trial', 'Stimulus', 'Response', 'Correct', 'RT', 'Red_Key']
            writer = csv.DictWriter(file, fieldnames = header)
            
            # writing data row-wise into the csv file
            if self.current_trial ==1 and self.practice:
                writer.writeheader()
            writer.writerow({'Subject' : self.subject,
                             'Date' : self.today,
                             'Time' : self.hour,
                             'Session' : self.session,
                            'Trial' : tt,
                            'Stimulus' : self.trial_order[self.current_trial-1],
                            'Response' : self.response,
                            'Correct': self.correct,
                            'RT': rep-self.stim_onset,
                            'Red_Key': self.rep_red})
        file.close()

def checkpath(path):
    if not os.path.isdir(f'{data_path}'):
        os.makedirs(f'{data_path}')
        
    if not os.path.isdir(f'{data_path}{path}'):
        os.makedirs(f'{data_path}{path}')
        
    out_path = (f'{data_path}{path}/')
    return out_path

def load_experiment_flags(json_file):
    file= open(json_file, encoding ='utf_8')
    flags = json.load(file)
    settings =[]
    for i in flags:
        settings.append(flags[i])
    return settings
    

def main():
    greeting = start_screen(screen, info, Font)

    while not greeting.run_lang:
        for event in pygame.event.get():
            greeting.parse_event(event)

        screen.fill((255,255,255))
        greeting.subject_entry.update()
        greeting.session_entry.update()
        greeting.update()
        pygame.display.flip()
        clock.tick(60)
        
    screen.fill((255,255,255))
    pygame.display.flip()
    select_language = lang_screen(screen, info, Font)
    
    while not select_language.run_practice:
        for event in pygame.event.get():
            select_language.parse_event(event)
            select_language.update()
            pygame.display.flip()
            clock.tick(60)

    screen.fill((255,255,255))
    pygame.display.flip()
    out_path = checkpath(greeting.subject_info)
    settings = load_experiment_flags(f'{src}/settings.json')
    text_prompts = load_experiment_flags(f'{src}/{select_language.lang}')
    experiment_run = experiment(screen, info, greeting.subject_info, greeting.session_info, out_path, settings, text_prompts)

    while experiment_run.is_running:
        for event in pygame.event.get():
           experiment_run.event_handler(event)
        experiment_run.update_trial_state()

if __name__ == '__main__':
    main()
