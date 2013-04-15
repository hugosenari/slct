#! /usr/bin/python
import curses, sys, tty, os, errno

class cut(object):
    def __init__(self, line, sep=" "):
        self.line = str(line).strip()
        self.sep = sep
        cols = self.line.split(self.sep)
        self.value = cols[0]
        self.descr = ""
        if len(cols) > 1:
            self.descr = self.sep.join(cols[1:-1])


class cu_widget(object):
    X = 0
    Y = 1
    def __init__(self, content, screen = None, pos = [0, 0]):
        self.height = len(content.split("\n"))
        self.content = content
        self.pos = pos 
        self.screen = screen
        
    def to_screen(self, attr = 0):
        SCREEN_HEIGHT, SCREEN_WIDTH = self.screen.getmaxyx()
        i = 0
        for line in self.content.split("\n"):
            line = line if len(line) > SCREEN_WIDTH else line[:SCREEN_WIDTH]
            if self.pos[cu_widget.Y] + i < SCREEN_HEIGHT: 
                self.screen.addstr(self.pos[cu_widget.Y] + i , self.pos[cu_widget.X], line, attr)
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
    FORMAT = "[{STATUS}] {VALUE} - {TITLE}"
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


class Cu(object):
    def __enter__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak() 
        curses.flushinp()
        self.SCREEN_HEIGHT, self.SCREEN_WIDTH = self.stdscr.getmaxyx()
        self.cursor_pos = 0
        self.header = Header(self.stdscr, "SeLeCT",
        """
        ## Space: (un)check,
        ## U: move cursor up
        ## D: move cursor down
        ## Return: continue
        ## A: select all
        ## N: select none
        ## Q: quit
        """)
        self.br = Br(self.SCREEN_WIDTH)
        self.lines = []
        self.exit_status = 0
        return self

    def __exit__(self, *args, **dargs):
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def list(self, lines):
        self.stdscr.addstr(str(len(lines)))
        prev = self.br
        for line in lines:
            if len(line.replace(' ', '')) > 0:
                cutie = cut(line)
                checkbox = Checkbox(cutie.value, cutie.descr, False)
                self.lines.append(checkbox) 
                prev << checkbox
                prev = checkbox
        line = self.lines[self.cursor_pos]
        line.to_screen(curses.A_BOLD)            
        self.stdscr.move(self.header + self.br + self.cursor_pos, Checkbox.XPOS) 
        
    def updown(self, direction = 1):
        line = self.lines[self.cursor_pos]
        line.to_screen()
        self.cursor_pos = self.cursor_pos + direction
        if self.cursor_pos < 0:
            self.cursor_pos = 0
        elif self.cursor_pos >= len(self.lines):
            self.cursor_pos = len(self.lines) - 1
        line = self.lines[self.cursor_pos]
        line.to_screen(curses.A_BOLD)
        self.stdscr.move(self.header + self.br + self.cursor_pos, Checkbox.XPOS)
            
    def checkuncheck(self):
        line = self.lines[self.cursor_pos]
        line.change().to_screen(curses.A_BOLD)
        self.stdscr.move(self.header + self.br + self.cursor_pos, Checkbox.XPOS)
        self.update()
    
    def checkuncheckall(self, status=True):
        for line in self.lines:
            line.change(status).to_screen()
        self.update()
        
    def allchecked(self, status = True):
        for line in self.lines:
            if line.state == status:
                yield line

    def update(self):
        self.stdscr.refresh()
        
    def main(self, npt):
        self.header.to_screen()
        self.header << self.br
        if len(npt) > 0:
            self.list(npt.split("\n"))
            
        while True:
            self.update()
            cbin = self.getch()
            c = cbin.decode("utf-8")
            if c.lower() == 'q':
                self.quit()
                break
            elif c == '\r': break
            elif c == ' ': self.checkuncheck()
            elif c.lower() == 'a': self.checkuncheckall()
            elif c.lower() == 'n': self.checkuncheckall(False)
            elif c.lower() == 'u': self.updown(-1)
            elif c.lower() == 'd': self.updown()

    def getch(self):
        fd = sys.stdin.fileno()
        tty_mode = tty.tcgetattr(fd)
        tty.setcbreak(fd)
        ch = b'-1'
        try:
            ch = os.read(fd, 1)
        finally:
            tty.tcsetattr(fd, tty.TCSAFLUSH, tty_mode)
        return ch

    def log(self, text, n=0):
        SCREEN_HEIGHT, SCREEN_WIDTH = self.stdscr.getmaxyx()
        text = str(text)
        text = text.split("\n")[0]
        text = text[:SCREEN_WIDTH - 2]
        blank = " " * (SCREEN_WIDTH - 1)
        self.stdscr.addstr(SCREEN_HEIGHT -1 - n, 0, blank)
        self.stdscr.addstr(SCREEN_HEIGHT -1 - n, 0, text)
        
    def quit(self):
        self.exit_status = errno.EPIPE
    
        

if __name__ == "__main__":
    npt = sys.stdin.read()
    sys.stdin = open('/dev/tty', 'r')
    allchecked = []        
    with Cu() as icecream:
        icecream.main(npt)
        allchecked = icecream.allchecked()
    if (icecream.exit_status > 0):
        sys.exit(icecream.exit_status)
    else:
        for line in allchecked:
            print(str(line.value))
