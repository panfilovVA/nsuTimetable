import re
import time


def follow_file(file):
    file.seek(0, 2)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def parse_file(cnt):
    filename = "D:/Projects/out.txt"
    f = open(filename, "r+")
    lines = f.readlines()
    f.close()
    res = []
    for line in lines:
        line = line.strip()
        line = line.replace("[", "")
        line = line.replace("]", "")

        pattern = re.compile(r"""schedule\(subject\((?P<SID>.*?),(?P<SName>.*?)\),(?P<LType>.*?),teacher\((?P<TID>.*?),(?P<TName>.*?)\),room\((?P<RId>.*?),(?P<RSize>.*?),(?P<RType>.*?)\),group\((?P<GID>.*?),(?P<GSize>.*?)\),(?P<WeekDay>.*?),(?P<Lesson>.*?)\)""", re.VERBOSE)

        lessons = re.findall(pattern, line)
        if len(lessons) == cnt:
            res.append(lessons)
    return res
