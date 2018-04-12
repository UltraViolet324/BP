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
import collections


q_layers = 12
nr_res_k = 0
nr_res_o = 0
tile_collection = [512, 1024, 2048, 4096]
tile = 512
codeblock = 64
p_order = "RPCL"
x_axis = 0
y_axis = 0
kmode = ""
omode = ""
modes = {0: 0, 'BYPASS': 1, 'RESET': 2, 'RESTART': 4, 'BYPASS|RESET': 3, 'BYPASS|RESTART': 5, 'RESET|RESTART': 6,
         'BYPASS|RESET|RESTART': 7}
opj_mode = [0, 1, 2, 4, 3, 5, 6, 7]
kkd_mode = [0, 'BYPASS', 'CAUSAL', 'RESET', 'RESTART', 'CAUSAL|BYPASS', 'BYPASS|RESET', 'BYPASS|RESTART', 'CAUSAL|RESET',
            'CAUSAL|RESTART', 'RESET|RESTART', 'BYPASS|CAUSAL|RESET', 'BYPASS|CAUSAL|RESTART', 'CAUSAL|RESET|RESTART',
            'BYPASS|RESET|RESTART', 'BYPASS|CAUSAL|RESET|RESTART']
reversible = 'no'
openjpeg = 0
kakadu = 0
ireversible = 1
orig_bpp = 0.0000
time_comp = 0.0000
compress_bpp = 0.0000
compress_psnr = 0.0000
time_decomp = 0.0000
decompress_bpp = 0.0000
decompress_psnr = 0.0000
count = 0
dataset = []
num_threads = 4
layers = 0
time_decomp_layer_list = []
decompress_psnr_list = []
decompress_bpp_list = []
compression_ratio_kkd = 3
compression_ration_opj = ", ".join([str(compression_ratio_kkd)]*int(q_layers))
bpp_kkd = ""

# results.append(['Velikost dlazdice', 'pocet urovni rozkladu', 'Bit/Pixel', 'PSNR-komprese', 'cas_komprese', 'Bypass'])
# results2.append(['Velikost dlazdice', 'pocet urovni rozkladu', 'Bit/Pixel', 'PSNR-dekomprese', 'cas_dekomprese', 'Bypass'])


exit_failure = 1
DEBUG = 0


def debug(value):
    if DEBUG:
        print(value)


def main():
    global nr_res
    global tile_collection
    global tile
    global opj_mode
    global kkd_mode
    global layers
    global kakadu
    global openjpeg
    global modes
    global nr_res_o
    global nr_res_k
    global kmode
    global omode


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

    func = HelpingFunctions()

    if q_layers > 1:
        layers = 1
        for kmode, omode in modes.items():
            for tile in tile_collection:
                for nr_res_k in range(0, 10, 1):

                    kakadu = 1
                    # debug("Kakadu: " + str(kakadu))
                    func.parse_folder(args.input)
                    kakadu = 0
                    debug("kakadu: " + str(kakadu))
                    # sys.exit(5)

                    nr_res_o = nr_res_k + 1
                    openjpeg = 1
                    debug("opj: " + str(openjpeg))
                    func.parse_folder(args.input)
                    openjpeg = 0
                    debug("opj: " + str(openjpeg))

                    # sys.exit(4)

    for kmode, omode in modes.items():
        for tile in tile_collection:
            for nr_res_k in range(0, 10, 1):
                kakadu = 1
                debug("Kakadu: " + str(kakadu))
                func.parse_folder(args.input)
                kakadu = 0
                debug("kakadu: " + str(kakadu))
                nr_res_o = nr_res_k + 1
                openjpeg = 1
                debug("opj: " + str(openjpeg))
                if int(tile) == 512 and (int(omode) == 1 or int(omode) == 4 or int(omode) == 6 or int(omode) == 5 or int(omode) == 7) and int(nr_res_o) == 9:
                    debug("vyskocim")
                    openjpeg = 0
                    continue
                elif int(tile) == 512 and (int(omode) == 1 or int(omode) == 4 or int(omode) == 6 or int(omode) == 5 or int(omode) == 7) and int(nr_res_o) == 10:
                    openjpeg = 0
                    continue
                elif int(tile) == 1024 and (int(omode) == 1 or int(omode) == 4 or int(omode) == 6 or int(omode) == 5 or int(omode) == 7) and int(nr_res_o) == 10:
                    openjpeg = 0
                    continue
                else:
                    func.parse_folder(args.input)
                openjpeg = 0
                debug("opj: " + str(openjpeg))


