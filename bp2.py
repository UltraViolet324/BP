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
# from io import StringIO
# import time
# from datetime import datetime
from argparse import ArgumentParser
from PIL import Image
# import subprocess
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
results2.append(['Nazev souboru', 'Velikost dlazdice', 'pocet urovni rozkladu', 'Bit/Pixel', 'PSNR', 'TIME', 'Bypass'])
results3.append(['Nazev souboru', 'Velikost dlazdice', 'pocet urovni rozkladu', 'Bit/Pixel', 'PSNR', 'TIME', 'Bypass'])
results2_b.append(['Nazev souboru', 'Velikost dlazdice', 'pocet urovni rozkladu', 'Bit/Pixel', 'PSNR', 'TIME', 'Bypass'])
results3_b.append(['Nazev souboru', 'Velikost dlazdice', 'pocet urovni rozkladu', 'Bit/Pixel', 'PSNR', 'TIME', 'Bypass'])

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

    args = parser.parse_args()

    error_message = ""
    if not args.input:
        error_message += "Input file is missing.\n"
    if len(error_message) > 0:
        error_message += "Some arguments are not set. Please run with -h/--help\n"
        print(error_message)
        sys.exit(exit_failure)

    compress = Compress()

    compress.main_parse(args.input)
    compress.write_to_csv(results, 'before')
    compress.write_to_csv(results2, 'compressed_opj')
    compress.write_to_csv(results3, 'decompressed_opj')
    compress.write_to_csv(results2_b, 'compressed_kkd')
    compress.write_to_csv(results3_b, 'decompressed_kkd')
    # compress.psnr_compare(quality_values, psnr_values, size_values)
    # compress.psnr_compare2(quality_values, psnr_values2, size_values2)


