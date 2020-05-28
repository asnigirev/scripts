#!/usr/bin/python3
# Copyright (C) 2019 All rights reserved.
# Author Artem Snigirev <takeitawaytu@gmail.com>.

# -*- coding: utf-8 -*-

import sys
import os
import json
import requests
import csv
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from dateutil import tz
import pytz
import getpass

print('Copyright (C) 2019 All rights reserved.\nAuthor Artem Snigirev <takeitawaytu@gmail.com>.\n\n\n\n\n')
print('Be careful, old files will be ERASED!!!\n\n')

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
local_tz = pytz.timezone('UTC')

verify = 'False'
output = 'result.csv'
html_output = 'face_report.html'
verbose = None
check = True

while check:
    url = 'http://' + input('Please, enter server ip-address: ') + '/'
    user = input('Login: ')

    print('Don’t worry, the password will be typed, it’s just hidden')

    passw = getpass.getpass()

    print('Wait')

    try:
        resp = requests.post(url+'n7/n7session', auth=HTTPBasicAuth(user, passw))
        result = resp.text
        global n7token
        n7token = result
        if resp.status_code != 200:
            print("\nInvalid credentials\n Try again...\n")
            check = True
        else:
            check = False
#            break
    except Exception:
            print("\nInvalid server address\n Try again...\n")

while True:
    try:
        since_date = input('Please, enter start date (Ex. YYYY-MM-DD): ')
        since_time = input('Please, enter start time (Ex. hh:mm:ss):   ')
        since = str(since_date + 'T' + since_time + '.000')

        until_date = input('Please, enter end date (Ex. YYYY-MM-DD):   ')
        until_time = input('Please, enter end time (Ex. hh:mm:ss):     ')
        until = str(until_date + 'T' + until_time + '.000')

        since_timestamp = datetime.strptime(since, DATETIME_FORMAT).replace(tzinfo=tz.tzlocal())
        until_timestamp = datetime.strptime(until, DATETIME_FORMAT).replace(tzinfo=tz.tzlocal())
    except ValueError:
        print("\nDate or Time is not correct\n Try again...\n")
    else:
        break


def erase_files(output, html_output):
    html_header = ''
    if output is not None:
        with open(output, 'w', newline='') as out:
            writer = csv_writer(out)
            writer.writerow([
                '{}'.format('first_name'),
                '{}'.format('last_name'),
                '{}'.format('face_id'),
                '{}'.format('list_id'),
                '{}'.format('similar'),
                '{}'.format('channel_id'),
                '{}'.format('date'),
                '{}'.format('image_link'),
                '{}'.format('eth_img_link')
            ])
            out.close()
    if html_output is not None:
        with open(html_output, 'w', newline='') as out:
            out.write(html_header)
            out.close()
    newpath = r'.\snapshots'
    if not os.path.exists(newpath):
        os.makedirs(newpath)


def csv_writer(out):
    return csv.writer(out)


def get_photo(N, r, headers):
    img_url = r['snapshots'][2]['path']

    global html
    html = url + img_url[1:]
    path_to_snapshot = 'snapshots/img(' + str(N) + ').jpg'

    global image_link
    image_link = path_to_snapshot

    img = requests.get(html, headers=headers)
    with open(path_to_snapshot, 'wb') as img_file:
        img_file.write(img.content)
    image_link = path_to_snapshot
    print('snapshot: img(' + str(N) + ').jpg - has been downloaded')


def get_ethanol(N, headers, r, face_id, html):
    if r['params']['identity']['state'] == 'IDENTIFIED':
        path_to_eth = url+'n7/faces/'+str(face_id)
        eth_img_url = requests.get(path_to_eth, headers=headers)
        result = eth_img_url.text
        res = json.loads(result)
        res = res['images'][0]['image']
        path_to_eth_snapshot = 'snapshots/img(' + str(N) + ')ethalon.jpg'
        eth_img = requests.get(url+res[1:], headers=headers)

        with open(path_to_eth_snapshot, 'wb') as eth_img_f:
            eth_img_f.write(eth_img.content)

    elif r['params']['identity']['state'] == 'NOT_IDENTIFIED':
        path_to_eth = r['snapshots'][0]['path']
        path_to_eth = url + path_to_eth[1:]
        path_to_eth_snapshot = 'snapshots/img(' + str(N) + ')ethalon.jpg'
        eth_img = requests.get(path_to_eth, headers=headers)

        with open(path_to_eth_snapshot, 'wb') as eth_img_f:
            eth_img_f.write(eth_img.content)

    global eth_img_link
    eth_img_link = path_to_eth_snapshot
    print('snapshot: eth(' + str(N) + ').jpg - has been downloaded')


def print_result(first_name, last_name, face_id, list_id, similar, channel_id, date, image_link, eth_img_link):
    with open(output, 'a', newline='') as out:
        writer = csv_writer(out)
        writer.writerow([
            '{}'.format(first_name),
            '{}'.format(last_name),
            '{}'.format(face_id),
            '{}'.format(list_id),
            '{}'.format(similar),
            '{}'.format(channel_id),
            '{}'.format(date),
            '{}'.format(image_link),
            '{}'.format(eth_img_link)
        ])


