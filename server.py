import re
import datetime
import socket


sock = socket.socket()
sock.bind(('localhost', 3631))
sock.listen(1)
conn, addr = sock.accept()

print('connected:', addr)


def generate_period(time_param):
    if len(time_param) == 3:
        seq = (time_param[0], time_param[1], '59')
        return [':'.join(time_param), ':'.join(seq)]
    elif len(time_param) == 2:
        seq1 = (time_param[0], time_param[1], '00')
        seq2 = (time_param[0], time_param[1], '59')
        return [':'.join(seq1), ':'.join(seq2)]
    elif len(time_param) == 1:
        seq1 = (time_param[0], '00', '00')
        seq2 = (time_param[0], '59', '59')
        return [':'.join(seq1), ':'.join(seq2)]


def get_match_from_log(time_param, string_param):
    time_period = generate_period(time_param)

    with open('otrs_error.log', 'r') as f:
        match_qnty = 0
        match_collection = ''

        for line in f:
            brackets_indexes_in_line = []
            for m in re.finditer('\[.*?\]', line):
                brackets_indexes_in_line.append([m.start(), m.end()])
            try:
                data_start = brackets_indexes_in_line[0][0]
                data_end = brackets_indexes_in_line[0][1]

                log_time_str = line[data_start:data_end][12:20]
                log_time = datetime.datetime.strptime(log_time_str, '%H:%M:%S')

            except ValueError:
                # print('Отрезок не содержит дату - %s' % log_time_str)
                pass
            except IndexError:
                pass
            finally:
                log_time_from = datetime.datetime.strptime(time_period[0], '%H:%M:%S')
                log_time_till = datetime.datetime.strptime(time_period[1], '%H:%M:%S')

                if log_time_from <= log_time <= log_time_till:
                    if line.upper().find(string_param.upper()) is not -1:
                        match_qnty += 1
                        match_collection += '%s' % line

    return [match_qnty, match_collection]


while True:
    data = conn.recv(1024)
    if not data:
        break
    rcvd_data = data.decode().split('-')
    time_part = rcvd_data[0].split(':')
    string_part = rcvd_data[1]
    result = get_match_from_log(time_part, string_part)
    send_data = 'Найдено {} совпадений: \n{}'.format(result[0], result[1])
    conn.send(send_data.encode("utf-8"))

conn.close()