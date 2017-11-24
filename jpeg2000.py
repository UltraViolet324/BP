#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on 2017-10-22

@author: Lucie Vrtelova (xvrtel00@stud.fit.vutbr.cz)
"""
from subprocess import run
from PIL import Image
import os
import sys
import csv
import scipy.misc
import numpy
import psnr
from argparse import ArgumentParser

q_layers = 1
nr_res = 1
tile = 512
codeblock = 64
p_order = "RPCL"
x_axis = 0
y_axis = 0
mode = 0
reversible = 'yes'
openjpeg = 1
kakadu = 0
orig_bpp = 0.0000
time_comp = 0.0000
compress_bpp = 0.0000
compress_psnr = 0.0000
time_decomp = 0.0000
decompree_bpp = 0.0000
decompress_psnr = 0.0000


exit_failure = 1
DEBUG = 1


def debug(value):
    if DEBUG:
        print(value)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-i", "--input",
        dest="input",
        help="path to input folder",
        metavar="INPUT")

    args = parser.parse_args()

    error_message = ""
    if not args.input:
        error_message += "Input path is missing.\n"
    if len(error_message) > 0:
        error_message += "Some arguments are not set. Please run with -h/--help\n"
        print(error_message)
        sys.exit(exit_failure)

    opj = OpenJpeg()
    kkd = Kakadu()
    func = HelpingFunctions()

    if openjpeg:
        func.parse_folder(args.input)
    elif kakadu:
        name, dirn, ref = func.parse_folder(args.input)
        path = func.prepare_folder(dirn, name, True)
        orig_bpp = func.count_bpp(args.input)
        time_comp = kkd.compress(args.input, path, q_layers, nr_res, tile, codeblock, p_order, x_axis, y_axis, mode, reversible)
        compress_bpp = func.count_bpp(path)
        compress_psnr = func.postprocess_image(path, ref)
        path2 = func.prepare_folder(dirn, nr_res, False)
        time_decomp = kkd.decompress(path, path2)
        decompree_bpp = func.count_bpp(path2)
        decompress_psnr = func.postprocess_image(path2, ref)
        func.delete_image(path, path2)


class OpenJpeg:
    @staticmethod
    def compress(input_file, path, q_layers, nr_res, tile, codeblock, p_order, x_axis, y_axis, mode):
        """

        :param input_file:
        :param path:
        :param q_layers:
        :param nr_res:
        :param tile:
        :param codeblock:
        :param p_order:
        :param x_axis:
        :param y_axis:
        :param mode:
        :return:
        """
        with open('time_compressed_OJ.txt', 'w') as f:
            run(["/usr/bin/time", "-f", "%U", "./opj_compress", "-i", input_file, "-o", path, "-r", str(q_layers),
                 "-n", str(nr_res), "-t", str(tile) + ',' + str(tile), "-b", str(codeblock) + ',' + str(codeblock),
                 "-p",  p_order, "-d", str(x_axis) + ',' + str(y_axis), "-M", str(mode)], stderr=f)
        file = open('time_compressed_OJ.txt', 'r')
        file.readline()
        time = file.readline().strip()
        if 'Warning' in time:
            time = file.readline().strip()
        file.close()

        return float(time)

    @staticmethod
    def decompress(path, path2):
        with open('time_decompressed_OJ_B.txt', 'w') as f:
            run(["/usr/bin/time", "-f", "%U", "./opj_decompress", "-i", path, "-o", path2], stderr=f)
        file = open('time_decompressed_OJ_B.txt', 'r')
        file.readline()
        time = file.readline().strip()
        file.close()

        return float(time)


class Kakadu:
    @staticmethod
    def compress(input_file, path, q_layers, nr_res, tile, codeblock, p_order, x_axis, y_axis, mode, reversible):
        """

        :param input_file:
        :param path:
        :param q_layers:
        :param nr_res:
        :param tile:
        :param codeblock:
        :param p_order:
        :param x_axis:
        :param y_axis:
        :param mode:
        :param reversible:
        :return:
        """
        with open('time_compressed_kkd_B.txt', 'w') as f:
            run(["/usr/bin/time", "-f", "%U", "./kdu_compress", "-i", input_file, "-o", path,
                 "Creversible=" + reversible, "Stiles={" + str(tile) + ',' + str(tile) + "}",
                 "Clevels=" + str(nr_res), "Clayers=" + str(q_layers),
                 "Cblk={" + str(codeblock) + "," + str(codeblock) + "}", "Corder={" + p_order + "}",
                 "Cmodes={" + mode + "}", "SOrigin={" + x_axis + "," + y_axis + "}"],
                stderr=f)
        file = open('time_compressed_kkd_B.txt', 'r')
        time = file.readline().strip()
        file.close()

        return time

    @staticmethod
    def decompress(path, path2):
        """

        :param path:
        :param path2:
        :return:
        """
        with open('time_decompressed_kkd.txt', 'w') as f:
            run(["/usr/bin/time", "-f", "%U", "./kdu_expand", "-i", path, "-o", path2], stderr=f)
        file = open('time_decompressed_kkd.txt', 'r')
        time = file.readline().strip()
        file.close()

        return time


class HelpingFunctions:
    @staticmethod
    def prepare_folder(dirn, name, compress):
        """

        :param dirn:
        :param name:
        :param compress:
        :return:
        """

        if compress:
            path = dirn + '/compressed/' + name + '.jp2'

            try:
                if not os.path.exists(dirn + '/compressed'):
                    os.makedirs(dirn + '/compressed')
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(dirn, e.errno, e.strerror))
                sys.exit()

            return path
        else:
            path = dirn + '/decompressed/' + name + '.tif'

            try:
                if not os.path.exists(dirn + '/decompressed'):
                    os.makedirs(dirn + '/decompressed')
            except IOError as e:
                print(
                    "Failed to create directory '{0}'\nError (code {1}): '{2}'.".format(dirn, e.errno, e.strerror))
                sys.exit()

            return path

    @staticmethod
    def count_bpp(path):
        """

        :param path:
        :return:
        """
        with Image.open(path) as img:
            width, height = img.size
        resolution = width * height
        size = os.path.getsize(path) * 8
        bpp = float(size) / float(resolution)

        return bpp

    @staticmethod
    def write_to_csv(text, filename):
        """

        :param text:
        :param filename:
        :return:
        """
        with open(filename+'.csv', "w") as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerows(text)

    def parse_folder(self, input_file):
        """

        :param input_file:
        :return:
        """
        global orig_bpp
        global time_comp
        global compress_bpp
        global compress_psnr
        global time_decomp
        global decompree_bpp
        global decompress_psnr

        debug('main_parse | Input file: ' + input_file)
        # IF folder  ---------------------------------------------------------------
        if os.path.isdir(input_file):
            for file_of_folder in os.listdir(input_file):
                debug('main_parse | Is folder: <' + input_file + '> read file: <' + file_of_folder + '>')
                self.parse_folder(input_file + '/' + file_of_folder)
            if os.path.dirname(input_file) != "":
                # TODO: print data for one dataset deleno poctem fotek v datasetu
                print(orig_bpp, time_comp, compress_bpp, compress_psnr, time_decomp, decompree_bpp, decompress_psnr)
                orig_bpp = 0.0000
                time_comp = 0.0000
                compress_bpp = 0.0000
                compress_psnr = 0.0000
                time_decomp = 0.0000
                decompree_bpp = 0.0000
                decompress_psnr = 0.0000

        # IF valid image -------------------------------------------------------------------

        elif input_file.endswith(".tif"):
            opj = OpenJpeg()
            kkd = Kakadu()


            # print(name, dirn)
            # TODO: globalni citace, spoustet v cyklu
            name, dirn, ref = self.parse_file(input_file)
            path = self.prepare_folder(dirn, name, True)
            orig_bpp += self.count_bpp(input_file)
            time_comp += opj.compress(input_file, path, q_layers, nr_res, tile, codeblock, p_order, x_axis, y_axis, mode)
            print("compressed")
            compress_bpp += self.count_bpp(path)
            compress_psnr += self.postprocess_image(path, ref)
            path2 = self.prepare_folder(dirn, name, False)
            time_decomp += opj.decompress(path, path2)
            decompree_bpp += self.count_bpp(path2)
            decompress_psnr += self.postprocess_image(path2, ref)
            self.delete_image(path, path2)

        # Some mess  -- ignore----------------------------------------------------------------
        else:
            debug("File:" + input_file + " - ignored ")
            pass

    def parse_file(self, input_file):

        base = os.path.basename(input_file)
        name = os.path.splitext(base)[0]
        dirn = os.path.dirname(input_file)

        ref = scipy.misc.imread(input_file, flatten=True).astype(numpy.float32)

        return name, dirn, ref

    @staticmethod
    def postprocess_image(path, ref):

        # file_size = os.path.getsize(path)
        dist = scipy.misc.imread(path, flatten=True).astype(numpy.float32)
        psnr_count = psnr.psnr(ref, dist)

        return float(psnr_count)

    @staticmethod
    def delete_image(path, path2):

        try:
            os.remove(path)
        except IOError as e:
            print(
                "Failed  to remove '{0}'\nError (code {1}): '{2}'.".format(path, e.errno, e.strerror))
            sys.exit()

        try:
            os.remove(path2)
        except IOError as e:
            print(
                "Failed  to remove '{0}'\nError (code {1}): '{2}'.".format(path2, e.errno, e.strerror))
            sys.exit()


if __name__ == "__main__":
    main()
