#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on 2017-10-22

@author: Lucie Vrtelova (xvrtel00@stud.fit.vutbr.cz)
"""
import os
import sys
import csv
from io import StringIO
# import time
# from datetime import datetime
from argparse import ArgumentParser
from PIL import Image
import subprocess
from subprocess import run
import imgcmp

results = []
results2 = []

results.append(['Nazev souboru', 'Velikost', 'Pixely', 'Bit/Pixel'])
results2.append(['Nazev souboru', 'Velikost', 'Pixely', 'Bit/Pixel'])


exit_failure = 1
DEBUG = 0


def debug(value):
    if DEBUG:
        print(value)


def main():
    """
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-k", "--kakadu",
        help="kakadu library",
        action="store_true")
    parser.add_argument(
        "-j", "--openjpeg",
        dest="openjpeg",
        help="openjpeg2000 library",
        action="store_true")
    parser.add_argument(
        "-c", "--compress",
        help="compress",
        dest="compress",
        action="store_true")
    parser.add_argument(
        "-d", "--decompress",
        help="decompress",
        dest="decompress",
        action="store_true")
    parser.add_argument(
        "-i", "--input",
        dest="input",
        help="path file",
        metavar="INPUT")
    parser.add_argument(
        "-o", "--output",
        dest="output",
        help="output file",
        metavar="OUTPUT")

    args = parser.parse_args()

    error_message = ""
    if args.openjpeg and not args.input:
        error_message += "Input file is missing.\n"
    if args.openjpeg and not args.output:
        error_message += "Output file is missing.\n"
    if len(error_message) > 0:
        error_message += "Some arguments are not set. Please run with -h/--help\n"
        print(error_message)
        sys.exit(exit_failure)

    compress = Compress()
    if args.compress:
        compress.main_parse(args.input, 1)
        compress.main_parse(args.input, 2)
        compress.write_to_csv(results, 'results1')
        compress.write_to_csv(results2, 'res2')
    decompress = Decompress()
    decompress.main_parse(args.input)


class Compress:

    def read_image(self, input_file):
        global results
        #print(input_file + "\n")
        # Analyze image with openjpeg
        base = os.path.basename(input_file)
        name = os.path.splitext(base)[0]
        dirn = os.path.dirname(input_file)
        #print(dirn)
        #print(input_file)

        for x in range(0, 10):
            with open('out-file.txt', 'a') as f:
                run(["/usr/bin/time", "-f", "%U", "./opj_compress", "-i", input_file, "-o", dirn + '/compressed/' + name + '_' + str(x) + '.jp2', "-r", "1", "-n", str(x), "-t", "4096, 4096"], stderr=f)
        path, dirs, files = os.walk(dirn + "/compressed").next()
        file_count = len(files)
        print(file_count)
        # resolution = 16084992
        # size = os.path.getsize(input_file)*8
        # bytetopixel = int(size)/int(resolution)
        # Dynamic pixels count
        with Image.open(input_file) as img:
            width, height = img.size
        #print(img.size)
        # statistics count TODO
        resolution = width * height
        size = os.path.getsize(input_file)
        # size_all += size
        bytetopixel = float(size) / float(resolution)
        # bytetopixel_all += bytetopixel

        results.append([input_file, str(size) + 'B', str(resolution) + 'px', str(bytetopixel)])

    def count_compress(self, input_file):
        global results2
        with Image.open(input_file) as img:
            width, height = img.size
        #print(img.size)
        resolution = width * height
        size = os.path.getsize(input_file)
        bytetopixel = float(size) / float(resolution)

        results2.append([input_file, str(size) + 'B', str(resolution) + 'px', str(bytetopixel)])

    def main_parse(self, input_file, number):
        debug('main_parse | Input file: ' + input_file)
        # IF folder  ---------------------------------------------------------------
        if os.path.isdir(input_file):
            for file_of_folder in os.listdir(input_file):
                debug('main_parse | Is folder: <' + input_file + '> read file: <' + file_of_folder + '>')
                self.main_parse(input_file + '/' + file_of_folder, number)

        # IF valid image -------------------------------------------------------------------

        elif input_file.endswith(".tif") and number == 1:
            self.read_image(input_file)

        elif input_file.endswith(".jp2") and number == 2:
            self.count_compress(input_file)

        # Some mess  -- ignore----------------------------------------------------------------
        else:
            debug("File:" + input_file + " - ignored ")

    def write_to_csv(self, text, filename):
        with open(filename+'.csv', "w") as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerows(text)

class Decompress:

    def read_image(self, input_file):
        global results
        #print(input_file + "\n")
        # Analyze image with openjpeg
        base = os.path.basename(input_file)
        name = os.path.splitext(base)[0]
        dirn = os.path.dirname(input_file)
        #print(dirn)
        #print(input_file)

        path, dirs, files = os.walk(dirn+"/compressed").next()
        file_count = len(files)
        print(file_count)
        for x in range(0, file_count):
            with open('out-file.txt', 'a') as f:
                run(["/usr/bin/time", "-f", "%U", "./opj_decompress", "-i", input_file, "-o", dirn + '/decompressed/' + name + '.jp2'], stderr=f)

        # resolution = 16084992
        # size = os.path.getsize(input_file)*8
        # bytetopixel = int(size)/int(resolution)
        # Dynamic pixels count
        with Image.open(input_file) as img:
            width, height = img.size
        #print(img.size)
        # statistics count TODO
        resolution = width * height
        size = os.path.getsize(input_file)
        # size_all += size
        bytetopixel = float(size) / float(resolution)
        # bytetopixel_all += bytetopixel

        results.append([input_file, str(size) + 'B', str(resolution) + 'px', str(bytetopixel)])

    def count_compress(self, input_file):
        global results2
        with Image.open(input_file) as img:
            width, height = img.size
        #print(img.size)
        resolution = width * height
        size = os.path.getsize(input_file)
        bytetopixel = float(size) / float(resolution)

        results2.append([input_file, str(size) + 'B', str(resolution) + 'px', str(bytetopixel)])

    def main_parse(self, input_file):
        debug('main_parse | Input file: ' + input_file)
        # IF folder  ---------------------------------------------------------------
        if os.path.isdir(input_file):
            for file_of_folder in os.listdir(input_file):
                debug('main_parse | Is folder: <' + input_file + '> read file: <' + file_of_folder + '>')
                self.main_parse(input_file + '/' + file_of_folder)

        # IF valid image -------------------------------------------------------------------

        elif input_file.endswith(".jp2"):
            self.count_compress(input_file)

        # Some mess  -- ignore----------------------------------------------------------------
        else:
            debug("File:" + input_file + " - ignored ")

    def write_to_csv(self, text, filename):
        with open(filename+'.csv', "w") as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerows(text)


if __name__ == "__main__":
    main()
