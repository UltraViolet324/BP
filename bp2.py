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
results2_b = []
results3_b = []
size_values = []
psnr_values = []
quality_values = []
size_values2 = []
psnr_values2 = []
size_values2_b = []
psnr_values2_b = []
size_values_b = []
psnr_values_b = []

results.append(['Nazev souboru', 'Velikost', 'Pixely', 'Bit/Pixel'])
results2.append(['Nazev souboru', 'Velikost', 'Pixely', 'Bit/Pixel', 'PSNR', 'TIME'])
results3.append(['Nazev souboru', 'Velikost', 'Pixely', 'Bit/Pixel', 'PSNR', 'TIME'])
results2_b.append(['Nazev souboru', 'Velikost', 'Pixely', 'Bit/Pixel', 'PSNR', 'TIME'])
results3_b.append(['Nazev souboru', 'Velikost', 'Pixely', 'Bit/Pixel', 'PSNR', 'TIME'])

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
    if not args.input:
        error_message += "Input file is missing.\n"
    elif not args.output:
        error_message += "Output file is missing.\n"
    if len(error_message) > 0:
        error_message += "Some arguments are not set. Please run with -h/--help\n"
        print(error_message)
        sys.exit(exit_failure)

    compress_openjpeg = Compress_openjpeg()
    compress_kakadu = Compress_kakadu()

    compress_openjpeg.main_parse(args.input)
    compress_openjpeg.write_to_csv(results, 'before')
    compress_openjpeg.write_to_csv(results2, 'compressed')
    compress_openjpeg.write_to_csv(results3, 'decompressed')
    compress_openjpeg.write_to_csv(results2_b, 'compressed_b')
    compress_openjpeg.write_to_csv(results3_b, 'decompressed_b')
    #compress_openjpeg.psnr_compare(quality_values, psnr_values, size_values)
    #compress_openjpeg.psnr_compare2(quality_values, psnr_values2, size_values2)

    #compress_kakadu.main_parse(args.input, 1)
    #compress_kakadu.main_parse(args.input, 2)
    #compress_kakadu.main_parse(args.input, 3)
    #compress_kakadu.write_to_csv(results, 'results1')
    #compress_kakadu.write_to_csv(results2, 'res2')
    #compress_kakadu.write_to_csv(results3, 'res3')
    #compress_kakadu.psnr_compare(quality_values, psnr_values, size_values)
    #compress_kakadu.psnr_compare2(quality_values, psnr_values2, size_values2)


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
        usertime = []

        self.ref = scipy.misc.imread(ref_file, flatten=True).astype(numpy.float32)

        for bypass in range(0, 2, 1):
            for self.tile in range(1024, 1025, 1024):
                for self.nr_res in range(1, 3, 1):
                    if bypass == 0:
                        path = self.prepare_folder(self.nr_res, bypass)
                        print(path)
                        dist_file = path
                        with open('time_compressed_OJ.txt', 'w') as f:
                            run(["/usr/bin/time", "-f", "%U", "./opj_compress", "-i", input_file, "-o", path, "-r", "1", "-n", str(self.nr_res), "-t", str(self.tile) + ',' + str(self.tile), "-b", "64,64", "-p", "RPCL"], stderr=f)
                        file = open('time_compressed_OJ.txt', 'r')
                        time = file.read()

                        quality_values.append(self.nr_res)

                        file_size = os.path.getsize(dist_file)

                        dist = scipy.misc.imread(dist_file, flatten=True).astype(numpy.float32)

                        size_values2.append(int(file_size / 1024))
                        psnr_values2.append(psnr.psnr(self.ref, dist))
                        self.count_compress(path, time, psnr_values2[-1:], bypass)

                        base2 = os.path.basename(path)
                        self.name2 = os.path.splitext(base2)[0]
                        self.dirn2 = os.path.dirname(path)

                        path2 = self.prepare_folder2(self.nr_res, bypass)
                        print(path2)
                        dist_file = path2

                        with open('time_decompressed_OJ.txt', 'w') as f:
                            run(["/usr/bin/time", "-f", "%U", "./opj_decompress", "-i", path, "-o", path2], stderr=f)
                        file = open('time_decompressed_OJ.txt', 'r')
                        time = file.read()

                        file_size = os.path.getsize(dist_file)

                        dist = scipy.misc.imread(dist_file, flatten=True).astype(numpy.float32)

                        size_values.append(int(file_size / 1024))
                        psnr_values.append(psnr.psnr(self.ref, dist))
                        self.count_decompress(path, time, psnr_values[-1:], bypass)
                    else:
                        path = self.prepare_folder(self.nr_res, bypass)
                        print(path)
                        dist_file = path
                        with open('time_compressed_OJ_B.txt', 'w') as f:
                            run(["/usr/bin/time", "-f", "%U", "./opj_compress", "-i", input_file, "-o", path, "-r", "1",
                                 "-n", str(self.nr_res), "-t", str(self.tile) + ',' + str(self.tile), "-b", "64,64",
                                 "-p", "RPCL", "-M", "1"], stderr=f)
                        file = open('time_compressed_OJ_B.txt', 'r')
                        time = file.read()

                        quality_values.append(self.nr_res)

                        file_size = os.path.getsize(dist_file)

                        dist = scipy.misc.imread(dist_file, flatten=True).astype(numpy.float32)

                        size_values2_b.append(int(file_size / 1024))
                        psnr_values2_b.append(psnr.psnr(self.ref, dist))
                        self.count_compress(path, time, psnr_values2_b[-1:], bypass)

                        base2 = os.path.basename(path)
                        self.name2 = os.path.splitext(base2)[0]
                        self.dirn2 = os.path.dirname(path)

                        path2 = self.prepare_folder2(self.nr_res, bypass)
                        print(path2)
                        dist_file = path2

                        with open('time_decompressed_OJ_B.txt', 'w') as f:
                            run(["/usr/bin/time", "-f", "%U", "./opj_decompress", "-i", path, "-o", path2], stderr=f)
                        file = open('time_decompressed_OJ_B.txt', 'r')
                        time = file.read()

                        file_size = os.path.getsize(dist_file)

                        dist = scipy.misc.imread(dist_file, flatten=True).astype(numpy.float32)

                        size_values_b.append(int(file_size / 1024))
                        psnr_values_b.append(psnr.psnr(self.ref, dist))
                        self.count_decompress(path, time, psnr_values_b[-1:], bypass)

        # Dynamic pixels count
        with Image.open(input_file) as img:
            width, height = img.size
        # statistics count TODO
        resolution = width * height
        size = os.path.getsize(input_file)
        bytetopixel = float(size) / float(resolution)

        results.append([input_file, str(size) + 'B', str(resolution) + 'px', str(bytetopixel)])

    def prepare_folder(self, nr_res, bypass):
        """
        Ensures that temporary directory and file exists and is writable.
        Returns name of temporary file.
        """
        if bypass:
            self.path = self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_B' + '/' + self.name + '_' + str(
                self.tile) + '-' + str(nr_res) + '_B' + '.jp2'

            try:
                if not os.path.exists(self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_B'):
                    os.makedirs(self.dirn + '/compressed/' + '_' + str(
                        self.nr_res) + '_B')  # decimal equivalent of 0755 used on Windows
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
                sys.exit()

            return self.path
        else:
            self.path = self.dirn + '/compressed/' + '_' + str(self.nr_res) + '/' + self.name + '_' + str(self.tile) + '-' + str(nr_res) + '.jp2'

            try:
                if not os.path.exists(self.dirn + '/compressed/' + '_' + str(self.nr_res)):
                    os.makedirs(self.dirn + '/compressed/' + '_' + str(self.nr_res))  # decimal equivalent of 0755 used on Windows
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
                sys.exit()

            return self.path

    def prepare_folder2(self, nr_res, bypass):
        """
        Ensures that temporary directory and file exists and is writable.
        Returns name of temporary file.
        """

        if bypass:
            self.path = self.dirn + '/decompressed/' + '_' + str(nr_res) + '_B' + '/' + self.name2 + '_B.tif'

            try:
                if not os.path.exists(self.dirn + '/decompressed/' + '_' + str(nr_res) + '_B'):
                    os.makedirs(self.dirn + '/decompressed/' + '_' + str(nr_res) + '_B')
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
                sys.exit()

            return self.path

        else:
            self.path = self.dirn + '/decompressed/' + '_' + str(nr_res) + '/' + self.name2 + '.tif'

            try:
                if not os.path.exists(self.dirn + '/decompressed/' + '_' + str(nr_res)):
                    os.makedirs(self.dirn + '/decompressed/' + '_' + str(nr_res))
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
                sys.exit()

            return self.path

    def count_compress(self, path, time, psnr, bypass):
        global results2
        with Image.open(path) as img:
            width, height = img.size
        resolution = width * height
        size = os.path.getsize(path)
        bytetopixel = float(size) / float(resolution)

        if bypass:
            results2_b.append([path, str(size) + 'B', str(resolution) + 'px', str(bytetopixel), psnr, time])
        else:
            results2.append([path, str(size) + 'B', str(resolution) + 'px', str(bytetopixel), psnr, time])
            print(results2[-1:])

    def count_decompress(self, path, time, psnr, bypass):
        global results3
        with Image.open(path) as img:
            width, height = img.size
        print(path)
        resolution = width * height
        size = os.path.getsize(path)
        bytetopixel = float(size) / float(resolution)

        if bypass:
            results3_b.append([path, str(size) + 'B', str(resolution) + 'px', str(bytetopixel), psnr, time])
        else:
            results3.append([path, str(size) + 'B', str(resolution) + 'px', str(bytetopixel), psnr, time])

    def main_parse(self, input_file):
        debug('main_parse | Input file: ' + input_file)
        # IF folder  ---------------------------------------------------------------
        if os.path.isdir(input_file):
            for file_of_folder in os.listdir(input_file):
                debug('main_parse | Is folder: <' + input_file + '> read file: <' + file_of_folder + '>')
                self.main_parse(input_file + '/' + file_of_folder)

        # IF valid image -------------------------------------------------------------------

        elif input_file.endswith(".tif"):
            self.read_image(input_file)

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


class Compress_kakadu:

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
        # print(input_file + "\n")
        # Analyze image with openjpeg
        base = os.path.basename(input_file)
        self.name = os.path.splitext(base)[0]
        self.folder = os.path.dirname(input_file).split('/')[1]
        # print(self.folder)
        self.dirn = os.path.dirname(input_file)
        ref_file = input_file

        self.ref = scipy.misc.imread(ref_file, flatten=True).astype(numpy.float32)

        for self.tile in range(1024, 4096, 1024):
            for self.nr_res in range(1, 11, 1):
                path = self.prepare_folder(self.nr_res)
                print(path)
                dist_file = path
                with open('time_' + self.folder + '-' + str(self.tile) + '-' + str(self.nr_res) + '_c.txt', 'a') as f:
                    run(["/usr/bin/time", "-f", "%U", "./kdu_compress", "-i", input_file, "-o", path, "Creversible=yes", "Stiles={" + self.tile + ',' + self.tile + "}", "Clevels=" + str(self.nr_res), "Clayers=1", "Cblk={64,64}", "Corder={RPCL}"], stderr=f)
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

        with open('time_' + self.folder + '_' + str(self.tile) + '-' + str(nrnr) + '_d.txt', 'a') as f:
            run(["/usr/bin/time", "-f", "%U", "./kdu_expand", "-i", path, "-o", path2], stderr=f)

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

        self.path = self.dirn + '/compressed/' + str(self.tile) + '_' + str(self.nr_res) + '/' + self.name + '_' + self.tile + '-' + str(nr_res) + '.jp2'

        try:
            if not os.path.exists(self.dirn + '/compressed/' + str(self.tile) + '_' + str(self.nr_res)):
                os.makedirs(self.dirn + '/compressed/' + str(self.tile) + '_' + str(self.nr_res))  # decimal equivalent of 0755 used on Windows
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

        self.path = self.dirn + '/decompressed/' + self.tile.split(',')[0] + '_' + str(nr_res) + '/' + self.name2.split('_')[0] + '_' + self.tile.split(',')[0] + '-' + str(nr_res) + '.tif'

        try:
            if not os.path.exists(self.dirn + '/decompressed/' + self.tile.split(',')[0] + '_' + str(nr_res)):
                os.makedirs(self.dirn + '/decompressed/' + self.tile.split(',')[0] + '_' + str(nr_res))  # decimal equivalent of 0755 used on Windows
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
