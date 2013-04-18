slct
====

Checkbox for pipe comandline



Usage
-----
Pipe something to slctp with "value description" format.

Choose what values you want to output.

Pipe your result to another command.


```bash
git clone git://github.com/hugosenari/slct.git
cd slct/src
cat text.txt
cat text.txt|./slctp
cat text.txt|./slctp|xargs echo
./slct.py text.txt
./slct.py text.txt output.txt
```

Know Bugs
---------
- You can't use Esc to Quit


TO-DO
-----
- Input format options
- Output format options
- Predefined input options (ie: ps aux, top, find ., grep -r, git status -s)
- User config defined input options (~/.slct.d/userFormat)