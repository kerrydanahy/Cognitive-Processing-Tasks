#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Audio Processing Speed Task

Settings Json controls the task parameters
Lang_prompt Json controls the displayed text prompts
(isi of 300 and 1000)

auditory track volume level and check on max volume options.

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
from glob import glob
import math

#path variables
src = pathlib.Path(__file__).parents[0].resolve().as_posix()
image_path =  f"{src}/images/"
sound_path = f"{src}/sounds/"
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
                
            #print(x_start)
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
        self.Title_disp = TextDisplay('Welcome to the Audio Sustained Selective Attention task!', 
                                      self.width*.5, self.height*.1, self.width, self.height,
                                      Font, (0,0,0),100)
        
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
        self.run_sound_check = False
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
        self.run_sound_check = True

class Sound_Level_Check:
    
    def __init__(self, screen, info, Font, text_prompts):
        self.run_practice = False
        self.volume= 1
        self.Font = Font
        self.width = info.current_w
        self.height = info.current_h
        self.prompt = text_prompts[1]
        self.audio_prompt = TextDisplay(text_prompts[0], 
                                       self.width*.5, self.height*.1, self.width, self.height, Font, (0,0,0),100)
        self.screen = screen
        self.isi = 600
        self.clock = pygame.time.get_ticks()
        self.timer_start= True
        #audio settings
        self.sounds= sorted(glob(f'{sound_path}*.wav'))
        self.s_idx = 0
        self.PlaybackStart = pygame.USEREVENT+0
        self.PlaybackEnd = pygame.USEREVENT+1
        self.channel = pygame.mixer.Channel(1)
        self.channel.set_endevent(self.PlaybackEnd)
        

        
        self.audio_prompt.render(self.screen)
        
        
    def play_sound(self, file):
        sound= pygame.mixer.Sound(file)
        self.channel.set_volume(self.volume)
        self.channel.play(sound)
        
    def stop_sound(self):
        self.channel.stop()
        
    def parse_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                self.adjust_volume('down')
                self.s_idx = 0
                pygame.time.set_timer(self.PlaybackStart, self.isi+500)
                
                
            elif event.key == pygame.K_u:
                self.adjust_volume('up')
                self.s_idx = 0
                pygame.time.set_timer(self.PlaybackStart, self.isi+500)
                
            elif event.key == pygame.K_SPACE:
                if self.s_idx == 0:
                    pygame.time.set_timer(self.PlaybackStart, self.isi+500)
                else:
                    self.run_practice = True
            else:
                ''' forces response'''
                pass
        elif event.type == self.PlaybackEnd:
            self.s_idx +=1
            if self.s_idx == len(self.sounds):
                self.audio_prompt = TextDisplay(self.prompt, self.width*.5, self.height*.1, self.width, self.height, Font, (0,0,0), 100)
                self.audio_prompt.render(self.screen)
                pygame.time.set_timer(self.PlaybackStart, 0)
                '''wait for user response'''
                
        elif event.type == self.PlaybackStart:
            self.play_sound(self.sounds[self.s_idx])
                
    def update(self):
        self.audio_prompt.render(self.screen)
        
    def adjust_volume(self, adjustment):
        if adjustment == 'down':
            self.volume -=.3
            if self.volume == 0:
                self.volume = .1
                #print('message: set too low')
        else:
            self.volume += .2
            if self.volume > 1:
                self.volume =1
                #print('message: set too high')
                

