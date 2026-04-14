#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Visual Sustained Selective Attention Task

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
from datetime import date, datetime
import math

#path variables
src = pathlib.Path(__file__).parents[0].resolve().as_posix()
image_path =  f"{src}/images/"
data_path = f"{src}/logs/"


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
                self.image,(self.position[2],self.position[3])),self.rect)
        
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
        self.Title_disp = TextDisplay('Welcome to the Visual Sustained Selective Attention task!', 
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
        self.out_path = out_path
        self.is_running= True
        self.intro = True
        self.practice = False
        self.exp = False
                
        # Experimenter flags, user can change these with settings file
        #uses set layout in order below
        self.stim_mask = ['LL','LR','UL','UR']
        self.practice_mask=settings[0]
        self.trial_mask = settings[1]
        self.iti = settings[2]
        self.stim_dur = settings[3]
        self.rep_key = settings[4] #sets response key
        self.target = {self.rep_key: 1,
                       'norep': 0}
        self.can_respond = True # flag for blocking user input until wanted
        self.num_practice = sum(self.practice_mask)
        self.num_trials = sum(self.trial_mask)
        # Set the random presentation orders     
        ## below creates a list of position masks based on the specified counts passed in
        ## order is always LL, LR, UL, UR
        self.order = [pos for idx, pos in enumerate(self.stim_mask) for count in range(self.practice_mask[idx])]     
        random.shuffle(self.order)
        
        self.intro_text = prompts[0]
        self.correct_text = prompts[1]
        self.practice_text = prompts[2]
        self.task_text = prompts[3]
        self.exit_text = prompts[4]
        self.prac_fb_text = prompts[5]
        
        
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
        self.stim_LL = ImageDisplay(f'{image_path}LL.bmp', [0,0, self.width, self.height], 1)
        self.stim_LR = ImageDisplay(f'{image_path}LR.bmp', [0,0, self.width, self.height], 0)
        self.stim_UL = ImageDisplay(f'{image_path}UL.bmp', [0,0, self.width, self.height], 0)
        self.stim_UR = ImageDisplay(f'{image_path}UR.bmp', [0,0, self.width, self.height], 0)
        self.stim_blank = ImageDisplay(f'{image_path}blank.bmp', [0,0, self.width, self.height],0)
        #dict of image generation functions called for displaying
        self.imgen_dict = {'LL': self.stim_LL.render,
                           'LR': self.stim_LR.render,
                           'UL': self.stim_UL.render,
                           'UR': self.stim_UR.render,
                           'BLNK' : self.stim_blank.render}

    
        #exp variables
        self.flip = 1
        self.clock = pygame.time
        self.current_trial = 0
        self.prac_correct = 0
        self.update_trial_state()
        self.event_dict= {self.rep_key: self.key_press,
                          ' ' : self.key_press,
                          'r' : self.key_press,
                          '\x1b' : self.force_quit}

 
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
         
    def force_quit(self, key_id):
        #Pressing the escape key will not exit the task
        self.is_running = False
           
    def update_trial_state(self):
        if self.intro:
            if self.current_trial == 0:
                self.display_prompt('intro')
                self.stage='f'
            else:
                self.display_intro_sequence(self.current_trial)
        elif self.practice:
            if self.current_trial == 0:
                self.display_prompt('practice')
            else:
                if self.current_trial > self.num_practice:
                    self.practice = False
                    self.current_trial = -1
                    self.display_prompt('feedback')
                    self.stage='f'
                else:
                    self.timer_run(self.flag)
        else:
            '''Exp trial flow '''
            if self.current_trial == -1:
                self.display_prompt('feedback')
                self.can_respond= True
            elif self.current_trial == 0:
                self.display_prompt('trial_text')
                self.stage='f'
                self.order= [pos for idx, pos in enumerate(self.stim_mask) for count in range(self.trial_mask[idx])]  
                random.shuffle(self.order)
                self.exp = True
            else:
                if self.current_trial > self.num_trials:
                    self.display_prompt('ending')
                    self.can_respond = True
                else:
                    '''load/reload screen'''
                    self.timer_run(self.flag)

    def display_prompt(self, flag):
        if flag == 'intro':
            self.text_prompts = TextDisplay(self.intro_text, self.width*.5, self.height*.1, self.width, 800, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'correct':
            self.text_prompts = TextDisplay(self.correct_text, self.width*.5, self.height*.1, self.width, self.height, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'practice':
            self.text_prompts = TextDisplay(self.practice_text, self.width*.5, self.height*.1, self.width, self.height, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'feedback':
            self.text_prompts = TextDisplay(f'{self.prac_fb_text}: {self.prac_correct}/10 !\nPress SPACE to continue or r to repeat practice', self.width*.5, self.height*.1, self.width, 800, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'trial_text':
            self.text_prompts = TextDisplay(self.task_text, self.width*.5, self.height*.1, self.width, 800, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'ending':
            self.text_prompts = TextDisplay(self.exit_text, self.width*.5, self.height*.3, self.width, 400, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        pygame.display.flip()
    
    def timer_intro_run(self, flag):
        '''Handles timing of sequences '''
        t= self.clock.get_ticks()
        if t<(self.trial_start+self.stim_dur +600):
            pass
        else:
            self.current_trial +=1
            self.trial_start = self.clock.get_ticks()
            self.display_intro_sequence(self.current_trial)
    
    def display_intro_sequence(self, flag):
        seq= ['LL', 'UL', 'UR', 'LR']
        if flag == 1:
            self.imgen_dict[seq[self.current_trial-1]](self.screen) #display target box
            pygame.display.flip()
        elif flag ==2:
            self.display_prompt('correct')
            self.can_respond= True
            self.stage='f'
        elif flag <6 :
            self.imgen_dict[seq[self.current_trial-2]](self.screen)
            self.timer_intro_run('intro')
            pygame.display.flip()
        else:
            self.intro = False
            self.practice= True
            self.stage='f'
            self.current_trial =0
            self.screen.fill((255,255,255))
            self.update_trial_state()
                
    def timer_run(self, flag):
        t= self.clock.get_ticks()
        if flag == 'blank':
            if t <(self.trial_start+self.iti):
                if self.flip:
                    self.imgen_dict['BLNK'](self.screen)
                    pygame.display.flip()
                    self.flip=0
            else:
                self.flip=1
                self.trial_start = self.clock.get_ticks()
                self.imgen_dict[self.order[self.current_trial-1]](self.screen)
                self.stim_onset = t
                self.flag = 'stim'
                self.can_respond= True
                pygame.display.flip()
        elif flag == 'stim':
            if t< (self.trial_start +self.stim_dur):
                if self.flip:
                    self.imgen_dict[self.order[self.current_trial-1]](self.screen)
                    pygame.display.flip()
                    self.flip=0
            else:
                self.flip=1
                self.trial_start = self.clock.get_ticks()
                self.flag='rep_window'
                self.imgen_dict['BLNK'](self.screen)
                pygame.display.flip()
        elif flag == 'rep_window':
            if t<(self.trial_start+self.iti):
                if self.flip:
                    self.imgen_dict['BLNK'](self.screen)
                    pygame.display.flip()
                    self.flip=0
            else:
                self.key_press('norep')
                
        
                
    def key_press(self, key_id: str):
        rep=self.clock.get_ticks()
        if key_id == 'norep':
            rep = math.nan
            
        if self.can_respond:
            if  key_id == ' ':
                if self.current_trial > self.num_trials:
                    self.is_running = False
                elif self.stage =='f':
                    self.screen.fill((255,255,255))
                    pygame.display.flip()
                    self.current_trial +=1
                    self.trial_start= self.clock.get_ticks()
                    self.stage='1'
                    self.update_trial_state()
                
            elif key_id == 'r':
                if not self.exp:
                    self.screen.fill((255,255,255))
                    pygame.display.flip()
                    self.current_trial= 0
                    self.prac_correct = 0
                    self.practice = True
                    self.order = [pos for idx, pos in enumerate(self.stim_mask) for count in range(self.practice_mask[idx])]     
                    random.shuffle(self.order)
                    self.trial_start= self.clock.get_ticks()
                    self.update_trial_state()
                
            elif key_id == self.rep_key or 'norep':
                    self.can_respond= False
                    self.flip=1
                    self.flag='blank'
                    self.screen.fill((255,255,255))
                    #pygame.display.flip()
                    self.response = self.target[key_id] #returns 1 or 0
                    
                    if self.intro:
                        self.current_trial +=1
                        self.display_prompt('correct')
                        
                    else:
                        if self.response == (self.order[self.current_trial-1]=='LL'):
                            self.prac_correct +=1
                        self.correct = self.response == (self.order[self.current_trial-1]=='LL')
                        self.log_data(rep)
                        self.current_trial +=1
                        self.trial_start= self.clock.get_ticks()
                        self.update_trial_state()

    def log_data(self,rep):
        if self.practice:
            tt= 'Practice'
        else:
            tt= self.current_trial
            
        file = open(f'{self.out_path}VSSA_{self.today}_{self.subject}_{self.session}.csv', 'a', newline ='')
        with file:
            header = ['Subject', 'Date', 'Session', 'Time', 'Trial', 'Stimulus', 'Response', 'Correct', 'RT', 'Rep_Key']
            writer = csv.DictWriter(file, fieldnames = header)
            
            # writing data row-wise into the csv file
            if self.current_trial ==1 and self.practice:
                writer.writeheader()
            writer.writerow({'Subject' : self.subject,
                            'Date' : self.today,
                            'Time' : self.hour,
                            'Session' : self.session,
                            'Trial' : tt,
                            'Stimulus' : self.order[self.current_trial-1],
                            'Response' : self.response,
                            'Correct': self.correct,
                            'RT': rep-self.stim_onset,
                            'Rep_Key': self.rep_key})
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