class Compress:

    def __init__(self):

        self.tile = ''
        self.nr_res = ''
        self.dirn = ''
        self.path = ''
        self.name = ''
        self.ref = ''
        self.dist = ''
        self.dire = ''
        self.dirn2 = ''
        self.name2 = ''

    def read_image(self, input_file):
        global results
        base = os.path.basename(input_file)
        self.name = os.path.splitext(base)[0]
        self.dirn = os.path.dirname(input_file)
        ref_file = input_file

        self.ref = scipy.misc.imread(ref_file, flatten=True).astype(numpy.float32)

        for kakadu in range(0, 2, 1):
            for bypass in range(0, 2, 1):
                for self.tile in range(1024, 1025, 1024):
                    for self.nr_res in range(1, 3, 1):
                        if bypass == 0 and kakadu == 0:
                            path = self.prepare_folder(self.nr_res, bypass, kakadu)
                            print("b0k0 = " + path)
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
                            self.count_compress(path, time, psnr_values2[-1:], kakadu, bypass)

                            base2 = os.path.basename(path)
                            self.name2 = os.path.splitext(base2)[0]
                            self.dirn2 = os.path.dirname(path)

                            path2 = self.prepare_folder2(self.nr_res, bypass, kakadu)
                            print("b0k0d = " + path2)
                            dist_file = path2

                            with open('time_decompressed_OJ.txt', 'w') as f:
                                run(["/usr/bin/time", "-f", "%U", "./opj_decompress", "-i", path, "-o", path2], stderr=f)
                            file = open('time_decompressed_OJ.txt', 'r')
                            time = file.read()

                            file_size = os.path.getsize(dist_file)

                            dist = scipy.misc.imread(dist_file, flatten=True).astype(numpy.float32)

                            size_values.append(int(file_size / 1024))
                            psnr_values.append(psnr.psnr(self.ref, dist))
                            self.count_decompress(path2, time, psnr_values[-1:], kakadu, bypass)

                        elif bypass == 1 and kakadu == 0:
                            path = self.prepare_folder(self.nr_res, bypass, kakadu)
                            print("b1k0 = " + path)
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
                            self.count_compress(path, time, psnr_values2_b[-1:], kakadu, bypass)

                            base2 = os.path.basename(path)
                            self.name2 = os.path.splitext(base2)[0]
                            self.dirn2 = os.path.dirname(path)

                            path2 = self.prepare_folder2(self.nr_res, bypass, kakadu)
                            print("b1k0d = " + path2)
                            dist_file = path2

                            with open('time_decompressed_OJ_B.txt', 'w') as f:
                                run(["/usr/bin/time", "-f", "%U", "./opj_decompress", "-i", path, "-o", path2], stderr=f)
                            file = open('time_decompressed_OJ_B.txt', 'r')
                            time = file.read()

                            file_size = os.path.getsize(dist_file)

                            dist = scipy.misc.imread(dist_file, flatten=True).astype(numpy.float32)

                            size_values_b.append(int(file_size / 1024))
                            psnr_values_b.append(psnr.psnr(self.ref, dist))
                            self.count_decompress(path2, time, psnr_values_b[-1:], kakadu, bypass)

                        elif bypass == 0 and kakadu == 1:
                            path = self.prepare_folder(self.nr_res, bypass, kakadu)
                            print("b0k1 = " + path)
                            dist_file = path
                            with open('time_compressed_kkd.txt', 'w') as f:
                                run(["/usr/bin/time", "-f", "%U", "./kdu_compress", "-i", input_file, "-o", path,
                                     "Creversible=yes", "Stiles={" + str(self.tile) + ',' + str(self.tile) + "}",
                                     "Clevels=" + str(self.nr_res), "Clayers=1", "Cblk={64,64}", "Corder={RPCL}"],
                                    stderr=f)
                            file = open('time_compressed_kkd.txt', 'r')
                            time = file.read()

                            quality_values.append(self.nr_res)

                            file_size = os.path.getsize(dist_file)

                            dist = scipy.misc.imread(dist_file, flatten=True).astype(numpy.float32)

                            size_values2.append(int(file_size / 1024))
                            psnr_values2.append(psnr.psnr(self.ref, dist))
                            self.count_compress(path, time, psnr_values2[-1:], kakadu, bypass)

                            base2 = os.path.basename(path)
                            self.name2 = os.path.splitext(base2)[0]
                            self.dirn2 = os.path.dirname(path)

                            path2 = self.prepare_folder2(self.nr_res, bypass, kakadu)
                            print("b0k1d = " + path2)
                            dist_file = path2

                            with open('time_decompressed_kkd_B.txt', 'w') as f:
                                run(["/usr/bin/time", "-f", "%U", "./kdu_expand", "-i", path, "-o", path2], stderr=f)
                            file = open('time_decompressed_kkd_B.txt', 'r')
                            time = file.read()

                            file_size = os.path.getsize(dist_file)

                            dist = scipy.misc.imread(dist_file, flatten=True).astype(numpy.float32)

                            size_values.append(int(file_size / 1024))
                            psnr_values.append(psnr.psnr(self.ref, dist))
                            self.count_decompress(path2, time, psnr_values[-1:], kakadu, bypass)

                        elif bypass == 1 and kakadu == 1:
                            path = self.prepare_folder(self.nr_res, bypass, kakadu)
                            print("b1k1 = " + path)
                            dist_file = path
                            with open('time_compressed_kkd_B.txt', 'w') as f:
                                run(["/usr/bin/time", "-f", "%U", "./kdu_compress", "-i", input_file, "-o", path,
                                     "Creversible=yes", "Stiles={" + str(self.tile) + ',' + str(self.tile) + "}",
                                     "Clevels=" + str(self.nr_res), "Clayers=1", "Cblk={64,64}", "Corder={RPCL}", "Cmodes={BYPASS}"],
                                    stderr=f)
                            file = open('time_compressed_kkd_B.txt', 'r')
                            time = file.read()

                            quality_values.append(self.nr_res)

                            file_size = os.path.getsize(dist_file)

                            dist = scipy.misc.imread(dist_file, flatten=True).astype(numpy.float32)

                            size_values2.append(int(file_size / 1024))
                            psnr_values2.append(psnr.psnr(self.ref, dist))
                            self.count_compress(path, time, psnr_values2[-1:], kakadu, bypass)

                            base2 = os.path.basename(path)
                            self.name2 = os.path.splitext(base2)[0]
                            self.dirn2 = os.path.dirname(path)

                            path2 = self.prepare_folder2(self.nr_res, bypass, kakadu)
                            print("b1k1d = " + path2)
                            dist_file = path2

                            with open('time_decompressed_kkd.txt', 'w') as f:
                                run(["/usr/bin/time", "-f", "%U", "./kdu_expand", "-i", path, "-o", path2], stderr=f)
                            file = open('time_decompressed_kkd.txt', 'r')
                            time = file.read()

                            file_size = os.path.getsize(dist_file)

                            dist = scipy.misc.imread(dist_file, flatten=True).astype(numpy.float32)

                            size_values.append(int(file_size / 1024))
                            psnr_values.append(psnr.psnr(self.ref, dist))
                            self.count_decompress(path2, time, psnr_values[-1:], kakadu, bypass)

        with Image.open(input_file) as img:
            width, height = img.size
        resolution = width * height
        size = os.path.getsize(input_file) * 8
        bittopixel = float(size) / float(resolution)

        results.append([input_file, str(size) + 'B', str(resolution) + 'px', str(bittopixel)])

    def prepare_folder(self, nr_res, bypass, kakadu):
        """
        Ensures that temporary directory and file exists and is writable.
        Returns name of temporary file.
        """
        if bypass and kakadu:
            self.path = self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_kkd_B' + '/' + self.name + '_' + str(self.tile) + '-' + str(nr_res) + '_kkd_B' + '.jp2'

            try:
                if not os.path.exists(self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_kkd_B'):
                    os.makedirs(self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_kkd_B')
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
                sys.exit()

            return self.path

        elif not bypass and kakadu:
            self.path = self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_kkd' + '/' + self.name + '_' + str(self.tile) + '-' + str(nr_res) + '_kkd' + '.jp2'

            try:
                if not os.path.exists(self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_kkd'):
                    os.makedirs(self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_kkd')
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
                sys.exit()

            return self.path

        elif not kakadu and bypass:
            self.path = self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_opj_B' + '/' + self.name + '_' + str(self.tile) + '-' + str(nr_res) + '_opj_B' + '.jp2'

            try:
                if not os.path.exists(self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_opj_B'):
                    os.makedirs(self.dirn + '/compressed/' + '_' + str(
                        self.nr_res) + '_opj_B')
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
                sys.exit()

            return self.path

        elif not kakadu and not bypass:
            self.path = self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_opj' + '/' + self.name + '_' + str(self.tile) + '-' + str(nr_res) + '_opj.jp2'

            try:
                if not os.path.exists(self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_opj'):
                    os.makedirs(self.dirn + '/compressed/' + '_' + str(self.nr_res) + '_opj')
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
                sys.exit()

            return self.path

    def prepare_folder2(self, nr_res, bypass, kakadu):
        """
        Ensures that temporary directory and file exists and is writable.
        Returns name of temporary file.
        """

        if bypass and kakadu:
            self.path = self.dirn + '/decompressed/' + '_' + str(nr_res) + '_kkd_B' + '/' + self.name2 + '.tif'

            try:
                if not os.path.exists(self.dirn + '/decompressed/' + '_' + str(nr_res) + '_kkd_B'):
                    os.makedirs(self.dirn + '/decompressed/' + '_' + str(nr_res) + '_kkd_B')
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
                sys.exit()

            return self.path

        elif not kakadu and not bypass:
            self.path = self.dirn + '/decompressed/' + '_' + str(nr_res) + '_opj' + '/' + self.name2 + '.tif'

            try:
                if not os.path.exists(self.dirn + '/decompressed/' + '_' + str(nr_res) + '_opj'):
                    os.makedirs(self.dirn + '/decompressed/' + '_' + str(nr_res) + '_opj')
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
                sys.exit()

            return self.path

        elif kakadu and not bypass:
            self.path = self.dirn + '/decompressed/' + '_' + str(nr_res) + '_kkd' + '/' + self.name2 + '.tif'

            try:
                if not os.path.exists(self.dirn + '/decompressed/' + '_' + str(nr_res) + '_kkd'):
                    os.makedirs(self.dirn + '/decompressed/' + '_' + str(nr_res) + '_kkd')
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
                sys.exit()

            return self.path

        elif not kakadu and bypass:
            self.path = self.dirn + '/decompressed/' + '_' + str(nr_res) + '_opj_B' + '/' + self.name2 + '.tif'

            try:
                if not os.path.exists(self.dirn + '/decompressed/' + '_' + str(nr_res) + '_opj_B'):
                    os.makedirs(self.dirn + '/decompressed/' + '_' + str(nr_res) + '_opj_B')
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(self.dirn, e.errno, e.strerror))
                sys.exit()

            return self.path

    def count_compress(self, path, time, psnr, kakadu, bypass):
        global results2
        with Image.open(path) as img:
            width, height = img.size
        resolution = width * height
        size = os.path.getsize(path) * 8
        bittopixel = float(size) / float(resolution)

        if kakadu:
            results2_b.append([path, self.tile, self.nr_res, str(bittopixel), psnr, time, bypass])
        else:
            results2.append([path, self.tile, self.nr_res, str(bittopixel), psnr, time, bypass])
            print(results2[-1:])

    def count_decompress(self, path, time, psnr, kakadu, bypass):
        global results3
        with Image.open(path) as img:
            width, height = img.size
        print("count decompress = " + path)
        resolution = width * height
        size = os.path.getsize(path) * 8
        bittopixel = float(size) / float(resolution)

        if kakadu:
            results3_b.append([path, self.tile, self.nr_res, str(bittopixel), psnr, time, bypass])
        else:
            results3.append([path, self.tile, self.nr_res, str(bittopixel), psnr, time, bypass])

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

    def psnr_compare_decompressed(self, nr_res, psnr_values, size_values):

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
