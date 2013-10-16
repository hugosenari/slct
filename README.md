slct
====

Select for pipe comandline



Usage
-----
Pipe something to slctp with "value description" format.

Choose what values you want to output.

Pipe your result to another command.


Examples:
---------

```bash
git clone git://github.com/hugosenari/slct.git
cd slct/src

#Working with file:

#read content of in_file, output first col (separated by space) to stdout
./slct.py text.txt

#read content of in_file, output second col (separated by space) to stdout
./slct.py text.txt 1

#read content of in_file, output first col (separated by - ) to stdout
./slct.py text1.txt 0 "-"

#read content of in_file, output second col (separated by - ) to out_file
./slct.py text1.txt 1 "-" out_file


#Working with stdin:*

#read content of stdin and apply slct.py #1 example
cat text.txt|./slctp

#read content of stdin and apply slct.py #2 example
cat text.txt|./slctp 1

#read content of stdin and apply slct.py #3 exmaple
cat text1.txt|./slctp 0 "-"

#read content of stdin and apply slct.py #4 exmaple
cat text1.txt|./slctp 1 "-" > out_file
```


More Examples:
--------------

```bash
# select packages
apt-cache search python|./slctp

# select process id
ps ax|./slctp
ps aux|./slctp 1 "\s+"

# kill selected process
ps aux|./slctp 1 "\s+"|xargs kill

# select git changes
git status -s|./slctp 1
```


Installation:
-------------

Copy 'slct.py' and 'slctp' to somewhere in your $PATH


Know Bugs
---------
- You can't use Esc to Quit


TO-DO
-----
- Output format options
- Predefined input options (ie: ps aux, top, find ., grep -r, git status -s)
- User config defined input options (~/.slct.d/userFormat)
