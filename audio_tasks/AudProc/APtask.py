#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Auditory Processing Speed Task

Settings Json controls the task parameters
Lang_prompt Json controls the displayed text prompts

Note there is a 2s rep window for this task

add R for repeat and % correct during practice

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
from glob import glob
from datetime import date, datetime

#path variables
src = pathlib.Path(__file__).parents[0].resolve().as_posix()
image_path =  f"{src}/images/"
sound_path = f"{src}/sounds/"
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
        self.Title_disp = TextDisplay('Welcome to the Audio Processing Speed task!', 
                                      self.width*.5, self.height*.1, self.width, self.height,
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
        self.volume= 1      #volume starts at the max value
        self.Font = Font
        self.width = info.current_w
        self.height = info.current_h
        self.prompt = text_prompts[1]
        self.audio_prompt = TextDisplay(text_prompts[0], 
                                       self.width*.5, self.height*.1, self.width, self.height, Font, (0,0,0), 100)
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
                self.clock = pygame.time.get_ticks()
                pygame.time.set_timer(self.PlaybackStart, self.isi)
                
                
            elif event.key == pygame.K_u:
                self.adjust_volume('up')
                self.s_idx = 0
                self.clock = pygame.time.get_ticks()
                pygame.time.set_timer(self.PlaybackStart, self.isi)
                
            elif event.key == pygame.K_SPACE:
                if self.s_idx == 0:
                    #start playback
                    pygame.time.set_timer(self.PlaybackStart, self.isi)
                else:
                    self.run_practice = True
            else:
                ''' forces response'''
                pass
        elif event.type == self.PlaybackEnd:
            #print(f'End_Playback')
            self.s_idx +=1
            #print(f'{self.s_idx} loaded next sound')
            if self.s_idx == len(self.sounds):
                self.audio_prompt = TextDisplay(self.prompt, self.width*.5, self.height*.1, self.width, self.height, Font, (0,0,0), 100)
                self.audio_prompt.render(self.screen)
                pygame.time.set_timer(self.PlaybackStart, 0)
                '''wait for user response'''
                
        elif event.type == self.PlaybackStart:
            #print(f'playing sound: {self.s_idx}')
            self.play_sound(self.sounds[self.s_idx])
                
    def update(self):
        self.audio_prompt.render(self.screen)
        
    def adjust_volume(self, adjustment):
        if adjustment == 'down':
            self.volume -=.3
            if self.volume == 0:
                self.volume = .2
                print('message set too low')
        else:
            self.volume += .1
            if self.volume > 1:
                self.volume =1
                print('message set too high')
                
    
class experiment:
    def __init__(self, screen, info, sbj, session, volume, out_path, settings, prompts):
        #general display settings
        self.screen = screen
        self.width = info.current_w
        self.height = info.current_h
        self.smile = f"{image_path}smiley1.bmp"
        self.ear = f"{image_path}listen.bmp"
        self.x = f"{image_path}x.bmp"
        self.out_path = out_path
        self.is_running= True
        self.practice = True
        self.can_respond = True
        

                
        # Experimenter flags, user can change these with settings file
        #uses set layout in order below
        self.num_practice = settings[0]
        self.num_high_prac = settings[1]
        self.num_trials = settings[2]
        self.num_htrial = settings[3]
        self.iti = settings[4]
        self.stim_dur = settings[5]
        self.rep_high, self.rep_low = settings[6] #sets response keys [high, low]
        # Set the random presentation orders
        sequence= (self.rep_high + ' ')* self.num_high_prac + (self.rep_low+' ')*(self.num_practice-self.num_high_prac)
        sequence= sequence.split(' ')[0:-1]
        self.practice_order = random.sample(sequence, k = self.num_practice)
        sequence= (self.rep_high + ' ')* self.num_htrial + (self.rep_low+' ')*(self.num_trials-self.num_htrial)
        sequence= sequence.split(' ')[0:-1]
        self.trial_order = random.sample(sequence,  k = self.num_trials)
        
        #audio settings
        self.volume = volume
        self.sounds_dict = {self.rep_high: pygame.mixer.Sound(f'{sound_path}2000.wav'), self.rep_low: pygame.mixer.Sound(f'{sound_path}500.wav') }
        self.s_idx = 0
        self.PlaybackStart = pygame.USEREVENT+0
        self.PlaybackEnd = pygame.USEREVENT+1
        self.Repwindow = pygame.USEREVENT+2
        self.channel = pygame.mixer.Channel(1)
        self.channel.set_endevent(self.PlaybackEnd)
        
        
        self.practice_text = prompts[2]
        self.correct_text = prompts[3]
        self.incorrect_text = prompts[4]
        self.trial_text = prompts[5]
        self.exit_text = prompts[6]
        
        
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
        self.correct_fb = ImageDisplay(self.smile, [self.width*.3, self.height*.2, self.width*.4, self.height*.52], 'blue') #fix stim
        self.incorrect_fb = ImageDisplay(self.x,[0, 0, self.width, self.height], 'blue')
        self.listen = ImageDisplay(self.ear, [self.width*.3, self.height*.3, self.width*.4,self.height*.49], 'listen')

        #exp variables
        self.clock = pygame.time
        self.current_trial = 0
        self.window= 60000      #20s window for practice, changes to 2s for exp
        self.update_trial_state()
        self.event_dict= {self.rep_high: self.key_press,
                          self.rep_low: self.key_press,
                          ' ': self.key_press,
                          'r': self.key_press,
                          '\x1b' : self.force_quit}
        
        self.state = 'listen'

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
             #print(f'trial#: {self.current_trial}')
             #print(f'stimulus: {self.stims[self.current_trial-1]}')
             #print(f'{self.state}')
             
             #pygame.time.set_timer(self.Repwindow, 2000)
             
         elif event.type == self.PlaybackStart:
             self.stim_onset = self.clock.get_ticks() #grabs time of audio playback start
             self.play_sound(self.sounds_dict[self.stims[self.current_trial-1]])
             self.can_respond = True
             pygame.time.set_timer(self.Repwindow, self.window)
             
         elif event.type == self.Repwindow:
             pygame.time.set_timer(self.Repwindow, 0)
             if self.can_respond:
                self.key_press('timeout')
             elif self.current_trial > self.num_practice:
                self.can_respond = True
             #else:
                #this is for debugging
                #print('we responded already!')
            
         
    def play_sound(self, snd_obj):
        self.channel.set_volume(self.volume)
        self.channel.play(snd_obj)
        
    def stop_sound(self):
        self.channel.stop()
                
    def update_trial_state(self):
        if self.practice:
            if self.current_trial == 0:
                self.display_prompt('instruction')
                self.flag='f'
                self.stims=self.practice_order
            else:
                if self.current_trial > self.num_practice:
                    self.practice = False
                    pygame.time.set_timer(self.PlaybackStart, 0)
                    self.current_trial = 0
                    self.display_prompt('trial_text')
                    self.flag='f'
                    self.can_respond = False
                    self.window = 2000
                else:
                    self.display_stim(self.state)
        else:
            '''Exp trial flow '''
            if self.current_trial == 0:
                self.display_prompt('trial_text')
                self.stims=self.trial_order
                self.can_respond = True
            else:
                if self.current_trial > self.num_trials:
                    pygame.time.set_timer(self.PlaybackStart, 0)
                    self.can_respond = True
                    self.display_prompt('ending')
                    self.flag='f'
                    
                else:
                    '''load/reload screen'''
                    self.display_stim(self.state)
                    
    def display_stim(self, flag ):
        if flag == 'listen':
            self.listen.render(self.screen)
            pygame.display.flip()
        elif flag == 'feedback':
            pass

    def display_prompt(self, flag):
        if flag == 'instruction':
            self.text_prompts = TextDisplay(self.practice_text, self.width*.5, self.height*.1, self.width, self.height, Font, (0,0,0),100)
            self.text_prompts.render(self.screen)
            pygame.display.flip()
        elif flag == 'correct':
            self.text_prompts = TextDisplay(self.correct_text, self.width*.5, self.height*.7, self.width, 400, Font, (0,0,0),100)
            self.correct_fb.render(self.screen)
            self.text_prompts.render(self.screen)
        elif flag == 'incorrect':
            self.text_prompts = TextDisplay(self.incorrect_text, self.width*.5, self.height*.7, self.width, 400, Font, (0,0,0),100)
            self.incorrect_fb.render(self.screen)
            self.text_prompts.render(self.screen)
        elif flag == 'trial_text':
            self.text_prompts = TextDisplay(self.trial_text, self.width*.5, self.height*.1, self.width, self.height, Font, (0,0,0),100)
            self.text_prompts.render(self.screen)
        elif flag == 'ending':
            self.text_prompts = TextDisplay(self.exit_text, self.width*.5, self.height*.3, self.width, self.height, Font, (0,0,0),100)
            self.text_prompts.render(self.screen)
            
        pygame.display.flip()
    

    def key_press(self, key_id: str):
        #print('response key')
        rep=self.clock.get_ticks()
        if self.can_respond:
            if  key_id == ' ':
                if self.current_trial > self.num_trials:
                    self.is_running = False
                elif self.flag =='f':
                    #blank screen, silence user response, reset practice trials
                    self.screen.fill((255,255,255))
                    self.state = 'listen'
                    self.can_respond = False
                    pygame.display.flip()
                    self.current_trial +=1
                    self.fix_time = random.randrange(1000,3000,500) #generate random time to delay between 1-3 s by .5 steps
                    pygame.time.set_timer(self.Repwindow, 0)
                    pygame.time.set_timer(self.PlaybackStart, self.fix_time+self.iti)
                    
                    self.debug = self.clock.get_ticks()
                    self.flag='1'
                    self.update_trial_state()
                
            elif key_id == 'r':
                if self.current_trial == 0:
                    self.screen.fill((255,255,255))
                    pygame.display.flip()
                    self.state = 'listen'
                    self.can_respond = True
                    self.current_trial= 0
                    self.practice = True
                    self.fix_time = random.randrange(1000,3000,500) #generate random time to delay between 1-3 s by .25 steps
                    self.update_trial_state()
                
            elif key_id == self.rep_high or key_id ==self.rep_low or key_id == 'timeout':
                if self.state == 'listen':
                    self.screen.fill((255,255,255))
                    pygame.display.flip()
                    self.response = key_id
                    if self.practice:
                        self.log_data(rep)
                        self.state= 'feedback'
                        if key_id == self.practice_order[self.current_trial-1]:
                            self.display_prompt('correct')
                            
                        else:
                            self.display_prompt('incorrect')
                        self.flag='f'
                            
                    else:
                        #print('logged key press')
                        self.debug = self.clock.get_ticks()
                        self.can_respond = False
                        self.correct = self.response == self.trial_order[self.current_trial-1]
                        self.log_data(rep)
                        self.current_trial +=1
                        self.fix_time = random.randrange(1000,3000,500) #generate random time to delay between 1-3 s by .25 steps
                        pygame.time.set_timer(self.PlaybackStart, self.fix_time+self.iti)
                        self.update_trial_state()
                    
    def log_data(self,rep):
        if self.practice:
            tt = 'Practice'
        else:
            tt = self.current_trial
            
        file = open(f'{self.out_path}AP_{self.today}_{self.subject}_{self.session}.csv', 'a', newline ='')
        with file:
            header = ['Subject', 'Session', 'Date', 'Time','Volume', 'Trial', 'Stimulus', 'Response', 'Correct', 'RT', 'High_Key']
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
                            'Stimulus' : self.trial_order[self.current_trial-1],
                            'Response' : self.response,
                            'Correct': self.correct,
                            'RT': rep-self.stim_onset,
                            'High_Key': self.rep_high})
        file.close()
        #print('logged data')

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
    experiment_run = experiment(screen, info, greeting.subject_info, greeting.session_info, sound_check.volume, out_path, settings, text_prompts)

    while experiment_run.is_running:
        for event in pygame.event.get():
           experiment_run.event_handler(event)
        experiment_run.update_trial_state()

if __name__ == '__main__':
    main()
