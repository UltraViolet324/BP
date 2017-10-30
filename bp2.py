#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on 2017-10-22

@author: Lucie Vrtelova (xvrtel00@stud.fit.vutbr.cz)
"""
import os
import sys
import csv
import scipy.misc
import numpy
from io import StringIO
# import time
# from datetime import datetime
from argparse import ArgumentParser
from PIL import Image
import subprocess
from subprocess import run
import psnr
import matplotlib.pyplot as plt



results = []
results2 = []
results3 = []
size_values = []
psnr_values = []
quality_values = []
size_values2 = []
psnr_values2 = []

results.append(['Nazev souboru', 'Velikost', 'Pixely', 'Bit/Pixel'])
results2.append(['Nazev souboru', 'Velikost', 'Pixely', 'Bit/Pixel'])
results3.append(['Nazev souboru', 'Velikost', 'Pixely', 'Bit/Pixel', 'PSNR'])

exit_failure = 1
DEBUG = 1


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
        "-t", "--tile",
        dest="tile",
        help="size of tile",
        metavar="TILE")
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

    compress_openjpeg = Compress_openjpeg()
    compress_openjpeg.tile = args.tile

    if args.openjpeg:
        compress_openjpeg.main_parse(args.input, 1)
        compress_openjpeg.main_parse(args.input, 2)
        compress_openjpeg.main_parse(args.input, 3)
        compress_openjpeg.write_to_csv(results, 'results1')
        compress_openjpeg.write_to_csv(results2, 'res2')
        compress_openjpeg.write_to_csv(results3, 'res3')
        compress_openjpeg.psnr_compare(quality_values, psnr_values, size_values)
        compress_openjpeg.psnr_compare2(quality_values, psnr_values2, size_values2)


class Compress_openjpeg:

    def __init__(self):
        self.tile = ''
        self.nr_res = ''
        self.dirn = ''
        self.path = ''
        self.name = ''
        self.folder = ''
        self.ref = ''
        self.dist = ''
        self.dire = ''
        self.dirn2 = ''
        self.name2 = ''
        self.folder2 = ''



    def read_image(self, input_file):
        global results
        #print(input_file + "\n")
        # Analyze image with openjpeg
        base = os.path.basename(input_file)
        self.name = os.path.splitext(base)[0]
        self.folder = os.path.dirname(input_file).split('/')[1]
        print(self.folder)
        self.dirn = os.path.dirname(input_file)
        ref_file = input_file

        self.ref = scipy.misc.imread(ref_file, flatten=True).astype(numpy.float32)

        for self.nr_res in range(1, 11, 1):
            path = self.prepare_folder(self.nr_res)
            print(path)
            dist_file = path
            with open('time_' + self.folder + '-' + self.tile + '-' + str(self.nr_res) + '_c.txt', 'a') as f:
                run(["/usr/bin/time", "-f", "%U", "./opj_compress", "-i", input_file, "-o", path, "-r", "1", "-n", str(self.nr_res), "-t", self.tile], stderr=f)

            quality_values.append(self.nr_res)

            file_size = os.path.getsize(dist_file)

            dist = scipy.misc.imread(dist_file, flatten=True).astype(numpy.float32)

            size_values2.append(int(file_size / 1024))
            psnr_values2.append(psnr.psnr(self.ref, dist))

        # Dynamic pixels count
        with Image.open(input_file) as img:
            width, height = img.size
        # statistics count TODO
        resolution = width * height
        size = os.path.getsize(input_file)
        bytetopixel = float(size) / float(resolution)

        results.append([input_file, str(size) + 'B', str(resolution) + 'px', str(bytetopixel)])

    def read_image2(self, input_file):
        global results
        base2 = os.path.basename(input_file)
        self.name2 = os.path.splitext(base2)[0]
        self.dirn2 = os.path.dirname(input_file)
        nr = base2.split('-')[1]
        nrnr = nr.split('.')[0]
        print(nrnr)

        path = input_file
        print(path)
        path2 = self.prepare_folder2(nrnr)
        print(path2)
        dist_file = path2

        with open('time_' + self.folder + '_' + self.tile + '-' + str(nrnr) + '_d.txt', 'a') as f:
            run(["/usr/bin/time", "-f", "%U", "./opj_decompress", "-i", path, "-o", path2], stderr=f)

        file_size = os.path.getsize(dist_file)

        dist = scipy.misc.imread(dist_file, flatten=True).astype(numpy.float32)

        size_values.append(int(file_size / 1024))
        psnr_values.append(psnr.psnr(self.ref, dist))

        print(psnr_values)

        with Image.open(input_file) as img:
            width, height = img.size
        # statistics count TODO
        resolution = width * height
        size = os.path.getsize(input_file)
        bytetopixel = float(size) / float(resolution)

        results.append([input_file, str(size) + 'B', str(resolution) + 'px', str(bytetopixel)])

    def prepare_folder(self, nr_res):
        """
        Ensures that temporary directory and file exists and is writable.
        Returns name of temporary file.
        """

        self.path = self.dirn + '/compressed/' + self.tile + '_' + str(self.nr_res) + '/' + self.name + '_' + self.tile + '-' + str(nr_res) + '.jp2'

        try:
            if not os.path.exists(self.dirn + '/compressed/' + self.tile + '_' + str(self.nr_res)):
                os.makedirs(self.dirn + '/compressed/' + self.tile + '_' + str(self.nr_res))  # decimal equivalent of 0755 used on Windows
        except IOError as e:
            print(
                "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
            sys.exit()

        return self.path

    def prepare_folder2(self, nr_res):
        """
        Ensures that temporary directory and file exists and is writable.
        Returns name of temporary file.
        """

        self.path = self.dirn + '/decompressed/' + self.tile + '_' + str(nr_res) + '/' + self.name2 + '.tif'

        try:
            if not os.path.exists(self.dirn + '/decompressed/' + self.tile + '_' + str(nr_res)):
                os.makedirs(self.dirn + '/decompressed/' + self.tile + '_' + str(nr_res))  # decimal equivalent of 0755 used on Windows
        except IOError as e:
            print(
                "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
            sys.exit()

        return self.path

    def count_compress(self, input_file):
        global results2
        with Image.open(input_file) as img:
            width, height = img.size
        #print(img.size)
        resolution = width * height
        size = os.path.getsize(input_file)
        bytetopixel = float(size) / float(resolution)
        count = len(psnr_values2)
        for x in range(1, count, 1):
            psnr_pr = psnr_values2[x]

        results2.append([input_file, str(size) + 'B', str(resolution) + 'px', str(bytetopixel), psnr_pr])

    def count_compress2(self, input_file):
        global results3
        with Image.open(input_file) as img:
            width, height = img.size
        #print(img.size)
        print(input_file)
        resolution = width * height
        size = os.path.getsize(input_file)
        bytetopixel = float(size) / float(resolution)
        count = len(psnr_values)
        for x in range(1, count, 1):
            psnr_pr = psnr_values[x]

        results3.append([input_file, str(size) + 'B', str(resolution) + 'px', str(bytetopixel), psnr_pr])

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
            self.read_image2(input_file)

        elif input_file.endswith(".tif") and number == 3:
            self.count_compress2(input_file)

        # Some mess  -- ignore----------------------------------------------------------------
        else:
            debug("File:" + input_file + " - ignored ")

    def write_to_csv(self, text, filename):
        with open(filename+'.csv', "w") as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerows(text)

    def psnr_compare(self, nr_res, psnr_values, size_values):

        plt.figure(figsize=(8, 8))

        plt.plot(nr_res, numpy.asarray(psnr_values) / 100.0, 'ro', label='PSNR/100')
        plt.legend(loc='lower right')
        plt.xlabel('JPEG Quality')
        plt.ylabel('Metric')
        plt.savefig('jpg_demo_quality.png')

        plt.figure(figsize=(8, 8))

        plt.plot(size_values, numpy.asarray(psnr_values) / 100.0, label='PSNR/100')
        plt.legend(loc='lower right')
        plt.xlabel('JPEG File Size, KB')
        plt.ylabel('Metric')
        plt.savefig('jpg_demo_size.png')

    def psnr_compare2(self, nr_res, psnr_values, size_values):

        plt.figure(figsize=(8, 8))

        plt.plot(nr_res, numpy.asarray(psnr_values) / 100.0, 'ro', label='PSNR/100')
        plt.legend(loc='lower right')
        plt.xlabel('JPEG Quality')
        plt.ylabel('Metric')
        plt.savefig('jpg_demo_quality2.png')

        plt.figure(figsize=(8, 8))

        plt.plot(size_values, numpy.asarray(psnr_values) / 100.0, label='PSNR/100')
        plt.legend(loc='lower right')
        plt.xlabel('JPEG File Size, KB')
        plt.ylabel('Metric')
        plt.savefig('jpg_demo_size2.png')


if __name__ == "__main__":
    main()
