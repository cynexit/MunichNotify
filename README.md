# MunichNotify
If you live in the city of Munich (Germany) you might have noticed that by now you need to book appointments with the citizens’ bureau online. No matter if you need a new passport or want to register a car, you have to pray that there is a convenient appointment open which is almost impossible within the next two months.

However, many people cancel or move their appointments and slots might open up randomly from time to time. This script can notify you if that is the case so you can snatch that sexy appointment straight away.


## Setup

This script is written for Python 3 and shouldn’t require any non-standard packages besides `requests`. Just `git clone` or download all files into a folder, then:

1) Adjust the `config.py.example` file to your needs, set dates and services
2) Rename it to `config.py`
3) Run `python3 main.py`
4) Done


## Cron

If you want to run the script periodically just use cron, add it using `crontab -e`:

```
*/10 * * * * /path/to/MunichNotify/main.py
```

This example checks for new appointments every ten minutes. Make sure `chmod +x main.py` is set.


## FAQ

Q: Why is there no functionality to instantly reserve a time slot?  
A: Because there is too much potential for abuse. It’s easy to add to this script, but I would ask you not to do it.

Q: I don’t know shit about running Python scripts.  
A: Congrats that you even got here! It’s easier than you think, just search for e.g. “python3 windows beginners guides”.

Q: I don’t have a Linux server ready. :(  
A: You can host this on uberspace.de for as low as one euro a month.
