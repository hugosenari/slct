slct
====

Checkbox pipe comandline



Usage
-----
pipe something to slct with "value description" format
choose what you to output
xargs to execute command with selected values

```bash
git status -s|head -n 10|cut -c4-|python3 slct.py|xargs git add
aptitude search python|cut -c5-|grep "^python3"|head -n 10|python3 src/slct.py
```

Know Bugs
---------
- Input need to be smaller than screen


TO-DO
-----
- Paginate for content greater than screen
- Input format options
- Output format options
- Predefined input options (ie: ps aux, top, find ., grep -r)
