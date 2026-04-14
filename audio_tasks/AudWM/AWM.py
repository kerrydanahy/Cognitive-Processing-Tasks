#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Audio Working Memory Task

Settings Json controls the task parameters
Lang_prompt Json controls the displayed text prompts
isi = 500
iti = 1000
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

#path variables
src = pathlib.Path(__file__).parents[0].resolve().as_posix()
image_path =  f"{src}/images/"
data_path = f"{src}/logs/"
sound_path = f"{src}/sounds/"

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
        self.Title_disp = TextDisplay('Welcome to the Audio Working Memory task!', 
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
                                       self.width*.5, self.height*.1, self.width, 900, Font, (0,0,0),100)
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
                self.audio_prompt = TextDisplay(self.prompt, self.width*.5, self.height*.1, self.width, 900, Font, (0,0,0),100)
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
        self.screen = screen
        self.width = info.current_w
        self.height = info.current_h
        self.out_path = out_path
        self.is_running= True
        self.intro = True
        self.practice = False
        self.exp = False
        self.can_respond = True
        self.stage = 1 
        self.state = None
        self.stim_idx = 0
        self.acc_count= 0
        self.last_correct= True

        
        # Experimenter flags, user can change these with settings file
        #uses set layout in order below
        self.num_trials_sequence= settings[0]
        self.iti = settings[2]
        self.stim_dur = settings[3]
        self.isi = settings[4]
        self.w_key, self.r_key = settings[5] #sets response key
        # Set up sequences
        self.block_size= settings[1]
        self.stim_seq= self.gen_stim_sequence(self.num_trials_sequence[0], self.block_size[0], 2)
        self.lvl=1

        self.intro_text = prompts[2]
        self.demofb_text = prompts[3]
        self.demo2_text = prompts[4]
        self.correct_text = prompts[5]
        self.incorrect_text = prompts[6]
        self.practice_text = prompts[7]
        self.task_text = prompts[8]
        self.lvl2_text = prompts[9]
        self.lvl3_text = prompts[10]
        self.lvl3_text = prompts[11]
        self.exit_text = prompts[12]
        self.lvl_text = {2 : prompts[9],
                         3: prompts[10],
                         4: prompts [11]}

        
        
        #trial data
        d = date.today()
        self.today = d.strftime("%y-%m-%d")
        self.hour = datetime.now().strftime("%H:%M:%S")
        self.subject = sbj
        self.session = session
        self.volume = volume
        self.response = []
        self.stimuli = []
        self.correct = []
        self.trial_num = []

        #set image displays
        self.smiley = ImageDisplay(f'{image_path}smiley1.bmp', [self.width*.3, self.height*.2, self.width*.4, self.height*.52], 0)
        self.fix1 = ImageDisplay(f'{image_path}fix1.bmp', [self.width*.3, self.height*.3, self.width*.4, self.height*.4], 0)
        self.fix2 = ImageDisplay(f'{image_path}fix2.bmp', [self.width*.3, self.height*.3, self.width*.4, self.height*.4], 0)
        self.listen = ImageDisplay(f'{image_path}Listen.bmp', [self.width*.3,self.height*.3, self.width*.4, self.height*.4], 0)        
        
        #Audio settings
        self.sounds_dict = {1: pygame.mixer.Sound(f'{sound_path}250.wav'),
                     2: pygame.mixer.Sound(f'{sound_path}500.wav'),
                     3: pygame.mixer.Sound(f'{sound_path}1000.wav'),
                     4: pygame.mixer.Sound(f'{sound_path}2000.wav'),
                     5: pygame.mixer.Sound(f'{sound_path}3000.wav')}
        self.volume = volume
        self.PlaybackStart = pygame.USEREVENT+0
        self.PlaybackEnd = pygame.USEREVENT+1
        self.channel = pygame.mixer.Channel(1)
        self.channel.set_endevent(self.PlaybackEnd)
        self.can_play = True
        self.get_time = True
 
        self.fixgen_dict = {'1': self.fix1.render,
                            '2': self.fix2.render}

        #exp variables
        self.clock = pygame.time
        self.current_trial = 0
        self.prac_correct = 0
        self.update_trial_state()
        self.event_dict= {self.r_key: self.key_press,
                          self.w_key: self.key_press,
                          ' ': self.key_press,
                          'r': self.key_press,
                          '\x1b': self.force_quit}
    
    def force_quit(self, key_id):
        #Force quit the task
        self.is_running = False
        
    def gen_stim_sequence(self, num_stims, block_size, lvl):
        rep_pos=[]
        for i in range(block_size):
            s_point = random.sample([0,1],1)[0]
            for i in range(4):
                if i % 2 == 0:
                    s_point = int(not s_point)
                rep_pos.append(s_point)
            
        stim_sequence = []
        for i in rep_pos:
            t = random.choices([1,2,3,4,5], k=lvl)
            t.append(int(i))
            stim_sequence.append(t)
        #random.shuffle(stim_sequence)
        return stim_sequence
    
    def parse_seq(self, stim_seq):
        if stim_seq[-1]:
            stim_seq.pop()
            stim_seq=stim_seq+stim_seq
            loc_diff = 0
            
        else:
            stim_seq.pop()
            ld= len(stim_seq)
            loc_diff = random.choice(range(1,ld))
            weights= [1,1,1,1,1]
            stim_seq=stim_seq+stim_seq
            weights[stim_seq[loc_diff+ld]-1] = 0
            stim_seq[ld+loc_diff]= random.choices([1,2,3,4,5], weights=weights)[0]
            loc_diff = loc_diff +ld +1
        return stim_seq, loc_diff
    
    def event_handler(self, event):
         if event.type == pygame.KEYDOWN:
             try:
                 '''pass key press to the dictionary of functions'''
                 self.event_dict[chr(event.key)](chr(event.key))
             except:
                '''if pressed key is not in the event dictionary do nothing'''
                pass
         elif event.type == self.PlaybackEnd:
            pass
             #print('end playback')

       
    def play_sound(self, snd_obj):
        self.channel.set_volume(self.volume)
        self.channel.play(snd_obj)
        
    def stop_sound(self):
        self.channel.stop()
                
    def update_trial_state(self):
        if self.intro:
            if self.current_trial == 0:
                self.display_prompt('intro')
                self.last_call= self.clock.get_ticks()
            elif self.current_trial == 2:
                self.display_prompt('demo2')
            elif self.current_trial ==3:
                self.display_stim('Demo2')
            elif self.current_trial == 4:
                self.intro=False
                self.practice = True
                self.current_trial=0
                self.trial_seq, self.loc_diff = self.parse_seq(self.stim_seq[self.current_trial])
                self.stage='f'
            else:
                self.display_stim('Demo')
        elif self.practice:
            if self.current_trial == 0:
                self.display_prompt('practice')
            else:
                if self.current_trial > self.num_trials_sequence[0]:
                    self.stim_seq= self.gen_stim_sequence(self.num_trials_sequence[self.lvl], self.block_size[self.lvl], self.lvl+1)
                    self.practice = False
                    self.stage='f'
                    self.acc_count = 0
                    self.current_trial = 0
                    self.screen.fill((255,255,255))
                    self.display_prompt('trial_text')
                else:
                    if self.stage == 'f':
                        self.display_prompt('feedback')
                    else:
                        self.display_stim('Practice')
        else:
            '''Exp trial flow '''
            if self.current_trial> self.num_trials_sequence[self.lvl]:
                self.can_respond = True
                self.stage= 'DONE!'
                self.display_prompt('ending')
            elif self.current_trial == 0:
                self.display_prompt('trial_text')
            else:
                if self.stage == 'f':
                    self.display_prompt('lvl_up')
                else:
                    self.display_stim(self.lvl)


    def display_prompt(self, flag):
        if flag == 'intro':
            self.text_prompts = TextDisplay(self.intro_text, self.width*.5, self.height*.05, self.width, 800, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen) 
        elif flag == 'demo2':
            self.text_prompts = TextDisplay(self.demo2_text, self.width*.5, self.height*.1, self.width, 800, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'demofb':
            self.text_prompts = TextDisplay(self.demofb_text, self.width*.5, self.height*.1, self.width, 800, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'feedback':
            if self.correct:
                self.text_prompts = TextDisplay(self.correct_text, self.width*.5, self.height*.7, self.width, self.height, Font, (0,0,0), 100)
                self.smiley.render(self.screen)
                self.text_prompts.render(self.screen)
            else:
                self.text_prompts = TextDisplay(self.incorrect_text, self.width*.5, self.height*.1, self.width, 400, Font, (0,0,0), 100)
                self.text_prompts.render(self.screen)
        elif flag == 'practice':
            self.text_prompts = TextDisplay(self.practice_text, self.width*.5, self.height*.1, self.width, 400, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'lvl_up':
            self.text_prompts = TextDisplay(self.lvl_text[self.lvl], self.width*.5, self.height*.1, self.width, 800, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'trial_text':
            self.text_prompts = TextDisplay(self.task_text, self.width*.5, self.height*.1, self.width, 800, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        elif flag == 'ending':
            self.text_prompts = TextDisplay(self.exit_text, self.width*.5, self.height*.3, self.width, 400, Font, (0,0,0), 100)
            self.text_prompts.render(self.screen)
        pygame.display.flip()
    
    def timer_run(self, flag, pos_seq):
        t = self.clock.get_ticks()
        if flag == 'seq':
            if self.can_play:
                #print('play audio')
                #try:
                    #print(f'ISI setting: {self.isi}')
                    #print(f'ISI real: {self.clock.get_ticks()-self.pt}')
                #except:
                 #   pass
                self.pt= self.clock.get_ticks()
                self.play_sound(self.sounds_dict[pos_seq])
                self.can_play= False
            if t <(self.last_call+self.isi):
                pass
            else:
                #print(self.stage)
                self.stage +=1
                self.last_call = self.clock.get_ticks()

        elif flag == 'blank':
            #print(f'{flag}')
            self.last_call = self.clock.get_ticks()
            self.stage +=1
            self.can_play = True
            self.stim_idx +=1
            
        elif flag == 'fix':
            if t<(self.last_call +self.iti):
                if pos_seq == '1':
                    self.screen.fill((255,245,0))
                    self.bg_color = (255,245,0)
                else:
                    self.screen.fill((154,217,234))
                    self.bg_color = (154,217,234)
                self.fixgen_dict[pos_seq](self.screen)
            else:
                self.last_call = self.clock.get_ticks()
                self.stage +=1
                self.can_play = True
                #print(f'{flag}')

            pygame.display.flip()
        
    def display_stim(self, flag):
        if flag == 'Demo':    
            if self.stage == 1:
                self.can_respond = False
                self.timer_run('fix', '1')
            elif self.stage == 2:
                self.timer_run('seq', 4)
            elif self.stage == 3:
                self.timer_run('blank', None)
            elif self.stage == 4:
                self.timer_run('seq', 3)
            elif self.stage == 5:
                self.timer_run('fix', '2')
            elif self.stage == 6:
                self.timer_run('seq', 4)
            elif self.stage == 7:
                self.timer_run('blank', None)
            elif self.stage == 8:
                self.timer_run('seq', 3)
            elif self.stage ==9:
                self.screen.fill((255,255,255))
                pygame.display.flip()
                self.stage +=1
                self.display_prompt('demofb')
                self.can_respond = True
               
            else:
                self.display_prompt('demofb')
                
                
        elif flag == 'Demo2':
            if self.stage == 1:
                self.can_respond = False
                self.timer_run('fix', '1')
            elif self.stage == 2:
                self.timer_run('seq', 4)
            elif self.stage == 3:
                self.timer_run('blank', None)
            elif self.stage == 4:
                self.timer_run('seq', 2)
            elif self.stage == 5:
                self.timer_run('fix', '2')
            elif self.stage == 6:
                self.timer_run('seq', 4)
            elif self.stage == 7:
                self.timer_run('blank', None)
            elif self.stage == 8:
                self.timer_run('seq', 5)
            elif self.stage ==9:
                self.screen.fill((255,255,255))
                pygame.display.flip()
                self.stage +=1
                self.display_prompt('demofb')
                self.can_respond = True
               
            else:
                self.display_prompt('demofb')
                

                
        elif flag == 'Practice':
            if self.stage == 1:
                self.can_respond = False
                self.timer_run('fix', '1')
            elif self.stage%2 == 0:
                if self.stage == (1*2)+4:
                    self.stim_idx= 1+1
                if self.stage == 8:
                    self.can_respond = True
                    if self.get_time:
                        self.stim_onset = self.clock.get_ticks()
                        self.get_time= False
                self.timer_run('seq', self.trial_seq[self.stim_idx])
            elif self.stage%2 == 1:
                if self.stage >=9:
                    pass
                elif self.stage == 5:
                    self.timer_run('fix', '2')
                else:
                    self.timer_run('blank', None)
                
        elif flag > 0:
            if self.stage == 1:
                self.can_respond = False
                self.timer_run('fix', '1')
            elif self.stage%2 == 0:
                if self.stage == ((flag*2)+4):
                    self.stim_idx = flag+1
                if self.stage == ((flag+1)*4):
                    self.can_respond = True
                    if self.get_time:
                        self.stim_onset = self.clock.get_ticks()
                        self.get_time= False
                self.timer_run('seq', self.trial_seq[self.stim_idx])
            elif self.stage%2 == 1:
                if self.stage >=(((flag+1)*4)+1):
                    pass
                elif self.stage == (flag*2)+3:
                    self.timer_run('fix', '2')
                else:
                    self.timer_run('blank', None)

                                 
                
    def key_press(self, key_id: str):
        rep=self.clock.get_ticks()
        self.response= key_id
        if self.can_respond:
            if key_id == ' ':
                #print('space')
                if self.stage == 'f' or self.intro:
                    self.screen.fill((255,255,255))
                    self.stage= 1
                    self.stim_idx = 0
                    self.current_trial +=1
                    self.last_call= self.clock.get_ticks()
                if self.stage == 'DONE!':
                    self.is_running = False
                if not self.practice and not self.intro:
                    self.trial_seq, self.loc_diff = self.parse_seq(self.stim_seq[self.current_trial-1])
                    self.exp = True

                    
                
            elif key_id == 'r':
                if not self.exp:
                    #repeat practice
                    self.screen.fill((255,255,255))
                    self.exp = False
                    self.practice = True
                    self.current_trial = 0
                    self.stage = 'f'
                    self.stim_idx = 0
                
            elif key_id == self.r_key:
                #print(f'The key is: {self.r_key}')
                self.screen.fill((255,255,255))
                self.correct = not self.loc_diff == 0
                if self.practice:
                    self.log_data(rep)
                    self.stage = 'f'
                    self.display_prompt('feedback')
                    self.trial_seq, self.loc_diff = self.parse_seq(self.stim_seq[self.current_trial])
                else:
                    self.log_data(rep)
                    self.stage = 1
                    self.stim_idx = 0
                    self.current_trial +=1
                    self.last_call= self.clock.get_ticks()
                    self.trial_seq, self.loc_diff = self.parse_seq(self.stim_seq[self.current_trial-1])
                    if self.acc_count == 4:
                        self.lvl_up()
        
                    
        
            elif key_id == self.w_key:
                #print(f'The key is: {self.w_key}')
                self.screen.fill((255,255,255))
                self.correct = self.loc_diff == 0
                if self.practice:
                    self.log_data(rep)
                    self.stage = 'f'
                    self.display_prompt('feedback')
                    self.trial_seq, self.loc_diff = self.parse_seq(self.stim_seq[self.current_trial])
                else:
                    self.log_data(rep)
                    self.stage = 1
                    self.stim_idx = 0
                    self.current_trial +=1
                    self.last_call= self.clock.get_ticks()
                    self.trial_seq, self.loc_diff = self.parse_seq(self.stim_seq[self.current_trial-1])
                    if self.acc_count == 4:
                        self.lvl_up()
                
            pygame.display.flip()
            self.update_trial_state()
            
    def lvl_up(self):
        self.stage = 'f'
        self.lvl +=1
        self.acc_count = 0
        self.stim_seq = self.gen_stim_sequence(self.num_trials_sequence[self.lvl], self.block_size[self.lvl], self.lvl+1)
        self.current_trial -=1 #decrement down to avoid space bar num skip
        #print('lvl up!!!')
    
    def log_data(self,rep):
        if self.correct and self.last_correct:
            self.acc_count +=1
        elif self.correct:
            self.acc_count = 1
        else:
            self.acc_count = 0
        self.last_correct = self.correct
        #print(f'current acc is: {self.acc_count}') #####debug
        if self.practice:
            tt = 'Practice'
        else:
            tt = self.current_trial
        self.get_time = True  
        file = open(f'{self.out_path}AWM_{self.today}_{self.subject}_{self.session}.csv', 'a', newline ='')
        with file:
            header = ['Subject', 'Session', 'Date', 'Time', 'Trial', 'Stimulus', 'Response', 'Correct', 'RT', 'Loc_diff', 'Complexity', 'Rep_Key']
            writer = csv.DictWriter(file, fieldnames = header)
            
            # writing data row-wise into the csv file
            if self.current_trial ==1 and self.practice:
                writer.writeheader()
            writer.writerow({'Subject' : self.subject,
                            'Date' : self.today,
                            'Time' : self.hour,
                            'Session': self.session,
                            'Trial' : tt,
                            'Stimulus' : self.trial_seq,
                            'Response' : self.response,
                            'Correct': self.correct,
                            'RT': rep-self.stim_onset,
                            'Loc_diff': self.loc_diff,
                            'Complexity': self.lvl,
                            'Rep_Key': [self.w_key, self.r_key]})
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