def build_html_headers(html_output):
    html_headers = (
        '<html>\n'
        '   <head>\n'
        '       <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n'
        '   </head>\n'
        '   <body>\n'
        '       <table border="1">\n'
        '           <tbody>\n'
        '               <tr>\n'
        '                   <th>N</th>\n'
        '                   <th>First_Name</th>\n'
        '                   <th>Last_Name</th>\n'
        '                   <th>Face_id</th>\n'
        '                   <th>Facelist_id</th>\n'
        '                   <th>Similarity</th>\n'
        '                   <th>Channel_id</th>\n'
        '                   <th>Time_stamp</th>\n'
        '                   <th>Thumbnail</th>\n'
        '                   <th>Person_photo</th>\n'
        '               </tr>\n'
    )
    with open(html_output, 'a', newline='') as out:
        out.write(html_headers)
        out.close()


def build_html_end(html_output):
    html_end = (
            '           </tbody>\n'
            '       </table>\n'
            '   </body>\n'
            '</html>\n'
            )
    with open(html_output, 'a', newline='') as out:
        out.write(html_end)
        out.close()


def build_html_body(N, first_name, last_name, face_id, list_id, similar, channel_id, date, path_to_snapshot, path_to_eth_snapshot, html_output):
    html_str = (
            '               <tr align="middle">\n'
            '                   <td>' + str(N) + '</td>\n'
            '                   <td>' + str(first_name) + '</td>\n'
            '                   <td>' + str(last_name) + '</td>\n'
            '                   <td>' + str(face_id) + '</td>\n'
            '                   <td>' + str(list_id) + '</td>\n'
            '                   <td>' + str(similar) + '</td>\n'
            '                   <td>' + str(channel_id) + '</td>\n'
            '                   <td>' + str(date) + '</td>\n'
            '                   <td>\n'
            '                       <img style="width: 150px;" src="./' + str(path_to_snapshot) + '">\n'
            '                   </td>\n'
            '                   <td>\n'
            '                       <img style="width: 150px;" src="./' + str(path_to_eth_snapshot) + '">\n'
            '                   </td>\n'
            '               </tr>\n'
    )
    with open(html_output, 'a', newline='', encoding='utf-8') as out:
        out.write(html_str)
        out.close()


def get_faces(*args):
    check = True
    offset = 0
    N = 0
    while check is True:
        N = N
        headers = {
            'Authorization': 'N7Session '+n7token
            }
        params = {
            "limit": "240",
            "offset": offset,
            "order_type": "asc",
            "since": since_timestamp,
            "since_by_start_time": "true",
            "topics": "FaceDetected",
            "until": until_timestamp
        }
        resp = requests.get(
            url+'/n7/events',
            headers=headers,
            params=params
            )
        result = resp.text
        resp = json.loads(result)
        cond = len(resp)
        for index, r in enumerate(resp):
            if r['params']['identity']['state'] == 'IDENTIFIED':
                resp = r['params']['identity']['persons'][0]
                first_name = resp['face']['first_name']
                last_name = resp['face']['last_name']
                face_id = resp['face']['id']
                list_id = resp['list']['id']
                similar = r['params']['identity']['persons'][0]['similarity']
                channel_id = r['channel']

                unc_date = r['start_time'].replace('Z', '')
                unc_date = datetime.strptime(unc_date, DATETIME_FORMAT)
                upd_date = local_tz.localize(unc_date)
                date = datetime.strftime(upd_date.astimezone(pytz.timezone('Europe/Moscow')), DATETIME_FORMAT)
                try:
                    get_photo(N, r, headers)
                    get_ethanol(N, headers, r, face_id, html)
                except IndexError:
                    continue
            elif r['params']['identity']['state'] == 'NOT_IDENTIFIED':
                first_name = 'Not'
                last_name = 'Identified'
                face_id = '-'
                list_id = '-'
                similar = '-'
                channel_id = r['channel']

                unc_date = r['start_time'].replace('Z', '')
                unc_date = datetime.strptime(unc_date, DATETIME_FORMAT)
                upd_date = local_tz.localize(unc_date)
                date = datetime.strftime(upd_date.astimezone(pytz.timezone('Europe/Moscow')), DATETIME_FORMAT)
                try:
                    get_photo(N, r, headers)
                    get_ethanol(N, headers, r, face_id, html)
                except IndexError:
                    continue
            build_html_body(N, first_name, last_name, face_id, list_id, similar, channel_id, date, image_link, eth_img_link, html_output)
            print(first_name, ' ', last_name, ', face id: ', face_id, ', facelist id: ', list_id, ', eventdate: ', date)
            print_result(first_name, last_name, face_id, list_id, similar, channel_id, date, image_link, eth_img_link)
            N += 1
        offset += 240
        if cond == 0:
            check = False


# Основная функция
if __name__ == '__main__':
    erase_files(output, html_output)
    build_html_headers(html_output)
    get_faces()
    build_html_end(html_output)
    input('Done, press "enter"')

