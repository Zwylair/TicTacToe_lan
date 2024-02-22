import os
import json
import random
import socket
from tabulate import tabulate


def cls():
    os.system('cls')


def check_for_winner(sign: str):
    for win_pose in win_positions:
        are_poses_true = []
        for cell in win_pose:
            are_poses_true.append(game_map[cell[1]][cell[0]] == sign)

        if False in are_poses_true:
            continue
        else:
            return True
    return False


def check_for_tie():
    unpacked_game_map = [item for sublist in game_map for item in sublist]
    return '-' not in unpacked_game_map


is_host = bool(int(input(
    '[0] -- Client\n'
    '[1] -- Host\n'
    '\n'
    '=> '
)))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn_to = ['0.0.0.0', 4444]
signs = ['X', 'O']
game_map = [
    ['-', '-', '-'],
    ['-', '-', '-'],
    ['-', '-', '-']
]
win_positions = (
    ((0, 0), (1, 0), (2, 0)),
    ((1, 0), (1, 1), (1, 2)),
    ((2, 1), (2, 1), (2, 2)),
    ((0, 0), (1, 0), (2, 0)),
    ((1, 0), (1, 1), (1, 2)),
    ((2, 0), (2, 1), (2, 2)),
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0))
)

if is_host:
    s.bind(tuple(conn_to))
    s.listen()

    print('Waiting for a connection...')
    conn, addr = s.accept()
    print('Connected.')
else:
    conn = None
    ip_to_connect = input('Enter IP to connect (empty for localhost): ')
    ip_to_connect = 'localhost' if not ip_to_connect else ip_to_connect
    conn_to[0] = ip_to_connect

    s.connect(tuple(conn_to))

current_turn = random.choice(('client turn', 'server turn'))
my_sign = random.choice(signs)
signs.remove(my_sign)
opponent_sign = signs[0]

while True:
    use_conn = conn if is_host else s

    # turn changing
    if is_host:
        current_turn = 'server turn' if current_turn == 'client turn' else 'client turn'
        conn.sendall(current_turn.encode())
    else:
        while True:
            current_turn = use_conn.recv(1024).decode()
            if not current_turn:
                print('Connection was aborted.')
                exit(0)
            else:
                break

    # sending / receiving game map
    if is_host:
        conn.sendall(json.dumps(game_map).encode())
    else:
        while True:
            game_map = json.loads(use_conn.recv(1024).decode())
            if not current_turn:
                print('Connection was aborted.')
                exit(0)
            else:
                break

    cls()
    print(
        f'Game map (your sign is {my_sign}):\n'
        '\n'
        f'{tabulate(game_map, tablefmt="rounded_grid")}\n'
        '\n'
    )

    if check_for_tie():
        input('Tie! (Press ENTER to exit)\n')
        exit(0)

    if check_for_winner(my_sign):
        input('You win! (Press ENTER to exit)\n')
        exit(0)

    if check_for_winner(opponent_sign):
        input('Opponent win! (Press ENTER to exit)\n')
        exit(0)

    data = None
    if (current_turn == 'server turn' and is_host) or (current_turn == 'client turn' and not is_host):
        while True:
            data = input('Your turn: ')
            x, y = [int(i) - 1 for i in data.split(';')]

            if game_map[y][x] != '-':
                print('You cannot place your sign here as this cell is already filled. Choose another one.\n')
            else:
                break

        game_map[y][x] = my_sign

        use_conn.sendall(data.encode())
    elif (current_turn == 'server turn' and not is_host) or (current_turn == 'client turn' and is_host):
        print("Waiting for opponent's turn...")

        while True:
            data = use_conn.recv(1024).decode()
            if not data:
                print('Connection was aborted.')
                exit(0)
            else:
                break

        x, y = [int(i) - 1 for i in data.split(';')]
        game_map[y][x] = opponent_sign