class experiment:
    def __init__(self, screen, info, sbj, session, volume, out_path, settings, prompts):
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
        self.stim_mask = ['Keys','Carstart','DoorHandle','RaceCar']
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
        self.order= self.stim_mask
        
        #audio settings
        self.volume = volume
        self.sounds_dict = {'Keys': pygame.mixer.Sound(f'{sound_path}keys.wav'),
                            'Carstart': pygame.mixer.Sound(f'{sound_path}Carstart.wav'),
                            'DoorHandle': pygame.mixer.Sound(f'{sound_path}DoorHandle.wav'),
                            'RaceCar': pygame.mixer.Sound(f'{sound_path}RaceCar.wav')}
        self.s_idx = 0
        self.PlaybackStart = pygame.USEREVENT+0
        self.PlaybackEnd = pygame.USEREVENT+1
        self.Repwindow = pygame.USEREVENT+2
        self.channel = pygame.mixer.Channel(1)
        self.channel.set_endevent(self.PlaybackEnd)

        
        self.intro_text = prompts[2]
        self.correct_text = prompts[3]
        self.practice_text = prompts[4]
        self.task_text = prompts[5]
        self.exit_text = prompts[6]
        self.prac_fb_text = prompts[7]
        
        
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
        self.listen = ImageDisplay(f'{image_path}car.bmp', [self.width*.35,self.height*.3, self.width*.3, self.height*.44], 1)
        self.image_change = 'listen'
    
        #exp variables
        self.clock = pygame.time
        self.fix_time= 500
        self.current_trial = 0
        self.prac_correct = 0
        self.update_trial_state()
        self.event_dict= {self.rep_key: self.key_press,
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
         elif event.type == self.PlaybackEnd:
             #turn off audio playback timer
             pygame.time.set_timer(self.PlaybackStart, 0) #stops audio playback
             pygame.time.set_timer(self.Repwindow, 1000)

             # print(f'Expected time: {self.fix_time+ 1000}')
             # try:
             #    print(f'Elapsed time since last stim: {self.stim_onset-self.repwintime_debug}')
             # except:
             #    print('Calculating ISI requires 1st trial completion')
                
             # try:
             #    print(f'Stim_Dur: {self.clock.get_ticks()-self.stim_onset}')
             # except:
             #     pass
             #print(f'End of trial: {self.current_trial}')
             
             
         elif event.type == self.PlaybackStart:
             if self.intro:
                 self.play_sound(self.sounds_dict[self.order[self.s_idx]])
             else:
                 #print(f'loding stim: {self.order[self.current_trial-1]}')
                 #print(f'trial#: {self.current_trial}')
                 self.stim_onset = self.clock.get_ticks() #grabs time of audio playback start
                 self.play_sound(self.sounds_dict[self.order[self.current_trial-1]])
             self.can_respond = True
             
         elif event.type == self.Repwindow:
             #print('repwindow event')
             self.repwintime_debug= self.clock.get_ticks()
             #print(f'can respond: {self.can_respond}')
             pygame.time.set_timer(self.Repwindow, 0)
             if self.intro:
                 self.s_idx+=1
                 if self.s_idx >= 2:
                     self.key_press(' ')
                 else:
                     self.screen.fill((255,255,255))
                     pygame.display.flip()
                     self.current_trial+=1
             elif self.flag == 'f':
                 pass
             else:
                 if self.can_respond:
                     #if false we have already responded
                     self.key_press('norep')
                 else:
                    pass
                     #print('we responded already!')
                 pygame.time.set_timer(self.PlaybackStart, self.fix_time, 1)
    
    def play_sound(self, snd_obj):
        self.channel.set_volume(self.volume)
        self.channel.play(snd_obj)
        
    def stop_sound(self):
        self.channel.stop()
                
    def update_trial_state(self):
        if self.intro:
            if self.current_trial == 0:
                self.display_prompt('intro')
            else:
                self.display_intro_sequence(self.current_trial)
        elif self.practice:
            if self.current_trial == 0:
                self.display_prompt('practice')
                self.image_change= 'listen'
            else:
                if self.current_trial > self.num_practice:
                    self.practice = False
                    self.flag ='f'
                    self.current_trial = -1
                    self.display_prompt('feedback')
                    self.image_change= 'listen'
                    pygame.time.set_timer(self.PlaybackStart, 0)
                    pygame.time.set_timer(self.Repwindow, 0)
                else:
                    self.display_stim(self.image_change)
        else:
            '''Exp trial flow '''
            if self.current_trial == -1:
                self.display_prompt('feedback')
                self.can_respond= True
            elif self.current_trial == 0:
                self.display_prompt('trial_text')
                self.flag='f'
                pygame.time.set_timer(self.PlaybackStart, 0)
                self.order= [pos for idx, pos in enumerate(self.stim_mask) for count in range(self.trial_mask[idx])]  
                random.shuffle(self.order)
                self.exp = True
                self.image_change='listen'
            else:
                if self.current_trial > self.num_trials:
                    pygame.time.set_timer(self.PlaybackStart, 0)
                    self.display_prompt('ending')
                    self.can_respond = True
                else:
                    '''load/reload screen'''
                    self.display_stim(self.image_change)
                    
    def display_stim(self, flag):
        if flag == 'listen':
            self.listen.render(self.screen)
            pygame.display.flip()
            self.image_change = ' '
        elif flag == 'feedback':
            pass

    def display_prompt(self, flag):
        if flag == 'intro':
            self.text_prompts = TextDisplay(self.intro_text, self.width*.5, self.height*.1, self.width, self.height, Font, (0,0,0),100)
            self.text_prompts.render(self.screen)
        elif flag == 'correct':
            self.text_prompts = TextDisplay(self.correct_text, self.width*.5, self.height*.1, self.width, 400, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'practice':
            self.text_prompts = TextDisplay(self.practice_text, self.width*.5, self.height*.1, self.width, self.height, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'feedback':
            self.text_prompts = TextDisplay(f'{self.prac_fb_text}: {self.prac_correct}/{sum(self.practice_mask)}!\n Press SPACE to continue or r to repeat practice', self.width*.5, self.height*.1, self.width, 800, Font, (0,0,0), 100)
            #add image display here ?
            self.text_prompts.render(self.screen)
        elif flag == 'trial_text':
            self.text_prompts = TextDisplay(self.task_text, self.width*.5, self.height*.1, self.width, 800, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'ending':
            self.text_prompts = TextDisplay(self.exit_text, self.width*.5, self.height*.3, self.width, 400, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        pygame.display.flip()
    
    
    def display_intro_sequence(self, flag):
        if flag == 1:
            self.display_stim('listen')
            pygame.display.flip()
        elif flag ==2:
            self.display_prompt('correct')
            self.can_respond= True
        elif flag <6 : #8
            self.display_stim('listen')
            pass
        else:
            pygame.time.set_timer(self.PlaybackStart, 0)
            self.intro = False
            self.practice= True
            self.flag='f'
            self.current_trial =0
            self.screen.fill((255,255,255))
            self.order = [pos for idx, pos in enumerate(self.stim_mask) for count in range(self.practice_mask[idx])]     
            random.shuffle(self.order)
            self.update_trial_state()
                
    def key_press(self, key_id: str):
        rep=self.clock.get_ticks()
        if key_id == 'norep':
            rep = math.nan
            
        #print(f'key is: {key_id}')
        if self.can_respond:
            if  key_id == ' ':
                if self.intro:
                    self.screen.fill((255,255,255))
                    pygame.display.flip()
                    self.current_trial +=1
                    self.fix_time = 500
                    pygame.time.set_timer(self.PlaybackStart, self.fix_time+self.iti)
                    self.update_trial_state()
                    
                elif self.current_trial > self.num_trials:
                    self.is_running = False
                elif self.flag == 'f':
                    self.screen.fill((255,255,255))
                    pygame.display.flip()
                    #print('I am firing!!!')
                    self.flag='1'
                    self.current_trial +=1
                    self.fix_time = random.randrange(50,self.iti,50) #generate random time to delay
                    pygame.time.set_timer(self.PlaybackStart, self.fix_time, 1)
                    self.update_trial_state()
                
            elif key_id == 'r':
                if not self.exp:
                    self.screen.fill((255,255,255))
                    pygame.display.flip()
                    self.current_trial= 0
                    self.prac_correct = 0
                    self.practice = True
                    self.fix_time = random.randrange(50,self.iti,50) #generate random time to delay
                    self.order = [pos for idx, pos in enumerate(self.stim_mask) for count in range(self.practice_mask[idx])]     
                    random.shuffle(self.order)
                    self.update_trial_state()
                
            elif key_id == self.rep_key or 'norep':
                if self.practice or self.exp:
                    self.can_respond= False
                    #pygame.time.set_timer(self.Repwindow, 0)
                    self.screen.fill((255,255,255))
                    #pygame.display.flip()
                    self.response = self.target[key_id] #returns 1 or 0
   
                    if self.response == (self.order[self.current_trial-1]=='Keys'):
                        self.prac_correct +=1
                    self.correct = self.response == (self.order[self.current_trial-1]=='Keys')
                    self.log_data(rep)
                    self.current_trial +=1
                    self.fix_time = random.randrange(50,self.iti,50)


    def log_data(self,rep):
        if self.practice:
            tt = 'Practice'
        else:
            tt= self.current_trial
        
            
        file = open(f'{self.out_path}ASSA_{self.today}_{self.subject}_{self.session}.csv', 'a', newline ='')
        with file:
            header = ['Subject', 'Session', 'Date', 'Time', 'Volume', 'Trial', 'Stimulus', 'Response', 'Correct', 'RT', 'Rep_Key']
            writer = csv.DictWriter(file, fieldnames = header)
            
            # writing data row-wise into the csv file
            if self.current_trial ==1 and self.practice:
                writer.writeheader()
            writer.writerow({'Subject' : self.subject,
                            'Session' : self.session,
                            'Date' : self.today,
                            'Time' : self.hour,
                            'Volume' : self.volume,
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
    
    while not select_language.run_sound_check:
        for event in pygame.event.get():
            select_language.parse_event(event)
            select_language.update()
            pygame.display.flip()
            clock.tick(60)
    #load settings and prompts
    settings = load_experiment_flags(f'{src}/settings.json')
    text_prompts = load_experiment_flags(f'{src}/{select_language.lang}')
    sound_check = Sound_Level_Check(screen, info, Font, text_prompts)
    
    while not sound_check.run_practice:
        for event in pygame.event.get():
            screen.fill((255,255,255))
            sound_check.parse_event(event)
            sound_check.update()
            pygame.display.flip()
            clock.tick(60)
    screen.fill((255,255,255))
    pygame.display.flip()
    out_path = checkpath(greeting.subject_info)

    experiment_run = experiment(screen, info, greeting.subject_info, greeting.session_info,sound_check.volume, out_path, settings, text_prompts)

    while experiment_run.is_running:
        for event in pygame.event.get():
           experiment_run.event_handler(event)
        experiment_run.update_trial_state()

if __name__ == '__main__':
    main()
