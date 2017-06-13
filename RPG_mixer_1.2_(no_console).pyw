#!/usr/bin/env python3

# Xeus RPG mixer
# version 1.2
#
# 1. Description
#
#     The purpose of this application is to enhance every RPG session with easy management of sound samples.
#  With this script a game master is able to easily and quickly use sounds like howling of wolves, singing
#  of birds or flowing river and, thus, aid his or her narration. You can mix up up to 15 different samples
#  which can be played at the same time. The application allows to create keboard shortcuts to each used
#  sample and adjust the volume of each sound independently.
#
# 2. Requirements
#
#     The script requires python3 (version 3.1) and pygame (version 1.9.1). It was written with those versions
#  and probably (!) will work with newer versions, but it does not have to.
#
# 3. License
#
#     This script is licensed under the GNU General Public License version 3 from 29 June 2007.
#  You can find the full text of the license here: http://opensource.org/licenses/GPL-3.0

import pygame, os, sys
from pygame.locals import *
from tkinter import *
from tkinter import messagebox, filedialog

pygame.init()
pygame.mixer.init()

class verticalScrolledFrame(Frame):
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=TRUE)
        canvas = Canvas(self, bd=0, highlightthickness=0, height = 600, yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)        
        vscrollbar.config(command=canvas.yview)
        
        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        
        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW)
        
        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)
        
        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

class soundBox(LabelFrame):
    def __init__(self, master = None, _text = "Sound"):
        LabelFrame.__init__(self, master, text = _text, padx = 5)
        
        # variables
        self.name = StringVar(master)
        self.name.set("Choose file")
        self.loop = IntVar(master)
        self.sound = None
        self.keyBind = StringVar()
        
        # frame that manages a sound
        frame_sound = Frame(self, borderwidth = 1, relief = RIDGE)
        
        button_chooseFile = Button(frame_sound, textvariable = self.name, width = 25, command = self.choose_file)
        checkBox_loop = Checkbutton(frame_sound, text = "Loop", variable = self.loop)
        button_play = Button(frame_sound, text = "\u25B6", width = 5, command = self.play)
        button_stop = Button(frame_sound, text = "\u25A0", width = 5, command = self.stop)
        
        button_chooseFile.grid(row = 0, column = 0, columnspan = 3, sticky = W+E)
        checkBox_loop.grid(row = 1, column = 0)
        button_play.grid(row = 1, column = 1, sticky = W+E)
        button_stop.grid(row = 1, column = 2, sticky = W+E)
        
        # frame that manages the keyboard shortcut for playing the sound
        frame_shortcut = Frame(self)
        
        label_shortcut = Label(frame_shortcut, text = "Shortcut: ")
        entry_keyBind = Entry(frame_shortcut, textvariable = self.keyBind, width = 1, font = ("Courier", 12, "bold"))
        button_keyBind = Button(frame_shortcut, text = "\u2713", command = self.apply_shortcut)
        
        label_shortcut.grid(row = 0, column = 0, padx = 5)
        entry_keyBind.grid(row = 0, column = 1, padx = 5)
        button_keyBind.grid(row = 0, column = 2, padx = 5)
        
        # frame with volume slider
        labelFrame_volume = LabelFrame(self, text = "Volume")
        
        scale_volume = Scale(labelFrame_volume, from_ = 10, to = 0, orient = VERTICAL, length = 70, command = self.apply_volume)        
        scale_volume.set(10)
        
        scale_volume.grid(row = 0, column = 0, rowspan = 4)
        
        # main geography
        frame_sound.grid(row = 0, column = 0)
        frame_shortcut.grid(row = 1, column = 0)
        labelFrame_volume.grid(row = 0, column = 1, rowspan = 2, sticky = N+S+W+E, padx = 5, pady = 5)
    
    def play(self, value = None):
        if self.sound != None:
            
            if self.loop.get() == 0:
                self.sound.play(0)
            
            elif self.loop.get() == 1:
                self.sound.play(-1)
    
    def stop(self):
        if self.sound != None:
            self.sound.stop()
    
    def choose_file(self):
        path = filedialog.askopenfilename(filetypes = [("Sounds", "*.wav;*.ogg")], title = "Open sound")
        head, tail = os.path.split(path)
        self.name.set(tail)
        try:            
            self.sound = pygame.mixer.Sound(path)
        except error:
            messagebox.showerror(message = "The sound file is incorrect!")
        self.focus_set()
    
    def apply_volume(self, value):
        if self.sound != None:
            self.sound.set_volume(float(value) / 10)
    
    def apply_shortcut(self):
        bind = self.keyBind.get()
        if (bind != "") and (bind.__len__() == 1):
            self.bind_all(bind, self.play)
        else:
            if bind == "":
                messagebox.showwarning("Wrong shortcut!", "You have not entered a character for a shortcut.")
            elif bind.__len__() > 1:
                messagebox.showwarning("Wrong shortcut!", "Check if you entered just ONE character in the shortcut field.")
            self.keyBind.set("")
        self.focus_set()

class application(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.resizable(width = False, height = False)
        
        self.mainFrame = verticalScrolledFrame(self)
        self.mainFrame.pack(fill = Y)
        
        self.soundboxes = []
        
        for i in range(15):
            text = "Sound " + str(i + 1)
            self.soundboxes.append(soundBox(self.mainFrame.interior, text))
            self.soundboxes[-1].pack()

if __name__ == '__main__':
    RPG_mixer = application()
    RPG_mixer.title("RPG Mixer - v1.2")
    RPG_mixer.mainloop()
