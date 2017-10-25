import os, sys, time, getopt, datetime, zipfile
from PIL import Image
from subprocess import call
#from wand.image import Image

results = "NAZEV SOUBORU                        |           VELIKOST          |           PIXELS          |   byte/ pixel      \n"
results2 = "NAZEV SOUBORU                        |           VELIKOST          |           PIXELS          |   byte/ pixel      \n"

DEBUG = 1


def debug(value):
    if DEBUG:
        print value


def read_image(input_file):
    global results
    print input_file + "\n"
    # Analyze image with openjpeg
    base = os.path.basename(input_file)
    name = os.path.splitext(base)[0]
    dirn = os.path.dirname(input_file)
    print dirn
    for x in range(1, 10):
        call(["./opj_compress", "-i", input_file, "-o", dirn+'/compressed/'+name+'_'+str(x)+'.jp2', "-n", str(x)])
    #resolution = 16084992
    #size = os.path.getsize(input_file)*8
    #bytetopixel = int(size)/int(resolution)
    # Dynamic pixels count
    with Image.open(input_file) as img:
        width, height = img.size
    print img.size
    # statistics count TODO
    resolution = width*height
    size = os.path.getsize(input_file)
    # size_all += size
    bytetopixel = float(size) / float(resolution)
    # bytetopixel_all += bytetopixel

    results = results + input_file + " | " + str(size) + "B | " + str(resolution) + "px | " + str(bytetopixel) + "\n"


def count_compress(input_file):
    global results2
    with Image.open(input_file) as img:
        width, height = img.size
    print img.size
    resolution = width * height
    size = os.path.getsize(input_file)
    bytetopixel = float(size) / float(resolution)

    results2 = results2 + input_file + " | " + str(size) + "B | " + str(resolution) + "px | " + str(bytetopixel) + "\n"


def main_parse(input_file, number):
    debug('main_parse | Input file: ' + input_file)
    # IF folder  ---------------------------------------------------------------
    if os.path.isdir(input_file):
        for file_of_folder in os.listdir(input_file):
            debug('main_parse | Is folder: <' + input_file + '> read file: <' + file_of_folder + '>')
            main_parse(input_file + '/' + file_of_folder, number)

    # IF valid image -------------------------------------------------------------------

    elif input_file.endswith(".tif") and number == 1:
        read_image(input_file)

    elif input_file.endswith(".jp2") and number == 2:
        count_compress(input_file)

    # Some mess  -- ignore----------------------------------------------------------------
    else:
        debug("File:" + input_file + " - ignored ")

    return 0


#### TEST
# main_parse(sys.argv[1])


main_parse('datasets', 1)
main_parse('datasets', 2)

with open('results.txt', 'w') as f:
    f.write(results)

with open('results2.txt', 'w') as f:
    f.write(results2)
