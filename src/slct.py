#! /usr/bin/python3
import curses, sys, tty, os, errno

class cut(object):
    def __init__(self, line, sep=" "):
        self.line = str(line).strip()
        self.sep = sep
        cols = self.line.split(self.sep)
        self.value = cols[0]
        self.descr = ""
        if len(cols) > 1:
            self.descr = self.sep.join(cols[1:])


class cu_widget(object):
    X = 0
    Y = 1
    def __init__(self, content, screen = None, pos = [0, 0]):
        self.height = len(content.split("\n"))
        self.content = content
        self.pos = pos 
        self.screen = screen
        
    def to_screen(self, attr = 0):
        if self.screen:
            SCREEN_HEIGHT, SCREEN_WIDTH = self.screen.getmaxyx()
            i = 0
            for line in self.content.split("\n"):
                line = line[:SCREEN_WIDTH - 1 ]
                if self.pos[cu_widget.Y] + i < SCREEN_HEIGHT:
                    try:
                        self.screen.addstr(self.pos[cu_widget.Y] + i , self.pos[cu_widget.X], " " * (SCREEN_WIDTH-1))
                        self.screen.addstr(self.pos[cu_widget.Y] + i , self.pos[cu_widget.X], line, attr)
                    except:
                        self.log('error')
                i += 1
        return self
    
    def log(self, text, n=0):
        SCREEN_HEIGHT, SCREEN_WIDTH = self.screen.getmaxyx()
        text = str(text)
        text = text.split("\n")[0]
        text = text[:SCREEN_WIDTH - 2]
        blank = " " * (SCREEN_WIDTH - 1)
        self.screen.addstr(SCREEN_HEIGHT -1 - n, 0, blank)
        self.screen.addstr(SCREEN_HEIGHT -1 - n, 0, text)
    
    def __nonzero__(self):
        return True
    
    def __str__(self):
        return self.content
    
    def __len__(self):
        return self.height 
    
    def __add__(self, other):
        return len(self) + len(other) 
    
    def __sub__(self, other):
        return len(self) + len(other)
    
    def __mul__(self, n):
        return self.height * n

    def __lshift__(self, other):
        if hasattr(other, 'pos') and hasattr(other, 'to_screen') and hasattr(other, 'screen'):
            other.pos = [self.pos[cu_widget.X], self.pos[cu_widget.Y] + self.height]
            other.screen = self.screen
            other.to_screen()
        return other
    

class Br(cu_widget):
    FORMAT = "#"
    def __init__(self, width, stdscr=None, pos = [0 , 0]):
        super(Br, self).__init__(Br.FORMAT * width)


class Header(cu_widget):
    FORMAT = "{TITLE}\n{DESCR}"
    def __init__(self, stdscr, title, descr, pos = [0 , 0]):
        super(Header, self).__init__(
        Header.FORMAT.format(TITLE=title, DESCR=descr), stdscr, pos)


class Checkbox(cu_widget):
    CHECKED = "X"
    UNCHECKED = " "
    FORMAT = "[{STATUS}] {VALUE}   {TITLE}"
    XPOS = 1

    def __init__(self, value, title = "", state=False, stdscr=None, pos = [0 , 0]):
        self.state = state
        self.value = value
        self.title = title
        super(Checkbox, self).__init__(Checkbox.FORMAT.format(
            STATUS=Checkbox.CHECKED if state else Checkbox.UNCHECKED,
            VALUE=value,
            TITLE=title
        ), stdscr, pos)
        
    def __nonzero__(self):
        return self.state
    
    def change(self, state=None):
        self.state = not(self.state) if state is None else state 
        self.content = Checkbox.FORMAT.format(
            STATUS=Checkbox.CHECKED if self.state else Checkbox.UNCHECKED,
            VALUE=self.value,
            TITLE=self.title)
        return self
    
    def hover(self):
        self.to_screen(curses.A_BOLD)
        if self.screen:
            self.screen.move(self.pos[cu_widget.Y], Checkbox.XPOS)
        return self
    

