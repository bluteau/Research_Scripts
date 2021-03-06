#!/usr/bin/env python
'''
@name: plot_trans.py
@author: MMB
@date: 2014-04-30
@version: 1.1
@description: A python script for plotting the (effective) collision strengths
    for transitions from different calculations on the same graph. All data
    relevant files will be plotted for a specified transition and multiple
    transitions can be specified. The file names must be formatted exactly as
    those produced from the xtrct_trans.py module.
'''

import numpy as np
import matplotlib.pyplot as plt
import sys
import math
#import subprocess as sp
#import os
import datetime as dt
import glob
import argparse as ap
import re


def main(argv):
    '''Main function for module plot_trans '''

    prog_des = "A python script for plotting the (effective) collision "\
    "strengths for transitions from different calculations on the same graph."\
    " All data relevant files will be plotted for a specified transition and"\
    " multiple transitions can be specified. The file names must be formatted"\
    " exactly as those produced from the xtrct_trans.py module."
    parser = ap.ArgumentParser(prog='plot_trans.py', description=prog_des)
    parser.add_argument('trans', nargs='+', help='the list list of transitions'
                        ' specified by pairs of numbers, lower level then '
                        'upper level')
    parser.add_argument('-b', action='store_true', default=False, help='flag'
                        ' to plot Burgess-Tully scaled data present in the '
                        'current directory instead of the normal data. Files '
                        'with .burg extensions must contain this data.')
    parser.add_argument('-t', nargs=1, default='om', choices=('om', 'ups'),
                        help='use to specify the quantity to be plotted: omega'
                        '("om") or upsilon("ups"). Must be one of these two '
                        'strings. Default is "om" (i.e. plot any omega'
                        ' transitions in current directory) if option not'
                        ' present')
    parser.add_argument('-o', '--outfile', nargs=1, type=str,
                        default=False, help='flag to save output to file and '
                        'argument is used as description of output file '
                        '(mandatory)')
    parser.add_argument('-l', '--location', nargs=1, type=str,
                        default='upper left', help='argument specifies the '
                        'location for the legend in the generated graph. The '
                        'default is "upper left"')
    parser.add_argument('--logx', action='store_true', default=False,
                        help='flag to turn on log scaling of the x-axis')
    parser.add_argument('--logy', action='store_true', default=False,
                        help='flag to turn on log scaling of the y-axis')
    parser.add_argument('-c', '--conv', nargs='?', type=float, default=False,
                        const=2.205, help='flag to switch on convolution of the'
                        ' input data with a normalized Gaussian. The optional '
                        'argument specifies the scaling parameter (Ryd) in the deno-'
                        'minator of the exponent (default 2.205 Ryd).')
    parser.add_argument('-x', '--xsec', nargs='?', type=int, default=False,
                        const=1, help='flag to switch on conversion of omega'
                        ' values to cross-sections. The optional argument '
                        'specifies the statistical weight of the initial level '
                        '(default 1). This statistical weight will be used for'
                        ' all transitions, so operation is probably limited to '
                        'plotting one transition.')

    args = parser.parse_args(argv)
    #print(args)

    # Level nomenclature dict; should make this a bit more portable at some
    # point
    lev = {'1':'3d^{10}\!4s^2 \ ^1\!S_0', '275':\
            '3d^{9}\!4s^2\!4f \ \ ^3\!D_1^{\circ}', '290':\
            '3d^{9}\!4s^2\!4f \ \ ^1\!P_1^{\circ}', '295':\
            '3d^{9}\!4s^2\!4f \ \ ^3\!P_1^{\circ}', '2':\
            '3d^{10}\!4s\!4p \ \ ^3\!P_0^{\circ}', '3':'3d^{10}\!4s\!4p \ \ '\
            '^3\!P_1^{\circ} / \ ^1\!P_1^{\circ}', '24':'3d^{10}\!4s\!4d \ \ '\
            '^3\!P_0^{\circ}', '6':'3d^{10}\!4s\!4p \ \ ^1\!P_1^{\circ} / \ '\
            '^3\!P_1^{\circ}', '5':'3d^{10}\!4s^2 \ \ ^3\!P_0',\
            '8':'3d^{10}\!4p^2 \ \ ^1\!D_2'}

    # Physical Constants
    a_0 = 0.52917721092e-8 #Bohr radius in cm
    pia2 = math.pi * a_0**2 # pi * a_0^2

    LOGY = args.logy
    LOGX = args.logx
    typ = args.t[0]
    if args.outfile == False:
        save = False
    else:
        save = True
        outfile = args.outfile[0]
    x = args.trans
    if len(x) % 2 is not 0:
        raise Exception("You have given an odd number of levels."
                        " This needs to be even silly.")
    trans = [x[(2 * i): (2 * i + 2)] for i in range(int(len(x) / 2))]
    #print(trans)
    fname = []
    sty = ['-', '--', '-.', ':', '_', '.', '-x', '-*']
    clr = ['b', 'r', 'g', 'k', 'y']
    for i in trans:
        try:
            [int(a) for a in i]
        except ValueError as err:
            # TO-DO: implement a float conversion here
            print("You must enter integers for levels.")
            print("You entered: ", err.args)
            raise
        if args.b:
            if typ == 'ups':
                files = glob.glob('ups-' + i[0] + '_' + i[1] + '-*' + '.burg')
            else:
                files = glob.glob('om-' + i[0] + '_' + i[1] + '-*' + '.burg')
        else:
            if typ == 'ups':
                files = glob.glob('ups-' + i[0] + '_' + i[1] + '-*' + '.trns')
            else:
                files = glob.glob('om-' + i[0] + '_' + i[1] + '-*' + '.trns')
        files.sort()
        print('Processing transition ', i)
        print('Files:')
        print(files)
        fig, ax = plt.subplots(1)
        legend = []
        title = 'Transition ' + i[0] + '-' + i[1] + ', $' + lev[i[0]]\
                + '\\rightarrow' + lev[i[1]] + '$'
        if save:
            if typ == 'ups':
                fname.append('ups-' + i[0] + '_' + i[1] + '-' + outfile + '-'\
                             + dt.date.today().isoformat().replace('-', '_') +\
                             '.pdf')
            else:
                fname.append('om-' + i[0] + '_' + i[1] + '-' + outfile + '-'\
                             + dt.date.today().isoformat().replace('-', '_') +\
                             '.pdf')
        if LOGX:
            maxx = 0
            minx = 1e20
        if LOGY:
            maxy = 0
            miny = 1e20
        count = 1
        for j in reversed(files):
            desc = j.split('-')[2]
            legend.append(desc)
            # Load the input files and plot the appropriate columns
            data = np.loadtxt(j)
            # TO-DO: need to check the column assignments below
            #print('args.b= ', args.b)
            #print(data[0:-1, 1])
            if args.b:
                if desc == 'AS_DW':
                    x1 = data[:, 2]
                    y1 = data[:, 3]
                else:
                    x1 = data[:, 0]
                    y1 = data[:, 1]
            else:
                if desc == 'AS_DW':
                    x1 = data[0:-1, 0]
                    y1 = data[0:-1, 1]
                    if typ == 'om':
                        with open(j, 'r') as file:
                            head = file.readline()
                        a = float(re.sub(r'[^\d.]+', '', head.split('=')[1]))
                        x1 = x1 + a
                else:
                    x1 = data[0:-1, 1]
                    y1 = data[0:-1, 3]
            if LOGX:
                maxx = max(maxx, np.max(x1))
                minx = min(minx, np.min(x1))
            if LOGY:
                maxy = max(maxy, np.max(y1))
                miny = min(miny, np.min(y1))
            ## Create the desired uncertainty region
            #err = 0.1 * y2
            #
            if args.xsec != False: # convert the collision strengths to x-secs
                y1 = pia2 * y1 / (args.xsec * x1)
            if args.conv != False:
                # for convolution, omega values should start at E=0, so the 
                # below pads the loaded data with zeros
                incr = x1[2] - x1[1]
                # FWHM = 2 * math.sqrt(2*math.log(2)) * stdev
                sdev = args.conv / 2.3548200450309493 
                num = math.floor(x1[1] / incr)
                xadd = np.linspace(0, x1[1], num, endpoint=False)
                pad = np.zeros(num)
                xc1 = np.append(xadd, x1[1:])
                yc = np.append(pad, y1[1:])
                numc = 6 * math.floor(sdev / incr) + 1
                xc2 = np.linspace(-3 * sdev, 3 * sdev, numc)
                g = np.exp(-1 * xc2**2 / (2 * sdev**2))
                g = g / g.sum()
                #ax.plot(x1, g, clr[count - 1] + sty[count - 1])
                c = np.convolve(yc, g, mode='same')
                ax.plot(xc1, c, clr[count - 1] + sty[count - 1])
                out = np.column_stack((xc1, c))
                np.savetxt(typ + '-' + i[0] + '_' + i[1] + '-' + 'CONV' + '_' 
                        + desc, out) 
            elif typ == 'om':
                ax.plot(x1, y1, clr[count - 1] + sty[count - 1], alpha=0.3)
            else:
                ax.plot(x1, y1, clr[count - 1] + sty[count - 1])
            if count % 5 == 0:
                count = 1
            else:
                count += 1
            #ax.fill_between(x2, y2 - err, y2 + err, alpha=0.2, edgecolor='red', 
            #        facecolor='red')
        if LOGX:
            ax.set_xscale('log')
            xmax = maxx + 10 ** math.floor(math.log10(maxx))
            xmin = minx - 10 ** math.floor(math.log10(minx))
            ax.set_xlim([xmin, xmax])
        if LOGY:
            ax.set_yscale('log')
            #print(maxy, miny)
            ymax = maxy + 10 ** math.floor(math.log10(maxy))
            if round(miny) == 0:
                ymin = 0
            else:
                ymin = miny - 10 ** math.floor(math.log10(miny))
            ax.set_ylim([ymin, ymax])
        if typ == 'ups':
            if args.b:
                ax.set_ylabel("$\\Upsilon_r$, Reduced Effective Collision "\
                              "Strength")
                ax.set_xlabel("$T_r$, Reduced Temperature")
            else:
                ax.set_ylabel("$\\Upsilon$, Effective Collision Strength")
                ax.set_xlabel("$T \ (\mathrm{K})$")
        else:
            if args.b:
                ax.set_ylabel("$\Omega_r$, Reduced Collision "\
                              "Strength")
                ax.set_xlabel("$E_r$, Reduced Scattering Energy")
            else:
                if args.xsec != False:
                    ax.set_ylabel("$\sigma$, Cross Section")
                else:
                    ax.set_ylabel("$\Omega$, Collision Strength")
                ax.set_xlabel("$E$, Scattering Energy (Ryd)")
        ax.set_title(title)
        ax.legend(legend, loc=args.location, prop={'size':10})
        fig.set_size_inches(11.89, 8.27)
    if save:
        for i in plt.get_fignums():
            plt.figure(i)
            plt.savefig(fname[i - 1])
    else:
        plt.show()


if __name__ == '__main__':
    main(sys.argv[1:])