class OpenJpeg:
    @staticmethod
    def compress(input_file, path, quality_layers, number_of_resolution, tiles, codeblocks, order, x, y, omodes, compression_ratio):
        """

        :param compression_ratio:
        :param omodes:
        :param input_file:
        :param path:
        :param quality_layers:
        :param number_of_resolution:
        :param tiles:
        :param codeblocks:
        :param order:
        :param x:
        :param y:
        :return:
        """
        global ireversible
        global bpp_kkd
        global q_layers

        if not ireversible:
            with open('time_compressed_OJ.txt', 'w') as f:
                run(["/usr/bin/time", "-f", "%U", "./opj_compress", "-i", input_file, "-o", path, "-r", str(quality_layers),
                     "-n", str(number_of_resolution), "-t", str(tiles) + ',' + str(tiles), "-b",
                     str(codeblocks) + ',' + str(codeblock),
                     "-p", order, "-d", str(x) + ',' + str(y), "-M", str(omodes)], stderr=f)
            file = open('time_compressed_OJ.txt', 'r')
            file.readline()
            time = file.readline().strip()
            if 'Warning' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            file.close()

            return float(time)

        if ireversible:
            debug(bpp_kkd)
            bpp_opj = ', '.join(bpp_kkd)
            debug(compression_ratio)
            # sys.exit(3)
            with open('time_compressed_OJ.txt', 'w') as f:
                run(["/usr/bin/time", "-f", "%U", "./opj_compress", "-i", input_file, "-o", path, "-r", bpp_opj,
                     "-n", str(number_of_resolution), "-t", str(tiles) + ',' + str(tiles), "-b",
                     str(codeblocks) + ',' + str(codeblock),
                     "-p", order, "-d", str(x) + ',' + str(y), "-M", str(omodes), "-I"], stderr=f)
            file = open('time_compressed_OJ.txt', 'r')
            file.readline()
            time = file.readline().strip()
            if 'Warning' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            file.close()
            return float(time)


    @staticmethod
    def decompress(path, path2, layer, ref):
        if not layer:
            with open('time_decompressed_OJ_B.txt', 'w') as f:
                run(["/usr/bin/time", "-f", "%U", "./opj_decompress", "-i", path, "-o", path2], stderr=f)
            file = open('time_decompressed_OJ_B.txt', 'r')
            file.readline()
            time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            if 'handle' in time:
                time = file.readline().strip()
            file.close()

            return float(time)
        elif layer:
            time_layer = []
            opj_decompress_psnr = []
            opj_decompress_bpp = []
            for layer in range(1, q_layers + 1, 1):
                debug("layer_opj: " + str(layer))

                with open('time_decompressed_OJ_B.txt', 'w') as f:
                    run(["/usr/bin/time", "-f", "%U", "./opj_decompress", "-i", path, "-o", path2, "-l", str(layer)],
                        stderr=f)
                file = open('time_decompressed_OJ_B.txt', 'r')
                file.readline()
                time = file.readline().strip()
                if 'handle' in time:
                    time = file.readline().strip()
                if 'handle' in time:
                    time = file.readline().strip()
                if 'handle' in time:
                    time = file.readline().strip()
                if 'handle' in time:
                    time = file.readline().strip()
                if 'handle' in time:
                    time = file.readline().strip()
                if 'handle' in time:
                    time = file.readline().strip()
                file.close()

                time_layer.append((layer, float(time)))
                opj_decompress_bpp.append((layer, HelpingFunctions().count_bpp(path2)))
                opj_decompress_psnr.append((layer, HelpingFunctions().postprocess_image(path2, ref)))
                HelpingFunctions().delete_image(path2)
            return time_layer, opj_decompress_bpp, opj_decompress_psnr


