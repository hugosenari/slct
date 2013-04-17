slct
====

Checkbox pipe comandline



Usage
-----
Pipe something to slctp with "value description" format
choose what values you want to output
do

```bash
git clone git://github.com/hugosenari/slct.git
cd slct/src
cat text.txt
cat text.txt|./slctp
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