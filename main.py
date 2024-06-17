import tkinter as tk
from tkinter import messagebox
import random
import copy

# 定数の定義
H = 5
W = 5
END_TURN = 4
INF = float("inf")
dx = (0, 0, -1, 1)
dy = (-1, 1, 0, 0)


class Character:
    def __init__(self, x: int, y: int, game_score: int) -> None:
        self.x = x
        self.y = y
        self.game_score = game_score


class NumberCollectGame:
    def __init__(
        self,
        player_turn: int = 0,
        p1_name: str = "Player_1",
        p2_name: str = "Player_2",
        seed: int = 0,
    ) -> None:
        random.seed(seed)
        self.turn = 0
        self.player_name = [p1_name, p2_name]

        # 初期位置をランダムに決定
        chara_1_x = random.randrange(H)
        chara_1_y = random.randrange(W // 2)
        chara_1 = Character(chara_1_x, chara_1_y, 0)
        chara_2 = Character(H - chara_1_x - 1, W - chara_1_y - 1, 0)
        self.characters = [chara_1, chara_2]

        # 盤面上の数字をランダムに決定
        self.points = [[0] * W for _ in range(H)]
        for i in range(H):
            for j in range(W):
                if i == self.characters[0].x and j == self.characters[0].y:
                    continue
                if i == self.characters[1].x and j == self.characters[1].y:
                    continue
                self.points[i][j] = random.randrange(10)

    def reset(self, player_turn, p1_name, p2_name, seed):
        self.__init__(
            player_turn=player_turn, p1_name=p1_name, p2_name=p2_name, seed=seed
        )

    def isDone(self) -> bool:
        return self.turn == END_TURN

    def isFirstPlayer(self) -> bool:
        return self.turn % 2 == 0

    def getFirstPlayerScoreForWinRate(self) -> int:
        winig_status = self.getWiningStatus()
        if winig_status == "WIN":
            if self.isFirstPlayer():
                return 1
            else:
                return 0
        elif winig_status == "LOSE":
            if self.isFirstPlayer():
                return 0
            else:
                return 1
        else:
            return 0.5

    # 1ターン進める。
    # charactersをswapすることで、常にcharacters[0]が注目するキャラクターとする。
    def advance(self, action: int) -> None:
        character = self.characters[0]
        character.x += dx[action]
        character.y += dy[action]
        point = self.points[character.x][character.y]
        if point > 0:
            character.game_score += point
            self.points[character.x][character.y] = 0
        self.turn += 1
        self.characters[0], self.characters[1] = self.characters[1], self.characters[0]
        self.player_name[0], self.player_name[1] = (
            self.player_name[1],
            self.player_name[0],
        )

    # 合法手を返す。
    def legalActions(self) -> list[int]:
        actions = []
        character = self.characters[0]
        for action in range(4):
            tx = character.x + dx[action]
            ty = character.y + dy[action]
            if 0 <= tx and tx < H and 0 <= ty and ty < W:
                actions.append(action)
        return actions

    # 勝敗状況を返す。
    def getWiningStatus(self) -> str:
        if self.isDone():
            if self.characters[0].game_score > self.characters[1].game_score:
                return "WIN"
            elif self.characters[0].game_score < self.characters[1].game_score:
                return "LOSE"
            else:
                return "DRAW"
        else:
            return ""

    # デバッグ用関数。ゲーム状況をCUIで返す。
    def __str__(self) -> str:
        points = [i[:] for i in self.points]
        result = []
        result.append(f"turn: {self.turn}")
        for p_id in range(2):
            actual_p_id = (p_id + self.turn) % 2
            character = self.characters[actual_p_id]
            result.append(f"player_name: {self.player_name[actual_p_id]}")
            result.append(f"score: {character.game_score}")
            result.append(f"x: {character.x}, y: {character.y}")
            if p_id == 0:
                points[character.x][character.y] = "A"
            else:
                points[character.x][character.y] = "B"
        result.append("points: ")
        for i in points:
            result.append(f"{' '.join([str(j) for j in i])}")
        result.append("")
        return "\n".join(result)

    # ランダムに行動を決定
    def randomAction(self) -> int:
        legal_actions = self.legalActions()
        return random.choice(legal_actions)

    # 盤面の評価を返す
    def getScore(self) -> int:
        return self.characters[0].game_score - self.characters[1].game_score

    def miniMaxScore(self, depth: int) -> int:
        if self.isDone() or depth == 0:
            return self.getScore()
        legal_actions = self.legalActions()
        # 今のところ不要
        # if len(legal_actions) == 0:
        #     return self.getScore()
        best_score = -INF
        for action in legal_actions:
            next_number_collect_game = copy.deepcopy(self)
            next_number_collect_game.advance(action)
            score = -next_number_collect_game.miniMaxScore(depth - 1)
            if score > best_score:
                best_score = score
        return best_score

    def miniMaxAction(self, depth: int) -> int:
        best_action = -1
        best_score = -INF
        legal_actions = self.legalActions()
        # print(self)
        for action in legal_actions:
            next_number_collect_game = copy.deepcopy(self)
            next_number_collect_game.advance(action)
            score = -next_number_collect_game.miniMaxScore(depth)
            # print(action, dx[action], dy[action], score)
            if score > best_score:
                best_score = score
                best_action = action
        return best_action

    # 状況を出力しながらゲームを進行する
    def playGame(self, ais: list[callable]) -> None:
        # print(self)
        while not self.isDone():
            # 1P
            # print("1p ---------------------")
            # action = self.miniMaxAction(END_TURN)
            action = ais[0]()
            # print(f"action: {action}")
            self.advance(action)
            # print(self)
            if self.isDone():
                winig_status = self.getWiningStatus()
                if winig_status == "WIN":
                    print(f"Winner: {self.player_name[0]}")
                    return f"Winner: {self.player_name[0]}"
                elif winig_status == "LOSE":
                    print(f"Winner: {self.player_name[1]}")
                    return f"Winner: {self.player_name[1]}"
                elif winig_status == "DRAW":
                    print("DRAW")
                    return "DRAW"
                break

            # 2P
            # print("2p ---------------------")
            # action = self.randomAction()
            action = ais[1]()
            # print(f"action: {action}")
            self.advance(action)
            # print(self)
            if self.isDone():
                winig_status = self.getWiningStatus()
                if winig_status == "WIN":
                    print(f"Winner: {self.player_name[0]}")
                    return f"Winner: {self.player_name[0]}"
                elif winig_status == "LOSE":
                    print(f"Winner: {self.player_name[1]}")
                    return f"Winner: {self.player_name[1]}"
                elif winig_status == "DRAW":
                    print("DRAW")
                    return "DRAW"
                break


def testFirstPlayerWinRate(game_num: int = 100):
    first_player_win_num = 0
    first_player_draw_num = 0
    first_player_lose_num = 0
    p1_name = "Player_1"
    p2_name = "Player_2"
    number_collect_game = NumberCollectGame(
        seed=0, p1_name="Player_1", p2_name="Player_2"
    )
    ais = [
        lambda: NumberCollectGame.miniMaxAction(number_collect_game, END_TURN),
        lambda: NumberCollectGame.randomAction(number_collect_game),
    ]
    for i in range(game_num):
        number_collect_game.reset(p1_name, p2_name, i)
        result = number_collect_game.playGame(ais)
        if result == f"Winner: {p1_name}":
            first_player_win_num += 1
        elif result == f"Winner: {p2_name}":
            first_player_lose_num += 1
        else:
            first_player_draw_num += 1

    print(first_player_win_num, first_player_lose_num, first_player_draw_num)
    for i in range(game_num):
        number_collect_game.reset(p1_name, p2_name, i)
        result = number_collect_game.playGame(ais[::-1])
        if result == f"Winner: {p1_name}":
            first_player_lose_num += 1
        elif result == f"Winner: {p2_name}":
            first_player_win_num += 1
        else:
            first_player_draw_num += 1
    print(
        f"win: {first_player_win_num}, lose: {first_player_lose_num}, draw: {first_player_draw_num}"
    )
    print(f"win_rate: {first_player_win_num / (game_num * 2)}")


# testFirstPlayerWinRate(100)
# number_collect_game.playGame()


class NumberCollectGameGUI:
    def __init__(self):
        seed = random.randrange(100000)
        self.player_turn = random.randrange(2)
        self.game = NumberCollectGame(player_turn=self.player_turn, seed=seed)

        self.root = tk.Tk()
        self.root.title("Number Collect Game")
        self.root.geometry("900x900")
        self.initialize_turn_frame()
        self.initialize_score_frame()
        self.initialize_board_frame()
        self.root.mainloop()

    def initialize_turn_frame(self):
        """ターン表示フレームを初期化する"""
        self.turn_frame = tk.Frame(self.root)
        remaining_turns_text = f"残りのターン: {END_TURN}"
        turn_text = "プレイヤーのターン" if self.player_turn == 0 else "NPCのターン"

        self.remaining_turns_label = tk.Label(
            self.turn_frame, text=remaining_turns_text, font=("Helvetica", 14)
        )
        self.turn_label = tk.Label(
            self.turn_frame, text=turn_text, font=("Helvetica", 14)
        )
        self.remaining_turns_label.pack()
        self.turn_label.pack()
        self.turn_frame.pack()

    def initialize_score_frame(self):
        """スコア表示フレームを初期化する"""
        self.score_frame = tk.Frame(self.root)
        self.player_score_label = tk.Label(
            self.score_frame,
            text="プレイヤーのスコア\n0",
            bg="#FFCCCC",
            font=("Helvetica", 14),
            width=25,
        )
        self.npc_score_label = tk.Label(
            self.score_frame,
            text="NPCのスコア\n0",
            bg="#CCDDFF",
            font=("Helvetica", 14),
            width=25,
        )
        self.player_score_label.pack(side=tk.LEFT, padx=10, pady=10)
        self.npc_score_label.pack(side=tk.RIGHT, padx=10, pady=10)
        self.score_frame.pack(pady=10)

    def initialize_board_frame(self):
        """ボード表示フレームを初期化する"""
        self.board_frame = tk.Frame(self.root)
        self.board_buttons = [[None] * W for _ in range(H)]
        for i in range(H):
            for j in range(W):
                button = tk.Button(
                    self.board_frame,
                    text=self.game.points[i][j],
                    height=4,
                    width=8,
                    font=("Helvetica", 18),
                )
                button.config(command=lambda i=i, j=j: self.on_player_click(i, j))
                button.grid(row=i, column=j)
                self.board_buttons[i][j] = button

        self.board_frame.pack(pady=10)

    def on_player_click(self, row, col):
        """プレイヤーがボードをクリックした時の処理"""
        # self.clicked = (row, col)
        # self.change_button_states(tk.DISABLED)
        pass

    # def change_button_states(self, state):
    #     """ボード上のすべてのボタンの状態を変更する"""
    #     for i in range(3):
    #         for j in range(3):
    #             if self.game.board_state[i * 3 + j] == -1:
    #                 self.board_buttons[i][j].config(state=state)


game_GUI = NumberCollectGameGUI()