class Kakadu:
    @staticmethod
    def compress(input_file, path, quality_layers, number_of_resolution, tiles, codeblocks, order, x, y, kmodes, revers,
                 num_thread, compress_ratio):
        """

        :param input_file:
        :param path:
        :param quality_layers:
        :param number_of_resolution:
        :param tiles:
        :param codeblocks:
        :param order:
        :param x:
        :param y:
        :param modes:
        :param revers:
        :param num_thread:
        :param compress_ratio
        :return:
        """
        global ireversible
        global bpp_kkd

        if not ireversible:
            with open('time_compressed_kkd_B.txt', 'w') as f:
                run(["/usr/bin/time", "-f", "%U", "./kdu_compress", "-i", input_file, "-o", path,
                     "Creversible=" + revers, "Stiles={" + str(tiles) + ',' + str(tiles) + "}",
                     "Clevels=" + str(number_of_resolution), "Clayers=" + str(quality_layers),
                     "Cblk={" + str(codeblocks) + "," + str(codeblocks) + "}", "Corder={" + order + "}",
                     "Cmodes={" + str(kmodes) + "}", "Sorigin={" + str(x) + "," + str(y) + "}", "-num_threads",
                     str(num_thread)],
                    stderr=f)
            file = open('time_compressed_kkd_B.txt', 'r')
            time = file.readline().strip()
            file.close()
            return float(time)

        elif ireversible:
            with open('bitrate_kkd.txt', 'w') as r:
                with open('time_compressed_kkd_B.txt', 'w') as f:
                    run(["/usr/bin/time", "-f", "%U", "./kdu_compress", "-i", input_file, "-o", path,
                         "Creversible=" + revers, "Stiles={" + str(tiles) + ',' + str(tiles) + "}",
                         "Clevels=" + str(number_of_resolution), "Clayers=" + str(quality_layers),
                         "Cblk={" + str(codeblocks) + "," + str(codeblocks) + "}", "Corder={" + order + "}",
                         "Cmodes={" + str(kmodes) + "}", "Sorigin={" + str(x) + "," + str(y) + "}", "-num_threads",
                         str(num_thread), "-rate", str(compress_ratio)],
                        stderr=f, stdout=r)
            file = open('time_compressed_kkd_B.txt', 'r')
            time = file.readline().strip()
            file.close()

            with open('bitrate_kkd.txt', 'r') as in_file:  # open file for reading text.
                for line in in_file:  # Keep track of line numbers
                    if 'Layer bit-rates' in line:
                        bpp_kkd_str = in_file.readline().strip() + " " + in_file.readline().strip()
                        bpp_kkd_list = bpp_kkd_str.split(", ")
                        bpp_kkd = bpp_kkd_list[::-1]
                        debug(bpp_kkd)
                        # sys.exit(2)
            in_file.close()

            return float(time)

    @staticmethod
    def decompress(path, path2, layer, ref, num_thread):
        """

        :param path:
        :param path2:
        :param layer:
        :param ref:
        :param num_thread
        :return:
        """
        global q_layers

        if not layer:
            with open('time_decompressed_kkd.txt', 'w') as f:
                run(["/usr/bin/time", "-f", "%U", "./kdu_expand", "-i", path, "-o", path2, "-num_threads",
                     str(num_thread)], stderr=f)
            file = open('time_decompressed_kkd.txt', 'r')
            time = file.readline().strip()
            file.close()

            return float(time)
        elif layers:
            time_layer = []
            kkd_decompress_psnr = []
            kkd_decompress_bpp = []
            for layer in range(1, q_layers+1, 1):
                debug(str(layer) + " layer")
                debug("tile: " + str(tile))
                debug(str(nr_res_k) + " nr_res_k")
                with open('time_decompressed_kkd.txt', 'w') as f:
                    run(["/usr/bin/time", "-f", "%U", "./kdu_expand", "-i", path, "-o", path2, "-layers", str(layer),
                         "-num_threads",
                         str(num_thread)], stderr=f)
                file = open('time_decompressed_kkd.txt', 'r')
                time = file.readline().strip()
                file.close()

                time_layer.append((layer, (float(time))))
                kkd_decompress_bpp.append((layer, HelpingFunctions().count_bpp(path2)))
                kkd_decompress_psnr.append((layer, HelpingFunctions().postprocess_image(path2, ref)))
                HelpingFunctions().delete_image(path2)
            return time_layer, kkd_decompress_bpp, kkd_decompress_psnr


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
            debug(path)
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
            debug(path)
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
        with open(filename + '.csv', "a") as output:
            writer = csv.writer(output, lineterminator='\n', delimiter='\t')
            writer.writerow(text)

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
        global decompress_bpp
        global decompress_psnr
        global count
        global dataset
        global nr_res_o
        global nr_res_k
        global tile
        global omode
        global kmode
        global q_layers
        global codeblock
        global p_order
        global x_axis
        global y_axis
        global reversible
        global num_threads
        global layers
        global time_decomp_layer_list
        global decompress_bpp_list
        global decompress_psnr_list
        global compression_ration_opj
        global compression_ratio_kkd
        global ireversible

        debug('main_parse | Input file: ' + input_file)
        debug("jsem v parse folder")
        # IF folder  ---------------------------------------------------------------
        if os.path.isdir(input_file):
            for file_of_folder in os.listdir(input_file):
                debug('main_parse | Is folder: <' + input_file + '> read file: <' + file_of_folder + '>')
                self.parse_folder(input_file + '/' + file_of_folder)
            if os.path.dirname(input_file) != "":

                if openjpeg:
                    if not ireversible:
                        self.write_to_csv(
                            [tile, nr_res_o, str(compress_bpp / count), str(compress_psnr / count), str(time_comp / count),
                             str(omode)], "opj_compress_R_" + str(dataset[1]))
                    elif ireversible:
                        self.write_to_csv(
                            [tile, nr_res_o, str(compress_bpp / count), str(compress_psnr / count),
                             str(time_comp / count),
                             str(omode)], "opj_compress_I_" + str(dataset[1]))
                    if not layers:
                        self.write_to_csv([tile, nr_res_o, str(decompress_bpp / count), str(decompress_psnr / count),
                                           str(time_decomp / count), str(omode)], "opj_decompress_" + str(dataset[1]))
                    elif layers:
                        debug(time_decomp_layer_list)
                        time_decomp_layer = [dict(time_decomp_layer_list)]
                        debug(time_decomp_layer)

                        counter = collections.Counter()
                        for d in time_decomp_layer:
                            counter.update(d)
                        time_decomp_layer_dict = dict(counter)
                        debug(time_decomp_layer_dict)

                        decompress_bpp_layer = [dict(decompress_bpp_list)]
                        counter = collections.Counter()
                        for d in decompress_bpp_layer:
                            counter.update(d)
                        decompress_bpp_layer_dict = dict(counter)

                        decompress_psnr_layer = [dict(decompress_psnr_list)]
                        counter = collections.Counter()
                        for d in decompress_psnr_layer:
                            counter.update(d)
                        decompress_psnr_layer_dict = dict(counter)

                        for key in time_decomp_layer_dict.keys():
                            debug(key)
                            time_decomp = time_decomp_layer_dict.get(key)
                            decompress_bpp = decompress_bpp_layer_dict.get(key)
                            debug(decompress_bpp)
                            decompress_psnr = decompress_psnr_layer_dict.get(key)
                            debug(decompress_psnr)
                            debug(time_decomp)
                            self.write_to_csv([tile, nr_res_o, str(decompress_bpp / count), str(decompress_psnr / count),
                                               str(time_decomp / count), str(omode)],
                                              "opj_decompress_" + str(dataset[1]) + '_' + str(key))
                            # debug(orig_bpp / count, time_comp, compress_bpp, compress_psnr / count, time_decomp, decompree_bpp,
                            # decompress_psnr)
                            # debug(count)
                if kakadu:
                    if ireversible:
                        self.write_to_csv(
                            [tile, nr_res_k, str(compress_bpp / count), str(compress_psnr / count), str(time_comp / count),
                             str(kmode)], "kkd_compress_I_" + str(dataset[1]))
                    elif not ireversible:
                        self.write_to_csv(
                            [tile, nr_res_k, str(compress_bpp / count), str(compress_psnr / count),
                             str(time_comp / count),
                             str(kmode)], "kkd_compress_R_" + str(dataset[1]))
                    if not layers:
                        self.write_to_csv([tile, nr_res_k, str(decompress_bpp / count), str(decompress_psnr / count),
                                           str(time_decomp / count), str(kmode)], "kkd_decompress_" + str(dataset[1]))
                    elif layers:
                        time_decomp_layer = [dict(time_decomp_layer_list)]
                        counter = collections.Counter()
                        for d in time_decomp_layer:
                            counter.update(d)
                        time_decomp_layer_dict = dict(counter)

                        decompress_bpp_layer = [dict(decompress_bpp_list)]
                        counter = collections.Counter()
                        for d in decompress_bpp_layer:
                            counter.update(d)
                        decompress_bpp_layer_dict = dict(counter)

                        decompress_psnr_layer = [dict(decompress_psnr_list)]
                        counter = collections.Counter()
                        for d in decompress_psnr_layer:
                            counter.update(d)
                        decompress_psnr_layer_dict = dict(counter)
                        debug(decompress_bpp_layer_dict)

                        for key in time_decomp_layer_dict.keys():
                            debug(key)
                            time_decomp = time_decomp_layer_dict.get(key)
                            decompress_bpp = decompress_bpp_layer_dict.get(key)
                            debug(decompress_bpp)
                            decompress_psnr = decompress_psnr_layer_dict.get(key)
                            debug(decompress_psnr)
                            self.write_to_csv([tile, nr_res_k, str(decompress_bpp / count), str(decompress_psnr / count),
                                               str(time_decomp / count), str(kmode)],
                                              "kkd_decompress_" + str(dataset[1]) + '_' + str(key))
                            # debug(orig_bpp / count, time_comp, compress_bpp, compress_psnr / count, time_decomp, decompree_bpp,
                            # decompress_psnr)
                            # debug(count)

                orig_bpp = 0.0000
                time_comp = 0.0000
                compress_bpp = 0.0000
                compress_psnr = 0.0000
                time_decomp = 0.0000
                decompress_bpp = 0.0000
                decompress_psnr = 0.0000
                count = 0

        # IF valid image -------------------------------------------------------------------

        elif input_file.endswith(".tif"):
            opj = OpenJpeg()
            kkd = Kakadu()
            count += 1
            dataset = os.path.dirname(input_file).split("/")

            # debug(name + ", " + dirn)

            name, dirn, ref = self.parse_file(input_file)
            path = self.prepare_folder(dirn, name, True)
            orig_bpp += self.count_bpp(input_file)

            if openjpeg:
                debug("compressed_opj_start: " + ", " + str(nr_res_k) + ", " + str(tile) + ", " + str(q_layers) + ", " + str(omode))
                time_comp += opj.compress(input_file, path, q_layers, nr_res_o, tile, codeblock, p_order, x_axis, y_axis,
                                          omode, compression_ration_opj)
                debug("compressed_opj: " + ", " + str(nr_res_k) + ", " + str(tile) + ", " + str(q_layers) + ", " + str(omode))
                compress_bpp += self.count_bpp(path)
                compress_psnr += self.postprocess_image(path, ref)
                path2 = self.prepare_folder(dirn, name, False)
                if not layers:
                    time_decomp += opj.decompress(path, path2, layers, ref)
                    debug("deompress_opj")
                    decompress_bpp += self.count_bpp(path2)
                    decompress_psnr += self.postprocess_image(path2, ref)
                    self.delete_image(path)
                    self.delete_image(path2)
                else:

                    time_decomp_layer_list, decompress_bpp_list, decompress_psnr_list = opj.decompress(path, path2,
                                                                                                       layers, ref)
                    debug(time_decomp_layer_list)
                    debug("\n")
                    debug(decompress_psnr_list)
                    debug("\n")
                    debug(decompress_bpp_list)
                    debug("\n")
                    self.delete_image(path)

                self.delete_dir(dirn)

            if kakadu:
                debug('compressed_kkd_start: ' + ", " + str(nr_res_k) + ", " + str(tile) + ", " + str(q_layers) + ", " + str(kmode))
                time_comp += kkd.compress(input_file, path, q_layers, nr_res_k, tile, codeblock, p_order, x_axis, y_axis,
                                          kmode, reversible, num_threads, compression_ratio_kkd)
                debug("compressed_kkd: " + ", " + str(nr_res_k) + ", " + str(tile) + ", " + str(q_layers) + ", " + str(kmode))
                compress_bpp += self.count_bpp(path)
                compress_psnr += self.postprocess_image(path, ref)
                path2 = self.prepare_folder(dirn, name, False)
                if not layers:
                    time_decomp += kkd.decompress(path, path2, layers, ref, num_threads)
                    debug("decompress_kkd")
                    decompress_bpp += self.count_bpp(path2)
                    decompress_psnr += self.postprocess_image(path2, ref)
                    self.delete_image(path)
                    self.delete_image(path2)
                else:
                    time_decomp_layer_list, decompress_bpp_list, decompress_psnr_list = kkd.decompress(path, path2,
                                                                                                       layers, ref, num_threads)
                    debug(time_decomp_layer_list)
                    debug("\n")
                    debug(decompress_psnr_list)
                    debug("\n")
                    debug(decompress_bpp_list)
                    debug("\n")
                    self.delete_image(path)

                self.delete_dir(dirn)

        # Some mess  -- ignore----------------------------------------------------------------
        else:
            debug("File:" + input_file + " - ignored ")
            pass

    @staticmethod
    def parse_file(input_file):

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
    def delete_dir(dirn):

        try:
            os.rmdir(dirn + '/compressed')
        except IOError as e:
            print("Failed  to remove '{0}'\nError (code {1}): '{2}'.".format(dirn + '/compressed', e.errno, e.strerror))
            sys.exit()

        try:
            os.rmdir(dirn + '/decompressed')
        except IOError as e:
            print(
                "Failed  to remove '{0}'\nError (code {1}): '{2}'.".format(dirn + '/decompressed', e.errno, e.strerror))
            sys.exit()

    def delete_image(self, path):
        try:
            os.remove(path)
        except IOError as e:
            print(
                "Failed  to remove '{0}'\nError (code {1}): '{2}'.".format(path, e.errno, e.strerror))
            sys.exit()


if __name__ == "__main__":
    main()