class Cu(object):
    def __enter__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak() 
        curses.flushinp()
        self.SCREEN_HEIGHT, self.SCREEN_WIDTH = self.stdscr.getmaxyx()
        self.cursor_pos = 0
        self.header = Header(self.stdscr, "SeLeCT",
        """        Space: (un)check,
        Return: continue
        Q: quit""")
        self.br = Br(self.SCREEN_WIDTH)
        self.content_size = self.SCREEN_HEIGHT - len(self.header) - len(self.br)
        self.showing = {'begin': 0, 'end':0}
        self.lines = []
        self.exit_status = 0
        return self

    def __exit__(self, *args, **dargs):
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    
    def add(self, lines):
        for line in lines:
            if len(line.replace(' ', '')) > 0:
                cutie = cut(line)
                checkbox = Checkbox(cutie.value, cutie.descr, False)
                self.lines.append(checkbox)
        self.list()
        return self

    def list(self, begin=0):
        prev = self.br
        self.showing = {'begin': begin, 'end': self.content_size + begin}
        for checkbox in self.lines[begin:self.content_size + begin]:
            prev << checkbox
            prev = checkbox
        self.update()
        return self
        
    def updown(self, direction = 1):
        line = self.lines[self.cursor_pos]
        line.to_screen()
        self.cursor_pos = self.cursor_pos + direction
        if self.cursor_pos < 0:
            self.cursor_pos = 0
        elif self.cursor_pos >= len(self.lines):
            self.cursor_pos = len(self.lines) - 1
        if self.cursor_pos >= self.showing.get('end'):
            self.list(self.cursor_pos - self.content_size + 1)
        elif self.cursor_pos <= self.showing.get('begin'):
            self.list(self.cursor_pos)

    def checkuncheck(self):
        line = self.lines[self.cursor_pos]
        line.change()
    
    def checkuncheckall(self, status=True):
        for line in self.lines:
            line.change(status)
            line.to_screen()

        
    def allchecked(self, status = True):
        for line in self.lines:
            if line.state == status:
                yield line

    def update(self):
        if len(self.lines):
            line = self.lines[self.cursor_pos]
            line.hover()
        self.stdscr.refresh()
        
    def main(self, npt):
        self.header.to_screen()
        self.header << self.br
        if len(npt) > 0:
            self.add(npt.split("\n"))
        self.update()
        while True:
            cint = self.stdscr.getch()
            c = chr(cint)
            if cint in (curses.KEY_UP, 65) or\
                c.lower() in ('8',):
                self.updown(-1)
            elif cint in (curses.KEY_DOWN, 66) or\
                c.lower() in ('2',):
                self.updown()
            elif cint in (curses.KEY_NPAGE, 53) or\
                c.lower() in ('9',):
                self.updown(- self.content_size)
            elif cint in (curses.KEY_PPAGE, 54) or\
                c.lower() in ('3',):
                self.updown(self.content_size)
            elif cint in (curses.KEY_SELECT
                         , curses.KEY_B2
                         , curses.KEY_MOUSE
                         , 68, 67) or\
                c in (' ', '5', '4', '6', '.'):
                self.checkuncheck()
            elif c.lower() in ('*',):
                self.checkuncheckall()
            elif c.lower() in ('/',):
                self.checkuncheckall(False)
            elif cint in(curses.KEY_ENTER
                         , curses.KEY_RESUME
                         , 10) or\
                c in ('\r',):
                break
            elif c.lower() == 'q':
                self.cancel()
                break
            self.update()

    def log(self, text, n=0):
        SCREEN_HEIGHT, SCREEN_WIDTH = self.stdscr.getmaxyx()
        text = str(text)
        text = text.split("\n")[0]
        text = text[:SCREEN_WIDTH - 2]
        blank = " " * (SCREEN_WIDTH - 1)
        self.stdscr.addstr(SCREEN_HEIGHT -1 - n, 0, blank)
        self.stdscr.addstr(SCREEN_HEIGHT -1 - n, 0, text)
        
    def cancel(self):
        self.exit_status = errno.EPIPE
    
        

if __name__ == "__main__":
    npt = ""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as content:
            npt = content.read()
    else:
        sys.exit(errno.ENOTTY)
        
    allchecked = []
    exit_status = 1
     
    with Cu() as icecream:
        try:
            icecream.main(npt)
        except Exception as e:
            pass
        exit_status = icecream.exit_status
        allchecked = icecream.allchecked()

    if (exit_status > 0):
        sys.exit(icecream.exit_status)

    try:
        with open(sys.argv[2], 'w') as content:
            for line in allchecked:
                content.write(line.value + "\n")
    except:
        for line in allchecked:
            print(line.value)        