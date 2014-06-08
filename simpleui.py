import tkinter
import threading
from time import sleep
from functools import partial
import queue

##
##t's important that exceptions in my_method do not cause you to miss registering with the mainloop. You may want to put your call to root.after in the finally part of try/finally.
##[10:31:04 AM] Nieri TV: make incoming command queue for main bookworm object. only need to handle code that might be registered with external threads (e.g. callxyzfromui functions)
##[10:34:19 AM] Nieri TV: can that be made into a feature of the simple ui to handle it with a function that runs the queued commands as part of the main object flow




class SimpleUI:
    '''
    - created and handled within another object
    - dynamically generates interface items in separate areas
        - windows and frames to contain other elements
        - buttons linked to functions
        - text output
        - keypress watchers
    - general default for all functions is to use the root window unless
      otherwise specified
    - internal structure of ui:
        -elements are buttons, text output, etc.
        {window name: {'window':window,
                       'frame name': {'frame':frame,
                                      'element name':element}}}
    '''
    def __init__(self, root_name = 'root', hide = False):
        self._in_q = queue.Queue()
        self._out_q = queue.Queue()
        self._callback_q = queue.Queue()
        self._root_name = root_name
        self.t = threading.Thread(target = self._threadmain)
        self.t.start()
        if hide: self.hide()

    def _threadmain(self, **kwargs):
        def timertick():
            try:
                callable, args, kwargs = self._in_q.get_nowait()
            except queue.Empty:
                pass
            else:
                retval = callable(*args, **kwargs)
                self._out_q.put(retval)
            #re-register this function after completion
            ### get interval from config
            self._ui['windows'][self._root_name].after(100, timertick)
        self._ui = {}
        ui = self._ui
        
        ui['windows'] = {self._root_name: tkinter.Tk()}
        ui['windows'][self._root_name].protocol("WM_DELETE_WINDOW",
                                                self._close_ui)
        ui['frames'] = {}
        ui['buttons'] = {}
        ui['textouts'] = {}
        timertick()
        ui['windows'][self._root_name].mainloop()

    def _submit_to_tkinter(self, callable, *args, **kwargs):
        if self.t.is_alive():
            self._in_q.put((callable, args, kwargs))
            return self._out_q.get()
        else:
            raise RuntimeWarning('UI is already closed but messages are being sent to it.')

    def _queue_callback(self, callable):
        self._callback_q.put(callable)

    def run_external_callbacks(self):
        try:
            while 1:
                callable = self._callback_q.get_nowait()
                callable()
        except queue.Empty: pass

    def is_running(self):
        if self.t.is_alive():
            return True
        else:
            return False

    def show(self, window_name = None):
        self._submit_to_tkinter(self._show, window_name)

    def hide(self, window_name = None):
        self._submit_to_tkinter(self._hide, window_name)

    def add_window(self, name, hidden = False):
        self._submit_to_tkinter(self._add_window, name, hidden)

    def add_frame(self, name, window_name = None):
        self._submit_to_tkinter(self._add_frame, name, window_name)

    def add_textout(self, name, frame_name):
        self._submit_to_tkinter(self._add_textout, name, frame_name)

    def add_button(self, name, b_text, callable, frame_name):
        self._submit_to_tkinter(self._add_button, name, b_text,
                                callable, frame_name)

    def change_text(self, textout_name, new_text):
        self._submit_to_tkinter(self._change_text, textout_name, new_text)

    def close_ui(self):
        try: self._submit_to_tkinter(self._close_ui)
        except RuntimeWarning: pass

    def _close_ui(self):
        self._ui['windows'][self._root_name].destroy()

    def _show(self, window_name):
        window_list = (self._ui['windows'][window_name] if window_name else
                       [window for window in self._ui['windows'].values()] )
        for window in window_list:
            window.update()
            window.deiconify()

    def _hide(self, window_name):
        window_list = (self._ui['windows'][window_name] if window_name else
                       [window for window in self._ui['windows'].values()] )
        for window in window_list:
            window.withdraw()

    def _add_window(self, name, hidden):
        windows = self._ui['windows']
        windows['name'] = tkinter.TopLevel(windows[self._root_name])
        if hidden:
            self.hide(name)

    def _add_frame(self, frame_name, window_name):
        frames = self._ui['frames']
        window = (self._ui['windows'][window_name] if window_name else
                  self._ui['windows'][self._root_name])
        frames[frame_name] = tkinter.Frame(window)
        frames[frame_name].pack()

    def _add_textout(self, name, frame_name):
        textouts = self._ui['textouts']
        frame = self._ui['frames'][frame_name]
        textouts[name] = tkinter.Label(frame)
        textouts[name].pack()

    def _change_text(self, textout_name, new_text):
        self._ui['textouts'][textout_name].config(text = new_text)
        
    def _add_button(self, name, b_text, callable, frame_name):
        buttons = self._ui['buttons']
        frame = self._ui['frames'][frame_name]
        callback = partial(self._queue_callback, callable)
        buttons[name] = tkinter.Button(frame, text = b_text,
                                       command = callback)
        buttons[name].pack()
        
    def window_names(self):
        for window_name in self._ui['windows'].keys():
            yield window_name

    def frame_names(self, window_name):
        for frame_name in self._ui['frames'].keys():
            yield frame_name


def main():
    def button_pressed():
        print('button pressed')
    ui = SimpleUI()
##    input('press key to hide...')
    ui.hide()
##    input('press key to show...')
    ui.show()
##    input('press key to add frame...')
    ui.add_frame('frame1')
##    input('press key to add textout...')
    ui.add_textout('textout1', 'frame1')
##    input('press key to change text...')
    ui.change_text('textout1', 'added text')
##    input('press key to add button...')
    ui.add_button('button1', 'button 1', button_pressed, 'frame1')
    while 1:#input('(Q)uit or any other key to continue').lower() != 'q':
        ui.run_external_callbacks()
        if not ui.is_running():
            break
        sleep(.1)
    ui.close_ui()

if __name__ == '__main__':
    main()
